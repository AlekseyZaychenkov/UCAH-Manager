# -*- coding: utf-8 -*-
from django import forms

from workspace_editor.utils import copy_post_to
from workspace_editor.models import Workspace, Event, Schedule
from account.models import Account
from django.db.models import Q
from UCA_Manager.settings import PATH_TO_STORE

from datetime import datetime

from loader.utils import generate_storage_patch, create_empty_compilation



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
    print(f"EventCreateForm: start_date {str(start_date)}")

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


    # def set_compilation(self, compilation_id):
    #     compilation = self.instance
    #     compilation.id = compilation_id
    #     self.instance = event
    #
    # class Meta:
    #     model = Compilation
    #     exclude = ('resource',)


        # compilation = Compilation.create(
        #     name                         = 'Test',
        #     resource                     = 'Tumbler',
        #     search_tag                   = tag,
        #     search_blogs                 = blogs,
        #     downloaded_date              = str(datetime.now()),
        #     storage                      = storagePath,
        #
        #     post_ids                     = list()
        # )


class CompilationCreateForm(forms.Form):

    name                         = forms.CharField(required=True)
    # TODO: remove hardcode
    resource                     = 'Tumbler'
    search_tag                   = forms.CharField(required=True)
    search_blogs                 = forms.CharField(required=False)
    downloaded_date              = str(datetime.now())

    print(f"search_tag: '{search_tag}'")
    # TODO: remove hardcode
    search_tag  = 'paleontology'

    # TODO: check if its works
    storage                      = generate_storage_patch(PATH_TO_STORE, comp_id=id)
    post_ids                     = list()


    # def set_compilation(self, compilation_id):
    #     compilation = self.instance
    #     compilation.id = compilation_id
    #     self.instance = event
    #
    # class Meta:
    #     model = Compilation
    #     exclude = ('resource',)


        # compilation = Compilation.create(
        #     name                         = 'Test',
        #     resource                     = 'Tumbler',
        #     search_tag                   = tag,
        #     search_blogs                 = blogs,
        #     downloaded_date              = str(datetime.now()),
        #     storage                      = storagePath,
        #
        #     post_ids                     = list()
        # )


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


    # def set_compilation(self, compilation_id):
    #     compilation = self.instance
    #     compilation.id = compilation_id
    #     self.instance = event
    #
    # class Meta:
    #     model = Compilation
    #     exclude = ('resource',)


def get_workspaces(user_id):
    workspaces = Workspace.objects.filter(Q(owner=user_id) | Q(editable_by=user_id))
    choices = []

    for workspace in workspaces:
        choices.append((workspace.pk, workspace.name))

    return choices
