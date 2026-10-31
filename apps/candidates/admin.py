from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import AbstractUser

from apps.candidates.models import Candidate
from apps.cycles.models import Cycle


@admin.register(Candidate)
class CandidatesAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ("id", "candidate", "belt_rank","status", "audit_icon", "user__email", "cycle_title")

    # Clickable links that open the detail view
    list_display_links = ("id",)

    # Fields that can be filtered via a right-hand sidebar
    list_filter = ()

    # Columns searchable via a top search bar
    search_fields = ("name", "description")

    # Fields that can be edited directly on the list view page
    list_editable = ()

    # Sets the default order of items (- means descending)
    ordering = ("user__last_name", "-user__first_name", "-cycle_id")

    # Pagination: number of items per page
    list_per_page = 25
    @admin.display(description="Audit", boolean=False)
    def audit_icon(self, obj) -> str:
        if obj.audit:
            return format_html('<i class="text-success fa-solid fa-circle-check"></i>', obj.audit)
        return ""

    @admin.display(empty_value="N/A", description="Candidate")
    def candidate(self, obj) -> str:
        return f"{obj.user.last_name + ', ' if obj.user.last_name else ''}{obj.user.first_name} ({obj.user.username})"

    @admin.display(empty_value="N/A", description="Cycle | Split Cycle")
    def cycle_title(self, obj) -> str:
        if obj.cycle_cont:
            split_cycle = Cycle.objects.get(id=obj.cycle_cont)
            return f"{obj.cycle.title} | {split_cycle.title}"
        return obj.cycle.title if obj.cycle else "N/A"
