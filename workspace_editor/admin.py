from django.contrib import admin

from django import forms
from workspace_editor.models import *


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    pass


# @admin.register(Schedule)
# class ScheduleAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(ScheduleArchive)
# class ScheduleArchiveAdmin(admin.ModelAdmin):
#     pass

@admin.register(ResourceAccount)
class ResourceAccountAdmin(admin.ModelAdmin):
    pass


@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    pass


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    pass


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(TagRule)
class TagRuleAdmin(admin.ModelAdmin):
    pass


@admin.register(PostingTime)
class PostingTimeAdmin(admin.ModelAdmin):
    list_display = ('posting_time_id', 'event_rules', 'priority', 'time')


@admin.register(EventRules)
class EventsRulesAdmin(admin.ModelAdmin):
    pass