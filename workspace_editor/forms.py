# -*- coding: utf-8 -*-
from django import forms
from workspace_editor.models import Schedule, Event
from account.models import Account
from django.db.models import Q
from loader.models import Compilation
from loader import tumblr_loader
from loader.models import PostEntry
from loader.utils import generate_storage_patch
from loader.utils import create_compilation
from loader.tests.test_tumblr_loader import Test_TumblrLoader
from UCA_Manager.settings import PATH_TO_STORE

from datetime import datetime




class ScheduleForm(forms.ModelForm):
    visible_for = forms.CharField(required=False)
    editable_by = forms.CharField(required=False)
    path = generate_storage_patch(PATH_TO_STORE, others='autocreated')
    compilation = create_compilation(resource=Compilation.scheduleFormCreated, tag=None, blogs=None, storage=None)
    compilation_id = compilation.id

    class Meta:
        model = Schedule
        exclude = ("owner", "visible_for", "editable_by")

    def set_owner(self, user):
        schedule = self.instance
        schedule.owner_id = user.pk
        self.instance = schedule

    def save(self, commit=True):
        schedule = self.instance

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

    name = "EventCreateForm test"
    start_date = forms.DateTimeField(input_formats=["%d.%m.%Y %H:%M"], required=True)
    post_id = forms.CharField(required=True)
    # TODO: delete after wisualisation text and photos in schedule
    name = post_id
    print(f"post_id: {post_id}")

    def set_schedule(self, schedule_id):
        event = self.instance
        event.schedule_id = schedule_id
        self.instance = event

    # TODO: figure out where better to place such methods
    def copy_post_to_compilation(self, comp_id):
        event = self.instance
        epi = event.post_id
        print(f"epi: {epi}")
        old_pe = PostEntry.objects.get(epi)
        savedFileAddresses = self.save_files(storagePath, file_urls) if storagePath is not None else None

        new_pe = PostEntry.create(
            # information about original post
            blog_name             = old_pe.blog_name,
            blog_url              = old_pe.blog_url,
            id_in_social_network  = old_pe.id_in_social_network,
            url                   = old_pe.url,
            posted_date           = old_pe.posted_date,
            posted_timestamp      = old_pe.posted_timestamp,
            tags                  = old_pe.tags,
            text                  = old_pe.text,
            file_urls             = old_pe.file_urls,

            # information about search query parameters
            compilation_id        = comp_id,

            # information for posting
            stored_file_urls      = old_pe.stored_file_urls,
            external_link_urls    = old_pe.external_link_urls,

            # information for administration notes and file storing
            description           = old_pe.description
        )
        new_comp = Compilation.get(comp_id)
        if new_comp.post_ids is None:
            new_comp.post_ids = [new_pe.id]
        else:
            new_comp.post_ids.append(new_pe.id)

        if old_pe.copied_in_compilations is None:
            old_pe.copied_in_compilations = [new_comp.id]
        else:
            old_pe.copied_in_compilations.append(new_comp.id)




    class Meta:
        model = Event
        exclude = ('name', 'schedule', 'end_date', 'event_type')


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



class CompilationCreateForm(forms.Form):
    name                         = forms.CharField(required=True)
    # TODO: de-hardcode after adding second loader
    resource                     = 'Tumbler'
    search_tag                   = forms.CharField(required=True)
    search_blogs                 = forms.CharField(required=False)
    downloaded_date              = str(datetime.now())
    print(f"search_tag: '{search_tag}'")
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