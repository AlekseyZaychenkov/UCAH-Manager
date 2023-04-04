from workspace_editor.models import Workspace, TagRule
from loader.models import Post

def apply_substitution_rules(workspace_id: int, post_id: int):
    workspace = Workspace.objects.get(workspace_id=workspace_id)
    tag_rules = TagRule.objects.filter(event_rules=workspace.event_rules)
    post = Post.objects.get(id=post_id)

    substituted_tags = list()
    for tag_rule in tag_rules:
        for tag in post.tags:
            if tag == tag_rule.input:
                substituted_tags.append(tag_rule.output)
            else:
                substituted_tags.append(tag)
    post.tags = substituted_tags
    post.save()
