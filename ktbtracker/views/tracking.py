import logging
from collections import OrderedDict
from datetime import date, timedelta, datetime
from itertools import cycle
from zoneinfo import ZoneInfo

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.forms.models import model_to_dict
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView, ListView

from config.requirements import RequirementsConfig
from ktbtracker import debug
from ktbtracker.forms import TrackingForm
from ktbtracker.models import Candidate, Cycle, CycleWeek, Tracking, TrackingFullStatistics, TrackingStatistics

logger = logging.getLogger(__name__)

TRACKING_NAMES = OrderedDict(
    {e: _(e) for e in (RequirementsConfig.PHYSICAL + RequirementsConfig.CLASS + RequirementsConfig.OTHER)})


@debug
def calculate_tracking_totals(candidate: Candidate, cycle_week: CycleWeek | None = None) -> dict[str, float]:
    tracking_totals = {}
    candidate_tracking = Tracking.objects.filter(
        candidate=candidate,
        tracking_date_range=(cycle_week.start if cycle_week else candidate.cycle.cycle_start, cycle_week.end if cycle_week else candidate.cycle.cycle_end)
    ).values_list()

    for name in TRACKING_NAMES.keys():
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
    for name in TRACKING_NAMES.keys():
        full_statistics[name] = [t.get(name, 0) for t in full_tracking]


class TrackingBaseView(View):
    @property
    def _candidate(self) -> Candidate:
        # Determine the most recent candidate (or candidate chosen by a staff member)...
        if self.request.user.is_staff and self.request.GET.get("canid") and self.request.GET.get("canid").isdigit():
            return Candidate.objects.select_related("cycle", "user").get(id=int(self.request.GET.get("canid")))
        else:
            return Candidate.objects.select_related("cycle", "user").filter(user__id=self.request.user.id).order_by("-id").first()

    @property
    def _cycle(self) -> Cycle:
        # Determine the most recent cycle (or cycle chosen by a staff member)...
        if self.request.user.is_staff and self.request.GET.get("cycle") and self.request.GET.get("cycle").isdigit():
            return Cycle.objects.get(id=int(self.request.GET.get("cycle")))
        else:
            return Cycle.objects.all().order_by("-id").first()

    @property
    def _tracking_date(self) -> date:
        if self.request.GET.get("trackingDate"):
            try:
                return datetime.fromisoformat(self.request.GET.get("trackingDate")).date()
            except ValueError:
                return datetime.now(ZoneInfo("America/New_York")).date()
            # return datetime.strptime(self.request.GET.get("trackingDate"), "%Y-%m-%d").date()
        return datetime.now(ZoneInfo("America/New_York")).date()

    @property
    def _week(self) -> int | None:
        if self.request.GET.get("week"):
            try:
                q_week = int(self.request.GET.get("week"))
                return q_week if q_week <= 0 else q_week - 1
            except ValueError:
                return None
        return None


class TrackingListView(LoginRequiredMixin, TrackingBaseView, ListView):
    template_name = "tracking/index.html"
    model = Tracking

    @debug
    def get_queryset(self) -> QuerySet:
        tracking_week = self._cycle.cycle_week(self._week) if self._week is not None else self._cycle.cycle_week_of(self._tracking_date)

        return Tracking.objects.select_related("candidate").filter(
            candidate=self._candidate,
            tracking_date__range=(tracking_week.start, tracking_week.end),
            #tracking_date__gte=tracking_week.start,
            #tracking_date__lt=tracking_week.end + timedelta(days=1)
        ).all()

    @debug
    def get_context_data(self, *, object_list = ..., **kwargs):
        tracking_week = self._cycle.cycle_week(self._week) if self._week is not None else self._cycle.cycle_week_of(self._tracking_date)
        tracking_statistics = TrackingStatistics(self._candidate, tracking_week)
        cycle_statistics = TrackingStatistics(self._candidate, None)
        cycle_candidates = Candidate.objects.select_related("cycle", "user").filter(cycle=self._cycle).order_by("user__last_name", "user__first_name").all()

        context = super().get_context_data(**kwargs)
        context.update(
            TRACKING_NAMES=TRACKING_NAMES,
            cycle = self._cycle,
            candidate = self._candidate,
            tracking_week=tracking_week,
            tracking_stats=tracking_statistics.statistics,
            tracking_totals=tracking_statistics.totals,
            cycle_stats=cycle_statistics.statistics,
            cycle_totals=cycle_statistics.totals,
            cycle_candidates=cycle_candidates,
            today=datetime.now(ZoneInfo("America/New_York")).date(),
        )

        return context


class TrackingFormView(LoginRequiredMixin, TrackingBaseView, FormView):
    template_name = "tracking/editor.html"
    form_class = TrackingForm

    @debug
    def get_initial(self):
        try:
            tracking = Tracking.objects.select_related("candidate").get(candidate=self._candidate, tracking_date=self._tracking_date)
        except Tracking.DoesNotExist:
            tracking = Tracking(candidate=self._candidate, tracking_date=self._tracking_date)

        return model_to_dict(tracking)

    @debug
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            TRACKING_NAMES=TRACKING_NAMES,
            cycle = self._cycle,
            candidate=self._candidate,
            cycle_day=self._cycle.cycle_day(self._tracking_date),
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
