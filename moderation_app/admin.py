from django.contrib import admin

from .models import GuildConfig, Warning


@admin.register(Warning)
class WarningAdmin(admin.ModelAdmin):
    list_display = ("user_id", "guild_id", "moderator_id", "reason", "created_at")
    list_filter = ("guild_id",)
    search_fields = ("user_id", "reason")
    readonly_fields = ("created_at",)


@admin.register(GuildConfig)
class GuildConfigAdmin(admin.ModelAdmin):
    list_display = ("guild_id", "muted_role_id")
    search_fields = ("guild_id",)
