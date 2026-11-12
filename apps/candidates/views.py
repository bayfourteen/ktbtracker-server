import json
import logging
from pprint import pprint

from django.db.models import QuerySet
from django.shortcuts import render
from django.views.generic import ListView

from apps.candidates.models import Candidate
from apps.cycles.models import Cycle
from apps.ktbtracker.utils import debug

logger = logging.getLogger(__name__)

class CandidatesListView(ListView):
    template_name = "candidates/index.html"
    context_object_name = "candidates"
    paginate_by = 20
    model = Candidate

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        if self.request.GET.get("cycle") not in [None, "", "0"]:
            queryset = queryset.filter(cycle__id=int(self.request.GET.get("cycle", 0)))
        queryset = queryset.order_by("user__first_name", "user__last_name", "user__username")
        return queryset.select_related("user", "cycle").all()

    @debug
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = context.get("page_obj")
        paginator = context.get("paginator")

        context["page_range"] = paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)
        context["cycles"] = Cycle.objects.order_by("-cycle_start").all()
        context["selected_cycle"] = self.request.GET.get("cycle")

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx:
            logger.info("HTMX... request detected, rendering candidate selector widget")
            self.template_name = "candidates/widgets/selector.html#candidate-selector"

        response = super().render_to_response(context, **response_kwargs)
        return response
