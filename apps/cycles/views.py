from django.shortcuts import render
from django.views.generic import ListView

from apps.cycles.models import Cycle


class CyclesListView(ListView):
    template_name = "cycles/index.html"
    context_object_name = "cycles"
    ordering = ["-cycle_start"]
    paginate_by = 20
    model = Cycle

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = context.get("page_obj")
        paginator = context.get("paginator")

        context["page_range"] = paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)

        return context
