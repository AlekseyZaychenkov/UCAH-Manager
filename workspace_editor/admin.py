from django.contrib import admin
from workspace_editor.models import *


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    pass

@admin.register(ScheduleArchived)
class ScheduleArchiveAdmin(admin.ModelAdmin):
    pass

# @admin.register(Schedule)
# class ScheduleAdmin(admin.ModelAdmin):
#     pass
#

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
    list_display = ('event_id', 'datetime', 'schedule')
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



@admin.register(CompilationHolder)
class CompilationHolderAdmin(admin.ModelAdmin):
    list_display = ('compilation_holder_id', 'name', 'type_by_post_source', 'compilation_id')


@admin.register(CompilationHolderFilterDownloader)
class CompilationHolderFilterDownloaderAdmin(admin.ModelAdmin):
    list_display = ('compilation_holder', 'resource')

@admin.register(CompilationHolderFilterMixer)
class CompilationHolderFilterMixerAdmin(admin.ModelAdmin):
    list_display = ('compilation_holder', 'source_compilation_holder', 'priority', 'posts_likes_minimum', 'posts_likes_expected')