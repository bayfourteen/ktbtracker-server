import logging

from django.shortcuts import render
from django.views.generic import ListView

from apps.cycles.models import Cycle
from apps.ktbtracker.utils import debug

logger = logging.getLogger(__name__)


class CyclesListView(ListView):
    template_name = "cycles/index.html"
    context_object_name = "cycles"
    ordering = ("-cycle_start",)
    model = Cycle

    @debug
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = context.get("page_obj")
        paginator = context.get("paginator")

        if paginator:
            context["page_range"] = paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)
        context["selected_cycle"] = self.request.GET.get("cycle")

        return context

    def get_paginate_by(self, queryset):
        if self.request.htmx:
            return None
        return 20

    @debug
    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx:
            logger.info("HTMX... request detected, rendering cycle selector widget")
            self.template_name = "cycles/widgets/selector.html#user-selector"

        response = super().render_to_response(context, **response_kwargs)
        return response
