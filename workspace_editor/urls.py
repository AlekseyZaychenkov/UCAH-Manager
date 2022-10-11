from django.urls import path

from workspace_editor.views import home, downloading


urlpatterns = [
    path('workspace', home, name="workspace"),
    path('workspace?workspace_id=<int:workspace_id>', home, name="workspace_by_id"),
    path('workspace?workspace_id=<int:workspace_id>?post_id=<str:post_id>', home, name="workspace_by_id_post_by_id"),
    path('downloading?workspace_id=<int:workspace_id>', downloading, name="downloading_workspace_by_id"),
    path('downloading?workspace_id=<int:workspace_id>?post_id=<str:post_id>', downloading, name="downloading_workspace_by_id_post_by_id"),
    path('downloading?workspace_id=<int:workspace_id>?holder_id=<int:holder_id>', downloading, name="downloading_workspace_by_id_holder_by_id"),
    path('downloading?workspace_id=<int:workspace_id>?holder_id_to_delete=<int:holder_id_to_delete>', downloading, name="downloading_workspace_by_id_holder_by_id_to_delete"),
]

