from django.urls import path

from workspace_editor.views.views import *
from workspace_editor.views.event_rules_views import *

urlpatterns = [
    path('workspace', home, name="workspace"),
    path('workspace?workspace_id=<int:workspace_id>', home, name="workspace_by_id"),
    path('downloading?workspace_id=<int:workspace_id>', downloading, name="downloading_workspace_by_id"),

    path('workspace?workspace_id=<int:workspace_id>?post_id=<str:post_id>', home,
         name="workspace_by_id_post_by_id"),
    path('workspace?workspace_id=<int:workspace_id>?post_edit_id=<str:post_id>', home,
         name="workspace_by_id_post_edit_by_id"),
    path('workspace?workspace_id=<int:workspace_id>?post_delete_id=<str:post_id>', home,
         name="workspace_by_id_post_delete_by_id"),

    path('workspace/workspace_id=<int:workspace_id>/rules', event_rules_view, name="event_rules"),
    path('workspace/workspace_id=<int:workspace_id>/rules/event_rule_id=<int:event_rule_id>/delete',
                                                        event_rules_view, name="event_rules_tag_rule_delete"),

    path('downloading?workspace_id=<int:workspace_id>?post_id=<str:post_id>', downloading,
         name="downloading_workspace_by_id_post_by_id"),
    path('downloading?workspace_id=<int:workspace_id>?post_edit_id=<str:post_id>', downloading,
         name="downloading_workspace_by_id_post_edit_by_id"),
    path('downloading?workspace_id=<int:workspace_id>?post_delete_id=<str:post_id>', downloading,
         name="downloading_workspace_by_id_post_delete_by_id"),

    path('downloading?workspace_id=<int:workspace_id>?holder_id=<int:holder_id>', downloading,
         name="downloading_workspace_by_id_holder_by_id"),
    path('downloading?workspace_id=<int:workspace_id>?holder_id_to_delete=<int:holder_id_to_delete>', downloading,
         name="downloading_workspace_by_id_holder_by_id_to_delete"),

    path('workspace/workspace_id=<int:workspace_id>/resource_accounts', resource_accounts, name="resource_accounts"),
    path(
        'workspace/workspace_id=<int:workspace_id>/resource_accounts/resource_account_id=<int:resource_account_id>/add_blog',
        resource_account_add_blog, name="resource_account_add_blog"),
    path('workspace/workspace_id=<int:workspace_id>/resource_accounts/resource_account_id=<int:resource_account_id>/edit',
         resource_accounts, name="resource_account_edit"),
    path('workspace/workspace_id=<int:workspace_id>/resource_accounts/resource_account_id=<int:resource_account_id>/delete',
        resource_accounts, name="resource_account_delete"),
    # path('workspace/workspace_id=<int:workspace_id>/resource_accounts/create', resource_accounts, name="resource_accounts_create"),
    # TODO: investigate, why here <int:blog_id>':
    path('workspace/workspace_id=<int:workspace_id>/resource_accounts/resource_account_id=<int:blog_id>', resource_accounts,
         name="resource_accounts_resource_account_by_id"),

    path('workspace/workspace_id=<int:workspace_id>/blogs', blogs, name="blogs"),
    path('workspace/workspace_id=<int:workspace_id>/blogs/blog_id=<int:blog_id>/delete', blogs, name="blog_delete"),
]

