from django.contrib import admin

from apps.cycles.models import Cycle


@admin.register(Cycle)
class CyclesAdmin(admin.ModelAdmin):
    pass


