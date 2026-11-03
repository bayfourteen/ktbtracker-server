from datetime import date

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _

from apps.candidates.models import Candidate
from apps.cycles.models import Cycle, CycleChoiceField
from apps.ktbtracker.models import BeltRank
from apps.users.models import UserChoiceField, User


@admin.register(Cycle)
class CyclesAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = (
        "cycle_title",
        "cycle_start_date",
        "cycle_end_date",
        "pre_start_date",
        "cut_off_date",
        "candidate_count",
        "id",
    )

    # Clickable links that open the detail view
    list_display_links = ("id",)

    # Fields that can be filtered via a right-hand sidebar
    list_filter = ()

    # Columns searchable via a top search bar
    search_fields = ("name", "description")

    # Fields that can be edited directly on the list view page
    list_editable = ()

    #list_select_related = ("candidates",)

    # Sets the default order of items (- means descending)
    ordering = ("-cycle_start",)

    # Pagination: number of items per page
    list_per_page = 25

    readonly_fields = ("created", "created_by", "modified", "modified_by")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "cycle":
            return CycleChoiceField(Cycle.objects.order_by("-cycle_start").all())
        if db_field.name == "user":
            return UserChoiceField(
                User.objects.order_by("last_name", "first_name", "username").all()
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description="Candidates")
    def candidate_count(self, obj: Cycle) -> int:
        return obj.candidates.count()

    @admin.display(empty_value="N/A", description="Cut Off Date")
    def cut_off_date(self, obj: Cycle) -> date:
        return obj.cycle_post_end
    
    @admin.display(empty_value="N/A", description="Cycle")
    def cycle_title(self, obj: Cycle) -> str:
        return obj.title

    @admin.display(empty_value="N/A", description="Cycle Start")
    def cycle_start_date(self, obj: Cycle) -> date:
        return obj.cycle_start

    @admin.display(empty_value="N/A", description="Cycle Finish")
    def cycle_end_date(self, obj: Cycle) -> date:
        return obj.cycle_end

    @admin.display(empty_value="N/A", description="Pre-cycle Start")
    def pre_start_date(self, obj: Cycle) -> date:
        return obj.cycle_pre_start
