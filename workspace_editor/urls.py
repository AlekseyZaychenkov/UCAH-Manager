from django.urls import path, re_path

from workspace_editor.views import home, downloading


urlpatterns = [
    path('workspace', home, name="workspace"),
    path('workspace?workspace_id=<int:workspace_id>', home, name="workspace_by_id"),
    path('downloading?workspace_id=<int:workspace_id>', downloading, name="downloading_workspace_by_id"),
]

