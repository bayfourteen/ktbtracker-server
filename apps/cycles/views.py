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

        # Cache (or clear) the selected cycle in the session for use in other views
        if self.request.GET.get("cycle") not in [None, "", "0"]:
            self.request.session["_cycle_id"] = int(self.request.GET.get("cycle", 0))
        elif self.request.GET.get("cycle") in ["", "0"]:
            self.request.session.pop("_cycle_id", None)
        context["selected_cycle"] = self.request.GET.get("cycle") or self.request.session.get("_cycle_id")

        # For full page (non-HTMX) requests, add pagination info to context
        if not self.request.htmx:
            page_obj = context.get("page_obj")
            context["elided_range"] = page_obj.paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)

        return context

    def get_paginate_by(self, queryset):
        if self.request.htmx:
            return None
        return 20

    @debug
    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx:
            logger.info("HTMX... request detected, rendering cycle selector widget")
            self.template_name = "cycles/widgets/selector.html#cycle-selector"

        response = super().render_to_response(context, **response_kwargs)
        return response
