import os
from datetime import datetime

from django.http import QueryDict
from django.template.defaulttags import register
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from workspace_editor.forms.event_rules_forms import *

from workspace_editor.models import PostingTime, TagRule, Blog
from workspace_editor.views.views import __workspace_choice


@login_required
def event_rules_view(request, workspace_id=None, tag_rule_id=None):
    workspace = __workspace_choice(request, workspace_id)

    if workspace:
        if request.POST:
            __event_rules_request_handler(request, workspace)
            __tag_rule_request_handler(request, workspace)
            return redirect(f'event_rules', workspace_id=workspace.workspace_id)

        context = __prepare_event_rules_context(request=request, workspace=workspace)
        return render(request, "event_rules/event_rules.html", context)
    else:
        return redirect("workspace")


def __event_rules_request_handler(request, workspace):
    if request.POST['action'] == "event_rules_save":
        posting_time_id_list = request.POST.getlist('posting_time_id')
        posting_time_list = request.POST.getlist('time')
        for i in range(len(posting_time_id_list)):
            query_dict = QueryDict('', mutable=True)
            query_dict.update({'posting_time_id': posting_time_id_list[i], 'time': posting_time_list[i]})
            form = PostingTimeEditForm(query_dict)
            if form.is_valid():
                form.save()
            else:
                log.error(form.errors.as_data())

        form = EventRulesEditForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            log.error(form.errors.as_data())


def __tag_rule_request_handler(request, workspace):
    if request.POST['action'] == "tag_rule_create":
        form = TagRuleCreateForm(request.POST)
        if form.is_valid():
            tag_rule = form.save()

            if tag_rule.for_all:
                blog_ids_list = list()
                blogs = Blog.objects.filter(workspace=workspace, controlled=True)
                for blog in blogs:
                    blog_ids_list.append(blog.blog_id)

                for i in range(len(blog_ids_list)):
                    query_dict = QueryDict('', mutable=True)
                    query_dict.update({'blog_id': int(blog_ids_list[i]),
                                       'tag_rule_id': tag_rule.tag_rule_id,
                                       'apply': True})
                    form = BlogAddTagRuleForm(query_dict)
                    if form.is_valid():
                        form.save()
                    else:
                        log.error(form.errors.as_data())

            else:
                blog_ids_list = request.POST.getlist('blog_id')
                applies_list = request.POST.getlist('apply')
                for i in range(len(applies_list)):
                    query_dict = QueryDict('', mutable=True)
                    query_dict.update({'blog_id': int(blog_ids_list[i]),
                                       'tag_rule_id': tag_rule.tag_rule_id,
                                       'apply': applies_list[i]})
                    form = BlogAddTagRuleForm(query_dict)
                    if form.is_valid():
                        form.save()
                    else:
                        log.error(form.errors.as_data())
        else:
            log.error(form.errors.as_data())

    elif request.POST['action'] == "tag_rule_delete":
        form = TagRuleDeleteForm(request.POST)
        if form.is_valid():
            form.delete()
        else:
            log.error(form.errors.as_data())


def __prepare_event_rules_context(request, workspace):
    context = dict()
    context["MEDIA_LOCATION"] = "../../media"
    context["BLOGS_MEDIA_LOCATION"] \
        = os.path.join("../../media", str(request.user), 'blogs')
    context["workspace"] = workspace

    event_rules = workspace.event_rules
    context["event_rules"] = event_rules

    posting_time_rows = dict({1:list(), 2:list(), 3:list(), 4:list(), 5:list(), 6:list()})
    for i in range(1, 7):
        list_for_current_priority = list(PostingTime.objects.filter(event_rules=event_rules, priority=i))
        for j in range(0, 7):
            if j < len(list_for_current_priority):
                posting_time = list_for_current_priority[j]
                posting_time_and_form = {posting_time : PostingTimeEditForm(
                                                 initial={'posting_time_id': posting_time.posting_time_id,
                                                          'time': posting_time.time}
                                             )
                                        }
                posting_time_rows[j+1].append(posting_time_and_form)
            elif j + 1 in posting_time_rows.keys():
                posting_time_rows[j + 1].append(None)
            else:
                break
    context["posting_time_rows"] = posting_time_rows

    tag_rule_rows = dict()
    tag_rules = TagRule.objects.filter(event_rules=event_rules)
    for tag_rule in tag_rules:
        tag_rule_rows[tag_rule] = Blog.objects.filter(tag_rule=tag_rule)
    context["tag_rule_rows"] = tag_rule_rows

    context["event_rules_edit_form"] = EventRulesEditForm(initial={"distribution_type": event_rules.distribution_type,
                                                                   "start_type": event_rules.start_type})
    context["tag_rule_create_form"] = TagRuleCreateForm()
    blogs = Blog.objects.filter(workspace=workspace, controlled=True)
    blogs_to_forms = dict()
    for blog in blogs:
        blogs_to_forms[blog] = BlogAddTagRuleForm()
    context["blogs_to_forms"] = blogs_to_forms

    context["tag_rule_delete_form"] = TagRuleDeleteForm()

    return context


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)