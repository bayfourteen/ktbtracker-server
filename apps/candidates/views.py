import json
import logging
from pprint import pprint

from django.db.models import QuerySet
from django.shortcuts import render
from django.views.generic import ListView

import candidates
from apps.candidates.models import Candidate
from apps.cycles.models import Cycle

logger = logging.getLogger(__name__)

class CandidatesListView(ListView):
    template_name = "candidates/index.html"
    context_object_name = "candidates"
    ordering = ["user__first_name", "user__last_name"]
    paginate_by = 20
    model = Candidate

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

        if request.user.is_staff and request.GET.get("cycle") is not None:
            try:
                q_cycle = int(request.GET.get("cycle", ""))
                if q_cycle != self.cycle.id:
                    self.cycle = Cycle.objects.get(id=q_cycle)
                    request.session.update({"_cycle": self.cycle.id})
            except (ValueError, Cycle.DoesNotExist):
                self.cycle = Cycle.objects.all().order_by("-id").first()
                request.session.update({"_cycle": self.cycle.id})

    def get_queryset(self) -> QuerySet:
        return (Candidate.objects.select_related("cycle")
                .filter(cycle__id=self.cycle.id)
                .order_by("user__first_name", "user__last_name")
                .all())

    def get_context_data(self, **kwargs):
        print(f"context_data kwargs: {kwargs}")
        context = super().get_context_data(**kwargs)
        page_obj = context.get("page_obj")
        paginator = context.get("paginator")
        pprint(context.get("candidates")[0].user.__dict__)
        context["page_range"] = paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)
        # print(f"Page range: {list(context['page_range'])} {page_obj.number}")
        return context
