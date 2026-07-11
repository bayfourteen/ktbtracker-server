import logging
from collections import defaultdict
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.forms.models import model_to_dict
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, ListView, UpdateView
from django_htmx.http import HttpResponseClientRefresh, trigger_client_event

from ktbtracker.forms import TrackingForm
from ktbtracker.models import (
    Candidate,
    Cycle,
    CycleWeek,
    Requirements,
    Tracking,
    TrackingStatistics,
)
from ktbtracker.utils import debug

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
        logger.info(f"...setup {request=}, {request.user=} HTMX: {request.htmx == True}")
        today_date = datetime.now(ZoneInfo("America/New_York")).date()

        #
        # Determine the current cycle from the session if available, otherwise use the latest cycle or administrator selected...
        #
        logger.debug(f"...setup: cycle <<< Session: _cycle={request.session.get('_cycle', None)} Query: cycle={request.GET.get('cycle', None)}")
        if cycle_id := request.session.get("_cycle", 0):
            self.cycle = Cycle.objects.get(id=int(cycle_id))
        else:
            self.cycle = Cycle.objects.all().order_by("-id").first()
            request.session.update({"_cycle": self.cycle.id})

        if request.user.is_staff and request.GET.get("cycle") is not None:
            try:
                q_cycle = int(request.GET.get("cycle", ""))
                if q_cycle != self.cycle.id:
                    self.cycle = Cycle.objects.get(id=q_cycle)
                    request.session.update({"_cycle": self.cycle.id})
            except (ValueError, Cycle.DoesNotExist):
                self.cycle = Cycle.objects.all().order_by("-id").first()
                request.session.update({"_cycle": self.cycle.id})

        logger.debug(f"...setup: cycle >>> {self.cycle}")

        #
        # Determine the current candidate from the session if available, otherwise from the logged-in user or administrator selected...
        #
        logger.debug(f"...setup: candidate <<< Session: _candidate={request.session.get('_candidate', None)} Query: canid={request.GET.get('canid', None)}")
        if candidate_id := request.session.get("_candidate", 0):
            try:
                self.candidate = Candidate.objects.select_related("cycle", "user").get(id=int(candidate_id))
            except Candidate.DoesNotExist:
                self.candidate = None
                request.session.delete("_candidate")
        else:
            try:
                self.candidate = Candidate.objects.select_related("cycle", "user").filter(
                    user__id=request.user.id
                ).order_by("-id").first()
                if self.candidate:
                    request.session.update({"_candidate": self.candidate.id})
            except Candidate.DoesNotExist:
                self.candidate = None
                request.session.delete("_candidate")

        if request.user.is_staff and request.GET.get("canid") is not None:
            try:
                q_canid = int(request.GET.get("canid", ""))
                if q_canid != self.candidate.id:
                    self.candidate = Candidate.objects.select_related("cycle", "user").get(id=int(request.GET.get("canid", 0)))
                    request.session.update({"_candidate": self.candidate.id})
            except (ValueError, Candidate.DoesNotExist):
                self.candidate = None
                request.session.delete("_candidate")

        if self.candidate and self.candidate.cycle.id != self.cycle.id:
            logger.warning(f"The current candidate ({self.candidate.id or 0}) is not part of the current cycle.")
            self.candidate = None
            request.session.delete("_candidate")

        logger.debug(f"...setup: candidate >>> {self.candidate}")

        #
        # Mange the cycle week being viewed (default to the cycle week of the current date)...
        #
        logger.debug(f"...setup: week <<< Session: _week={request.session.get('_week', None)}, Query: week={request.GET.get('week', None)}")
        if week_idx := request.session.get("_week", None) is not None:
            try:
                week_idx = int(week_idx)
                self.tracking_week = self.cycle.cycle_week(week_idx if week_idx <= 0 else week_idx - 1)
            except ValueError:
                self.tracking_week = self.cycle.cycle_week_of(today_date)
                request.session.update({"_week": self.tracking_week.week if self.tracking_week.week < 0 else self.tracking_week.week + 1})
        else:
            self.tracking_week = self.cycle.cycle_week_of(today_date)
            request.session.update({"_week": self.tracking_week.week if self.tracking_week.week < 0 else self.tracking_week.week + 1})

        if self.request.GET.get("week", None) is not None:
            try:
                q_week = int(self.request.GET.get("week", 0))
                self.tracking_week = self.cycle.cycle_week(q_week if q_week <= 0 else q_week - 1)
                request.session.update({"_week": self.tracking_week.week if self.tracking_week.week < 0 else self.tracking_week.week + 1})
            except ValueError:
                self.tracking_week = self.cycle.cycle_week_of(today_date)
                request.session.update({"_week": self.tracking_week.week if self.tracking_week.week < 0 else self.tracking_week.week + 1})

        logger.debug(f"...setup: week >>> {self.tracking_week}")

        logger.debug(f"...setup: tracking_date <<< Session: _tracking_date={request.session.get('_tracking_date', None)}, Query: trackingDate={request.GET.get('trackingDate', None)}")
        if tracking_date := request.session.get("_tracking_date", None):
            try:
                self.tracking_date = date.fromisoformat(tracking_date or "")
            except ValueError:
                self.tracking_date = None
                request.session.delete("_tracking_date")
        else:
            self.tracking_date = None

        if self.request.GET.get("trackingDate") is not None:
            try:
                q_tracking_date = date.fromisoformat(self.request.GET.get("trackingDate", ""))
                self.tracking_date = q_tracking_date
                self.tracking_week = self.cycle.cycle_week_of(self.tracking_date)
                request.session.update({"_tracking_date": self.tracking_date.isoformat()})
                request.session.update({"_week": self.tracking_week.week if self.tracking_week.week < 0 else self.tracking_week.week + 1})
            except ValueError:
                self.tracking_date = None

        logger.debug(f"...setup: tracking_data >>> {self.tracking_date=}")
        logger.debug(f"...setup: week >>> {self.tracking_week}")

class TrackingListView(TrackingBaseView, ListView):
    template_name = "tracking/index.html"
    model = Tracking

    @debug
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if request.htmx:
            self.template_name += "#tracking-list"

    @debug
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @debug
    def get_queryset(self) -> QuerySet:
        if not self.candidate or self.candidate.cycle.id != self.cycle.id:
            return Tracking.objects.none()

        return Tracking.objects.select_related("candidate").filter(
            candidate__id=self.candidate.id,
            tracking_date__range=(self.tracking_week.start, self.tracking_week.end),
        ).order_by("tracking_date").all()

    @debug
    def get_context_data(self, **kwargs):
        today = datetime.now(ZoneInfo("America/New_York")).date()
        tracking_data = defaultdict(list)
        tracking_statistics = TrackingStatistics(self.candidate, self.tracking_week)
        cycle_statistics = TrackingStatistics(self.candidate, None)
        cycle_candidates = Candidate.objects.select_related("cycle", "user").filter(
            cycle=self.cycle
        ).order_by("user__last_name", "user__first_name").all()

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
            cycle_start=self.cycle.cycle_pre_start or self.cycle.cycle_start,
            cycle_end=self.cycle.cycle_post_end or self.cycle.cycle_end,
            editable_start=today - timedelta(days=3),
            editable_end=today + timedelta(days=3),
            today=today,
        )

        return context

    #def render_to_response(self, context, **response_kwargs):
    #    response = super().render_to_response(context, **response_kwargs)
    #    return trigger_client_event(response, "trackingListUpdated")


class TrackingEditView(TrackingBaseView, UpdateView):
    template_name = "tracking/index.html"
    form_class = TrackingForm
    model = Tracking

    @debug
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if request.htmx:
            self.template_name += "#tracking-editor"

    @debug
    def get_object(self, queryset: QuerySet | None = None ) -> Tracking:
        if not self.candidate or self.candidate.cycle.id != self.cycle.id:
            return Tracking.objects.none().first()

        try:
            tracking = (Tracking.objects.select_related("candidate").get(
                candidate__id=self.candidate.id or 0,
                tracking_date=self.kwargs.get("tracking_date"))
            )
        except Tracking.DoesNotExist:
            tracking = Tracking(candidate=self.candidate, tracking_date=self.kwargs.get("tracking_date"))

        return tracking

    @debug
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "cycle": self.cycle,
            "candidate": self.candidate
        })

        return kwargs

    @debug
    def get_context_data(self, **kwargs):
        tracking_date = self.kwargs.get("tracking_date")
        tracking_day = self.cycle.cycle_day(tracking_date)

        context = super().get_context_data(**kwargs)
        context.update(
            TRACKING_NAMES=Requirements.TRACKING_NAMES(),
            cycle = self.cycle,
            candidate=self.candidate,
            cycle_start=self.cycle.cycle_pre_start or self.cycle.cycle_start,
            cycle_end=self.cycle.cycle_post_end or self.cycle.cycle_end,
            tracking=self.get_initial(),
            tracking_day=tracking_day if tracking_day > 0 else tracking_day - 1,
            tracking_date=tracking_date,
        )

        return context

    def get_success_url(self):
        return reverse_lazy("tracking-index", fragment="tracking-list")

    @debug
    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            response = HttpResponseClientRefresh()  # HttpResponseClientRefresh()
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
