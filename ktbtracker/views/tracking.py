import json
import logging
from collections import OrderedDict, defaultdict
from datetime import date, timedelta, datetime
from itertools import cycle
from typing import Any
from zoneinfo import ZoneInfo

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView, ListView, UpdateView, TemplateView
from django_htmx.http import HttpResponseClientRefresh, trigger_client_event

from config.requirements import Requirements
from ktbtracker import debug
from ktbtracker.forms import TrackingForm
from ktbtracker.models import Candidate, Cycle, CycleWeek, Tracking, TrackingFullStatistics, TrackingStatistics

logger = logging.getLogger(__name__)

#TRACKING_NAMES = OrderedDict({e.key: e.title for e in Requirements})


@debug
def calculate_tracking_totals(candidate: Candidate, cycle_week: CycleWeek | None = None) -> dict[str, float]:
    tracking_totals = {}
    candidate_tracking = Tracking.objects.filter(
        candidate=candidate,
        tracking_date_range=(cycle_week.start if cycle_week else candidate.cycle.cycle_start, cycle_week.end if cycle_week else candidate.cycle.cycle_end)
    ).values_list()

    for name in Requirements.TRACKING_NAMES().keys():
        tracking_totals[name] = sum([t.get(name, 0) for t in candidate_tracking])

    return tracking_totals


@debug
def calculate_statistics(candidate: Candidate, cycle_week: CycleWeek | None = None):
    tracking_statistics = {}
    tracking_totals = calculate_tracking_totals(candidate, cycle_week)


@debug
def calculate_full_statistics(candidate: Candidate):
    full_statistics = {}
    full_tracking = Tracking.objects.filter(
        candidate=candidate,
        tracking_date__range=(candidate.cycle.cycle_start, candidate.cycle.cycle_end + timedelta(days=1))
    ).values_list()
    for name in Requirements.TRACKING_NAMES().keys():
        full_statistics[name] = [t.get(name, 0) for t in full_tracking]


class TrackingBaseView(LoginRequiredMixin, View):

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        #
        # Determine the current cycle from the session if available, otherwise use the latest cycle or administrator selected...
        #
        if cycle_id := request.session.get("_cycle", 0):
            self.cycle = Cycle.objects.get(id=int(cycle_id))
        else:
            self.cycle = Cycle.objects.all().order_by("-id").first()
            request.session.update({"_cycle": self.cycle.id})

        if request.user.is_staff and request.GET.get("cycle") and request.GET.get("cycle").isdigit():
            if self.cycle.id != int(request.GET.get("cycle", 0)):
                self.cycle = Cycle.objects.get(id=int(request.GET.get("cycle", 0)))
                request.session.update({"_cycle": self.cycle.id})

        logger.debug(f"...setup {cycle_id=} {self.cycle=}")

        #
        # Determine the current candidate from the session if available, otherwise from the logged-in user or administrator selected...
        #
        if candidate_id := request.session.get("_candidate", 0):
            try:
                self.candidate = Candidate.objects.select_related("cycle", "user").get(id=int(candidate_id))
            except Candidate.DoesNotExist:
                self.candidate = None
                request.session.delete("_candidate")
        else:
            try:
                self.candidate = Candidate.objects.select_related("cycle", "user").filter(user__id=request.user.id).order_by("-id").first()
                request.session.update({"_candidate": self.candidate.id})
            except Candidate.DoesNotExist:
                self.candidate = Candidate(cycle=self.cycle)
                request.session.delete("_candidate")

        if request.user.is_staff and request.GET.get("canid") and request.GET.get("canid").isdigit():
            if self.candidate.id != int(request.GET.get("canid", 0)):
                try:
                    self.candidate = Candidate.objects.select_related("cycle", "user").get(id=int(request.GET.get("canid", 0)))
                    request.session.update({"_candidate": self.candidate.id})
                except Candidate.DoesNotExist:
                    self.candidate = Candidate(cycle=self.cycle)
                    request.session.delete("_candidate")

        if self.candidate.cycle.id != self.cycle.id:
            logger.warning(f"The current candidate ({self.candidate.id or 0}) is not part of the current cycle.")
            self.candidate = Candidate(cycle=self.cycle)
            request.session.delete("_candidate")

        logger.debug(f"...setup {candidate_id=} {self.candidate=}")

        if tracking_date := request.session.get("_tracking_date", None):
            if self.request.GET.get("trackingDate"):
                try:
                    self.tracking_date = datetime.fromisoformat(self.request.GET.get("trackingDate")).date()
                    request.session.update({"_tracking_date": tracking_date})
                except ValueError:
                    self.tracking_date = datetime.now(ZoneInfo("America/New_York")).date()
                    request.session.update({"_tracking_date": self.tracking_date.isoformat()})
                # return datetime.strptime(self.request.GET.get("trackingDate"), "%Y-%m-%d").date()
            else:
                self.tracking_date = datetime.now(ZoneInfo("America/New_York")).date()
                request.session.update({"_tracking_date": self.tracking_date.isoformat()})
        else:
            self.tracking_date = datetime.now(ZoneInfo("America/New_York")).date()
            request.session.update({"_tracking_date": self.tracking_date.isoformat()})

        logger.debug(f"...setup {tracking_date=} {self.tracking_date=}")

        if week_idx := request.session.get("_week", 0):
            if self.request.GET.get("week") and request.GET.get("week").isdigit():
                try:
                    q_week = int(self.request.GET.get("week"))
                    self.tracking_week = self.cycle.cycle_week(q_week if q_week <= 0 else q_week - 1)
                    request.session.update({"_week": week_idx})
                except ValueError:
                    self.tracking_week = self.cycle.cycle_week_of(self._tracking_date or date.today())
                    request.session.update({"_week": self.tracking_week.week})
            else:
                self.tracking_week = self.cycle.cycle_week_of(self.tracking_date or date.today())
                request.session.update({"_week": self.tracking_week.week})
        else:
            self.tracking_week = self.cycle.cycle_week_of(self.tracking_date or date.today())
            request.session.update({"_week": self.tracking_week.week})
        logger.debug(f"...setup {week_idx=} {self.tracking_week=}")


class TrackingIndexView(TrackingBaseView, TemplateView):
    template_name = "tracking/index.html"


class TrackingHeaderView(TrackingBaseView, TemplateView):
    template_name = "tracking/partials/tracking_header.html"

    @debug
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

    @debug
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            cycle=self.cycle,
            candidate=self.candidate,
            tracking_week=self.tracking_week,
        )

        return context


class TrackingListView(TrackingBaseView, ListView):
    template_name = "tracking/partials/tracking_list.html"
    model = Tracking

    @debug
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @debug
    def get_queryset(self) -> QuerySet:
        return Tracking.objects.select_related("candidate").filter(
            candidate=self.candidate,
            tracking_date__range=(self.tracking_week.start, self.tracking_week.end),
        ).order_by("tracking_date").all()

    @debug
    def get_context_data(self, **kwargs):
        tracking_data = defaultdict(list)
        tracking_statistics = TrackingStatistics(self.candidate, self.tracking_week)
        cycle_statistics = TrackingStatistics(self.candidate, None)
        cycle_candidates = Candidate.objects.select_related("cycle", "user").filter(cycle=self.cycle).order_by("user__last_name", "user__first_name").all()

        # Transpose rows and columns...
        for tracking in self.object_list.values('tracking_date', *[k for k, v in Requirements.TRACKING_NAMES().items() if getattr(self.cycle, k, None)]):
            for k, v in tracking.items():
                tracking_data[k].append(v)

        # Fill-in any missing tracking records for the week with 0s...
        for tdate_idx, tdate in [(idx, t) for idx, t in enumerate(self.tracking_week.dates) if t not in tracking_data.get("tracking_date", [])]:
            logger.info(f"{tdate_idx} {tdate} not in data!")
            for k in ["tracking_date"] + [k for k, v in Requirements.TRACKING_NAMES().items() if getattr(self.cycle, k, None)]:
                tracking_data[k].insert(tdate_idx, tdate if k == "tracking_date" else 0)

        context = super().get_context_data(**kwargs)
        context.update(
            TRACKING_NAMES={k: v for k, v in Requirements.TRACKING_NAMES().items() if getattr(self.cycle, k, None)},
            cycle=self.cycle,
            candidate=self.candidate,
            tracking_week=self.tracking_week,
            tracking_data=tracking_data,
            tracking_stats=tracking_statistics.statistics,
            tracking_totals=tracking_statistics.totals,
            cycle_stats=cycle_statistics.statistics,
            cycle_totals=cycle_statistics.totals,
            cycle_candidates=cycle_candidates,
            today=datetime.now(ZoneInfo("America/New_York")).date(),
        )

        return context

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        return trigger_client_event(response, "trackingListUpdated")


class TrackingEditView(TrackingBaseView, UpdateView):
    template_name = "tracking/partials/tracking_form.html"
    form_class = TrackingForm
    model = Tracking

    @debug
    def get_object(self, queryset: QuerySet | None = None ) -> Tracking:
        try:
            tracking = Tracking.objects.select_related("candidate").get(candidate=self.candidate, tracking_date=self.kwargs.get("tracking_date"))
        except Tracking.DoesNotExist:
            tracking = Tracking(candidate=self.candidate, tracking_date=self.kwargs.get("tracking_date"))

        return tracking

    @debug
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "candidate": self.candidate
        })

        return kwargs

    @debug
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            TRACKING_NAMES=Requirements.TRACKING_NAMES(),
            cycle = self.cycle,
            candidate=self.candidate,
            cycle_day=self.cycle.cycle_day(self.kwargs.get("tracking_date")),
            tracking=self.get_initial(),
        )

        return context

    def get_success_url(self):
        return reverse_lazy("tracking-index")

    @debug
    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            response = HttpResponse()  # HttpResponseClientRefresh()
            trigger_client_event(response, "trackingListChanged")
            return trigger_client_event(response, "closeEditor")

        return super().form_valid(form)

    @debug
    def form_invalid(self, form):
        logger.debug(f"form invalid: {form.errors=}")
        response = super().form_invalid(form)


class TrackingFormView(TrackingBaseView, FormView):
    template_name = "tracking/editor.html"
    form_class = TrackingForm

    @debug
    def get_initial(self):
        tracking_date: date = self.kwargs.get("tracking_date")
        try:
            tracking = Tracking.objects.select_related("candidate").get(candidate=self._candidate, tracking_date=tracking_date)
        except Tracking.DoesNotExist:
            tracking = Tracking(candidate=self._candidate, tracking_date=tracking_date)

        return model_to_dict(tracking)

    @debug
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            TRACKING_NAMES=Requirements.TRACKING_NAMES,
            cycle = self._cycle,
            candidate=self._candidate,
            cycle_day=self._cycle.cycle_day(self.kwargs.get("tracking_date")),
            tracking=self.get_initial(),
        )

        return context

    @debug
    def get_form_kwargs(self):
        # Add additional keywords to initialize the ModelForm
        kwargs = super(TrackingFormView, self).get_form_kwargs()
        kwargs.update(cycle=self._cycle)

        return kwargs

    @debug
    def form_valid(self, form: TrackingForm):
        logger.info(f"TrackingForm.form_valid({form.fields})")
        return render(self.request, "tracking/partials/tracking.html", self.get_context_data())
