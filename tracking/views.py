import logging
from collections import OrderedDict
from datetime import date, timedelta, datetime
from operator import itemgetter

from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.template import loader
from django.utils.translation import gettext_lazy as _

from config.requirements import RequirementsConfig
from core.models import Tracking, Cycles, Candidates, CycleWeek
from tracking.forms import TrackingForm
from tracking.models import TrackingStatistics, TrackingFullStatistics

logger = logging.getLogger(__name__)

TRACKING_NAMES = OrderedDict(
    {e: _(e) for e in (RequirementsConfig.PHYSICAL + RequirementsConfig.CLASS + RequirementsConfig.OTHER)})


def calculate_tracking_totals(candidate: Candidates, cycle_week: CycleWeek | None = None) -> dict[str, float]:
    tracking_totals = {}
    candidate_tracking = Tracking.objects.filter(
        candidate=candidate,
        tracking_date__gte=cycle_week.start if cycle_week else candidate.cycle.cycle_start,
        tracking_date__lt=(cycle_week.end if cycle_week else candidate.cycle.cycle_end) + timedelta(days=1)
    ).values_list()

    for name in TRACKING_NAMES.keys():
        tracking_totals[name] = sum([t.get(name, 0) for t in candidate_tracking])

    return tracking_totals


def calculate_statistics(candidate: Candidates, cycle_week: CycleWeek | None = None):
    tracking_statistics = {}
    tracking_totals = calculate_tracking_totals(candidate, cycle_week)


def calculate_full_statistics(candidate: Candidates):
    full_statistics = {}
    full_tracking = Tracking.objects.filter(
        candidate=candidate,
        tracking_date__gte=candidate.cycle.cycle_start,
        tracking_date__lt=candidate.cycle.cycle_end + timedelta(days=1)
    ).values_list()
    for name in TRACKING_NAMES.keys():
        full_statistics[name] = [t.get(name, 0) for t in full_tracking]


# Create your views here.
def index(request: HttpRequest):
    # Process any query parameters...
    week = request.GET.get("week")
    tracking_date = request.GET.get("trackingDate")
    tracking_date = datetime.strptime(tracking_date, "%Y-%m-%d").date() if tracking_date else None

    template = loader.get_template("tracking/index.html")
    cycle = Cycles.objects.filter(id=36).first()
    candidate = Candidates.objects.filter(id=691).first()

    tracking_week = cycle.cycle_week(int(week)) if week else cycle.cycle_week_of(tracking_date or date.today())
    tracking_day = cycle.cycle_day(tracking_week.start)
    tracking_query = Tracking.objects.filter(
        candidate=candidate,
        tracking_date__gte=tracking_week.start,
        tracking_date__lt=tracking_week.end + timedelta(days=1)
    )
    tracking_statistics = TrackingFullStatistics(candidate)
    tracking_data = []
    for tracking_date in [tracking_week.start + timedelta(days=n) for n in range(0, len(tracking_week.days))]:
        if tracking_query.filter(tracking_date=tracking_date).exists():
            tracking_data.append(tracking_query.get(tracking_date=tracking_date))
        else:
            tracking_data.append(Tracking(candidate=candidate, tracking_date=tracking_date))

    context = {
        "TRACKING_NAMES": TRACKING_NAMES,
        "cycle": cycle,
        "candidate": candidate,
        "tracking_date": (tracking_date or date.today()).isoformat(),
        "tracking_week": tracking_week,
        "tracking_data": [model_to_dict(e) for e in tracking_data],
        "statistics": tracking_statistics.weeks[tracking_week.week].statistics,
        "totals": tracking_statistics.weeks[tracking_week.week].totals,
        "cycle_statistics": tracking_statistics.cycle,
        "today": date.today(),
    }

    return HttpResponse(template.render(context, request))


def editor(request: HttpRequest):
    template = loader.get_template("tracking/editor.html")
    cycle = Cycles.objects.filter(id=36).first()
    candidate = Candidates.objects.filter(id=691).first()

    if request.method == "POST":
        pass

    else:
        # Process any query parameters...
        candidate_id = request.GET.get("canid")
        tracking_date = request.GET.get("trackingDate")
        tracking_date = datetime.strptime(tracking_date, "%Y-%m-%d").date() if tracking_date else None

        try:
            tracking = Tracking.objects.get(tracking_date=tracking_date, candidate=candidate)
        except Tracking.DoesNotExist:
            tracking = Tracking(candidate=candidate, tracking_date=tracking_date)

        form = TrackingForm(instance=tracking, cycle=cycle)

        context = {
            "TRACKING_NAMES": TRACKING_NAMES,
            "cycle": cycle,
            "candidate": candidate,
            "form": form
        }
        logger.info(f"TrackinForm.fields={form.fields}")
        return HttpResponse(template.render(context, request))
