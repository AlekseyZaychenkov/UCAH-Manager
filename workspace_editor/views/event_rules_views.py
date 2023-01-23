from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from workspace_editor.views.views import __workspace_choice


@login_required
def event_rules(request, workspace_id=None):
    workspace = __workspace_choice(request, workspace_id)

    if workspace:
        if request.POST:
            __event_rules_request_handler(request, workspace)
            return redirect(f'downloading_workspace_by_id', workspace_id=workspace.workspace_id)

        context = __prepare_event_rules_context(request=request, workspace=workspace)
        return render(request, "event_rules/event_rules.html", context)
    else:
        return redirect("workspace")


def __event_rules_request_handler(request, workspace):
    pass


def __prepare_event_rules_context(request, workspace):
    context = dict()

    context["workspace"] = workspace


    return context