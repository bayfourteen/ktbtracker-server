import datetime
import logging

from bs4 import BeautifulSoup
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, UpdateView
from django_htmx.http import HttpResponseClientRefresh, trigger_client_event

from apps.candidates.models import Candidate
from apps.cycles.models import Cycle
from apps.journals.forms import JournalForm
from apps.journals.models import JournalPost
from apps.ktbtracker.utils import debug
from apps.users.models import User

logger = logging.getLogger(__name__)

class JournalsListView(ListView):
    template_name = "journals/index.html"
    context_object_name = "journals"
    ordering = ["-created"]
    paginate_by = 20
    model = JournalPost

    @debug
    def get_queryset(self):
        queryset = super().get_queryset()
        if candidate_id := self.request.GET.get("canid"):
            user_id = Candidate.objects.get(id=candidate_id).user_id
            queryset = queryset.filter(created_by=user_id, published=True)
        if cycle_id := self.request.GET.get("cycle"):
            cycle = Cycle.objects.get(id=cycle_id)
            queryset = queryset.filter(
                created__gte=cycle.cycle_pre_start or cycle.cycle_start,
                created__lte=cycle.cycle_post_end or cycle.cycle_end
            )
        return queryset.select_related("user").all()

    @debug
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Cache (or clear) the selected candidate in the session for use in other views
        if self.request.GET.get("canid") not in [None, "", "0"]:
            self.request.session["_canid"] = int(self.request.GET.get("canid", 0))
        elif self.request.GET.get("canid") in ["", "0"]:
            self.request.session.pop("_canid", None)
        context["selected_candidate"] = self.request.GET.get("canid") or self.request.session.get("_canid")

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

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        if self.request.htmx:
            self.template_name += "#journals-list"
            response = HttpResponseClientRefresh()
            return response

        return response

class JournalsEditView(UpdateView):
    template_name = "journals/partials/editor-dialog.html"
    success_url = ""
    form_class = JournalForm
    model = JournalPost

    @debug
    def get_initial(self):
        initial = super().get_initial()
        initial["content"] = BeautifulSoup(self.object.content, "html.parser").get_text(separator="\n", strip=True)
        return initial

    @debug
    def form_valid(self, form: JournalForm) -> HttpResponse:
        form.instance.content = BeautifulSoup(form.instance.content, "html.parser").get_text(separator="\n", strip=True)
        form.instance.modified = datetime.datetime.now(datetime.UTC)
        form.instance.modified_by = self.request.user.id
        self.object = form.save()
        if self.request.htmx:
            response = HttpResponseClientRefresh()  # HttpResponseClientRefresh()
            return trigger_client_event(response, "closeEditor")

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("journals:edit", kwargs={"pk": self.object.pk})