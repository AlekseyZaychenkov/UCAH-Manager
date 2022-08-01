# -*- coding: utf-8 -*-
from django import forms

from loader.models import Post
from workspace_editor.utils import copy_post_to
from workspace_editor.models import Workspace, Event, Schedule
from account.models import Account
from UCA_Manager.settings import PATH_TO_STORE
from loader.utils import generate_storage_patch, create_empty_compilation, \
    save_files_from_request

from django.db.models import Q
from datetime import datetime
import os


class WorkspaceForm(forms.ModelForm):
    visible_for = forms.CharField(required=False)
    editable_by = forms.CharField(required=False)

    class Meta:
        model = Workspace
        exclude = ("owner", "visible_for", "editable_by", "schedule", "schedule_archive",
                   "scheduled_compilation_id", "main_compilation_id", "main_compilation_archive_id")

    def set_owner(self, user):
        workspace = self.instance
        workspace.owner_id = user.pk
        self.instance = workspace

    def set_schedules(self, schedule, schedule_archive):
        workspace = self.instance
        workspace.schedule_id = schedule.schedule_id
        workspace.schedule_archive_id = schedule_archive.schedule_id
        self.instance = workspace

    def save(self, commit=True):
        workspace = self.instance

        workspace.scheduled_compilation_id = create_empty_compilation().id
        workspace.main_compilation_id = create_empty_compilation().id
        workspace.main_compilation_archive_id = create_empty_compilation().id

        if commit:
            workspace.save()

        for email in self.cleaned_data["visible_for"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                workspace.visible_for.add(user.pk)
        for email in self.cleaned_data["editable_by"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                workspace.editable_by.add(user.pk)

        return workspace


class WorkspaceEditForm(WorkspaceForm):
    workspace_id = forms.CharField(required=True)
    name         = forms.CharField(required=True)
    visible_for  = forms.CharField(required=False)
    editable_by  = forms.CharField(required=False)


    class Meta:
        model = Workspace
        exclude = ("owner", "schedule", "schedule_archive",
                   "scheduled_compilation_id", "main_compilation_id", "main_compilation_archive_id")

    def __init__(self, *args, **kwargs):
        super(WorkspaceEditForm, self).__init__(*args, **kwargs)
        if self.initial:
            self.fields["workspaces"] = forms.ChoiceField(choices=get_workspaces(self.initial["user_id"]), required=True)

    def save(self, workspace, commit=True):
        edited_workspace = self.instance

        edited_workspace.owner = workspace.owner
        edited_workspace.workspace_id = workspace.workspace_id
        edited_workspace.schedule = workspace.schedule
        edited_workspace.schedule_archive = workspace.schedule_archive
        edited_workspace.scheduled_compilation_id = workspace.scheduled_compilation_id
        edited_workspace.main_compilation_id = workspace.main_compilation_id
        edited_workspace.main_compilation_archive_id = workspace.main_compilation_archive_id

        edited_workspace.editable_by.clear()
        edited_workspace.visible_for.clear()

        for email in self.cleaned_data["visible_for"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                edited_workspace.visible_for.add(user.pk)

        for email in self.cleaned_data["editable_by"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                edited_workspace.editable_by.add(user.pk)

        if commit:
            edited_workspace.save()

        return edited_workspace


class ScheduleForm(forms.ModelForm):
    workspace = forms.CharField(required=False)

    class Meta:
        model = Schedule
        fields = '__all__'

    def save(self, commit=True):
        schedule = self.instance
        if commit:
            schedule.save()

        return schedule


class EventCreateForm(forms.ModelForm):
    start_date = forms.DateTimeField(input_formats=["%d.%m.%Y %H:%M"], required=True)
    post_id = forms.CharField(required=True)

    def safe_copied_post(self, recipient_compilation_id):
        post_id = self.instance.post_id
        new_post_id = copy_post_to(post_id, recipient_compilation_id)
        self.instance.post_id = new_post_id

    def set_schedule(self, schedule):
        event = self.instance
        event.schedule = schedule
        self.instance = event

    class Meta:
        model = Event
        exclude = ('schedule', )


class EventEditForm(forms.ModelForm):
    start_date = forms.DateTimeField(input_formats=["%d.%m.%Y %H:%M"], required=True)

    # TODO: check and fix
    def save(self, commit=True):
        event = self.instance
        event.start_date = self.cleaned_data["start_date"]
        if commit:
            event.save()

        return event

    class Meta:
        model = Event
        exclude = ('post_id', 'schedule_id', )


class CompilationCreateForm(forms.Form):
    name                         = forms.CharField(required=True)
    resource                     = 'Tumbler'
    search_tag                   = forms.CharField(required=True)
    search_blogs                 = forms.CharField(required=False)
    downloaded_date              = str(datetime.now())

    print(f"search_tag: '{search_tag}'")
    search_tag  = 'paleontology'

    # TODO: check if its works
    storage                      = generate_storage_patch(PATH_TO_STORE, comp_id=id)
    post_ids                     = list()


class PostCreateForm(forms.Form):
    tags            = forms.CharField(required=False)
    text            = forms.CharField(widget=forms.Textarea(attrs={"rows":3, "cols":10}), required=False)
    images          = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    description     = forms.CharField(widget=forms.Textarea(attrs={"rows":3, "cols":10}), required=False)

    def save(self, workspace, compilation, images=None, commit=True):
        tags = list()
        for tag in self.data["tags"].split():
            tags.append(tag)

        post = Post.create(
            # information about original post
            blog_name             = " ",
            blog_url              = " ",
            original_post_url     = " ",
            posted_date           = str(datetime.now()),
            posted_timestamp      = datetime.now().timestamp(),
            tags                  = tags,
            text                  = str(self.data["text"]),
            compilation_id        = compilation.id,
            description           = str(self.data["description"])
        )

        if commit:
            if images:
                post_storage_path \
                    = os.path.join(PATH_TO_STORE, str(workspace.workspace_id), str(compilation.id), str(post.id))
                saved_file_addresses = save_files_from_request(post_storage_path, images)
                post.stored_file_urls = saved_file_addresses

            if compilation.post_ids is None:
                compilation.post_ids = [post.id]
            else:
                compilation.post_ids.append(post.id)
            compilation.update()

            post.save()

        return post


def get_workspaces(user_id):
    workspaces = Workspace.objects.filter(Q(owner=user_id) | Q(editable_by=user_id))
    choices = []

    for workspace in workspaces:
        choices.append((workspace.pk, workspace.name))

    return choices


