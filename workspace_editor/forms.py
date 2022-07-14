# -*- coding: utf-8 -*-
from django import forms

from workspace_editor.utils import copy_post_to
from workspace_editor.models import Schedule, Event
from account.models import Account
from django.db.models import Q
from UCA_Manager.settings import PATH_TO_STORE

from datetime import datetime

from loader.utils import generate_storage_patch, create_empty_compilation



class ScheduleForm(forms.ModelForm):
    visible_for = forms.CharField(required=False)
    editable_by = forms.CharField(required=False)
    scheduled_compilation_id = create_empty_compilation().id
    main_compilation_id = create_empty_compilation().id
    main_compilation_archive_id = create_empty_compilation().id

    class Meta:
        model = Schedule
        exclude = ("owner", "visible_for", "editable_by",
                   "scheduled_compilation_id", "main_compilation_id", "main_compilation_archive_id")

    def set_owner(self, user):
        schedule = self.instance
        schedule.owner_id = user.pk
        self.instance = schedule

    def save(self, commit=True):
        schedule = self.instance
        schedule.scheduled_compilation_id = create_empty_compilation().id
        schedule.main_compilation_id = create_empty_compilation().id
        schedule.main_compilation_archive_id = create_empty_compilation().id
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

    def safe_copied_post(self, recipient_compilation_id):
        post_id = self.instance.post_id
        print(f"post_id: {post_id}")
        new_post_id = copy_post_to(post_id, recipient_compilation_id)
        self.instance.post_id = new_post_id

    def set_schedule(self, schedule):
        event = self.instance
        print(f"schedule: {schedule}")
        event.schedule = schedule
        self.instance = event
        # schedule = Schedule.objects.get(schedule_id=schedule_id)
        # event_id = event.event_id
        # print(f"schedule: {schedule}")
        # print(f"event_id: {event_id}")
        # print(f"event.event_id: {event.event_id}")
        # print(f"schedule.event_id: {schedule.event_id}")
        # schedule.event_id = event_id

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


def get_schedules(user_id):
    schedules = Schedule.objects.filter(Q(owner=user_id) | Q(editable_by=user_id))
    choices = []

    for schedule in schedules:
        choices.append((schedule.pk, schedule.name))

    return choices
