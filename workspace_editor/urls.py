from django.urls import path, re_path
from workspace_editor.views import home
from django.contrib import admin
from django.conf.urls import include


urlpatterns = [
    path('workspace', home, name="workspace"),
    path('workspace?workspace_id=<int:workspace_id>', home, name="workspace_by_id"),
]

