# -*- coding: utf-8 -*-
from django import forms
from workspace_editor.models import Schedule, Event
from account.models import Account
from django.db.models import Q
from loader.models import Compilation
from loader import tumblr_loader
from loader.tests.test_tumblr_loader import Test_TumblrLoader
from UCA_Manager.settings import PATH_TO_STORE

from datetime import datetime

from loader.utils import generate_storage_patch
from loader.utils import create_compilation
from workspace_editor.utils import copy_post_to_compilation


class ScheduleForm(forms.ModelForm):
    visible_for = forms.CharField(required=False)
    editable_by = forms.CharField(required=False)

    class Meta:
        model = Schedule
        exclude = ("owner", "visible_for", "editable_by")

    def set_owner(self, user):
        schedule = self.instance
        schedule.owner_id = user.pk
        self.instance = schedule

    def save(self, commit=True):
        schedule = self.instance
        schedule.compilation_id = createCompilation().id
        schedule.save()

        for email in self.cleaned_data["visible_for"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                schedule.visible_for.add(user.pk)
        for email in self.cleaned_data["editable_by"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                schedule.editable_by.add(user.pk)

        if commit:
            schedule.save()

        return schedule


def get_schedules(user_id):
    schedules = Schedule.objects.filter(Q(owner=user_id) | Q(editable_by=user_id))
    choices = []

    for schedule in schedules:
        choices.append((schedule.pk, schedule.name))

    return choices


class ScheduleSettingsForm(ScheduleForm):
    visible_for = forms.CharField(required=False)
    editable_by = forms.CharField(required=False)
    schedule_id = forms.CharField(required=True)

    class Meta:
        model = Schedule
        exclude = ("visible_for", "editable_by",)

    def __init__(self, *args, **kwargs):
        super(ScheduleSettingsForm, self).__init__(*args, **kwargs)
        if self.initial:
            self.fields["schedules"] = forms.ChoiceField(choices=get_schedules(self.initial["user_id"]), required=True)

    def save(self, commit=True):
        schedule = Schedule.objects.get(schedule_id=self.cleaned_data["schedule_id"])
        schedule.compilation_id = createCompilation().id
        schedule.name = self.cleaned_data["name"]
        schedule.editable_by.clear()
        schedule.visible_for.clear()

        for email in self.cleaned_data["visible_for"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                schedule.visible_for.add(user.pk)

        for email in self.cleaned_data["editable_by"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                schedule.editable_by.add(user.pk)

        if commit:
            schedule.save()

        return schedule


class EventCreateForm(forms.ModelForm):

    name = 'EventCreateForm test'
    start_date = forms.DateTimeField(input_formats=["%d.%m.%Y %H:%M"], required=True)
    post_id = forms.CharField(required=True)
    print(f"EventCreateForm: start_date {start_date}")


    def set_schedule(self, schedule_id):
        event = self.instance
        event.schedule_id = schedule_id
        self.instance = event

    def add_to_compilation(self, schedule_id):
        schedule = Schedule.objects.get(schedule_id=schedule_id)
        post_id = self.instance.post_id
        copy_post_to_compilation(schedule.compilation_id, post_id, True)

    class Meta:
        model = Event
        exclude = ('schedule', 'end_date', 'event_type')


class EventEditForm(forms.ModelForm):

    start_date = forms.DateTimeField(input_formats=["%d.%m.%Y %H:%M"], required=True)
    end_date = forms.DateTimeField(input_formats=["%d.%m.%Y %H:%M"], required=False)
    event_id = forms.CharField(required=True)

    def save(self, commit=True):
        event = Event.objects.get(event_id=self.cleaned_data["event_id"])
        event.name = self.cleaned_data["name"]
        event.start_date = self.cleaned_data["start_date"]
        event.end_date = self.cleaned_data["end_date"]
        event.event_type = self.cleaned_data["event_type"]
        if commit:
            event.save()

        return event

    class Meta:
        model = Event
        exclude = ("schedule",)


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


    storage                      = generate_storage_patch(PATH_TO_STORE, tags=search_tag)
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


    storage                      = generate_storage_patch(PATH_TO_STORE, tags=search_tag)
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


    storage                      = generate_storage_patch(PATH_TO_STORE, tags=search_tag)
    post_ids                     = list()


    # def set_compilation(self, compilation_id):
    #     compilation = self.instance
    #     compilation.id = compilation_id
    #     self.instance = event
    #
    # class Meta:
    #     model = Compilation
    #     exclude = ('resource',)


def createCompilation():
    path = generate_storage_patch(PATH_TO_STORE, others='autocreated')
    return create_compilation(resource='Created bu user', tag=None, blogs=None, storage=path)
