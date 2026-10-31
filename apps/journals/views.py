import logging

from django.shortcuts import render
from django.views.generic import ListView

from apps.journals.models import JournalPost

logger = logging.getLogger(__name__)

class JournalsListView(ListView):
    template_name = "journals/index.html"
    context_object_name = "journals"
    ordering = ["-created"]
    paginate_by = 20
    model = JournalPost

    def get_context_data(self, **kwargs):
        print(f"context_data kwargs: {kwargs}")
        context = super().get_context_data(**kwargs)
        page_obj = context.get("page_obj")
        paginator = context.get("paginator")

        context["page_range"] = paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)
        # print(f"Page range: {list(context['page_range'])} {page_obj.number}")
        return context
