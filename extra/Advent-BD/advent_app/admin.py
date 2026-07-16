from django.contrib import admin

from .models import AdventClaim, AdventDayConfig


@admin.register(AdventDayConfig)
class AdventDayConfigAdmin(admin.ModelAdmin):
    list_display = ("day", "enabled", "reward_type", "ball", "special")
    autocomplete_fields = ("ball", "special")
    search_fields = ("day", "label")


@admin.register(AdventClaim)
class AdventClaimAdmin(admin.ModelAdmin):
    list_display = ("player", "day", "claimed_at")
    autocomplete_fields = ("player",)
    search_fields = ("player__discord_id",)
