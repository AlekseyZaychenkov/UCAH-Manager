from django.contrib import admin

from workspace_editor.models import *


# Register your models here.


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