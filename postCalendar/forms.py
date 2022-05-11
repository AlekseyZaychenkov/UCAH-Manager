# -*- coding: utf-8 -*-
from django import forms
from postCalendar.models import Calendar, Event
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




class CalendarForm(forms.ModelForm):
    visible_for = forms.CharField(required=False)
    editable_by = forms.CharField(required=False)
    path = generate_storage_patch(PATH_TO_STORE, others='autocreated')
    compilation = create_compilation(resource=Compilation.calendarFormCreated, tag=None, blogs=None, storage=None)
    compilation_id = compilation.id

    class Meta:
        model = Calendar
        exclude = ("owner", "visible_for", "editable_by")

    def set_owner(self, user):
        calendar = self.instance
        calendar.owner_id = user.pk
        self.instance = calendar

    def save(self, commit=True):
        calendar = self.instance

        calendar.save()

        for email in self.cleaned_data["visible_for"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                calendar.visible_for.add(user.pk)
        for email in self.cleaned_data["editable_by"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                calendar.editable_by.add(user.pk)

        if commit:
            calendar.save()

        return calendar


def get_calendars(user_id):
    calendars = Calendar.objects.filter(Q(owner=user_id) | Q(editable_by=user_id))
    choices = []

    for calendar in calendars:
        choices.append((calendar.pk, calendar.name))

    return choices


class CalendarSettingsForm(CalendarForm):
    visible_for = forms.CharField(required=False)
    editable_by = forms.CharField(required=False)
    calendar_id = forms.CharField(required=True)

    class Meta:
        model = Calendar
        exclude = ("visible_for", "editable_by",)

    def __init__(self, *args, **kwargs):
        super(CalendarSettingsForm, self).__init__(*args, **kwargs)
        if self.initial:
            self.fields["calendars"] = forms.ChoiceField(choices=get_calendars(self.initial["user_id"]), required=True)


    def save(self, commit=True):
        calendar = Calendar.objects.get(calendar_id=self.cleaned_data["calendar_id"])
        calendar.name = self.cleaned_data["name"]
        calendar.editable_by.clear()
        calendar.visible_for.clear()

        for email in self.cleaned_data["visible_for"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                calendar.visible_for.add(user.pk)

        for email in self.cleaned_data["editable_by"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                calendar.editable_by.add(user.pk)

        if commit:
            calendar.save()

        return calendar


class EventCreateForm(forms.ModelForm):

    name = "EventCreateForm test"
    start_date = forms.DateTimeField(input_formats=["%d.%m.%Y %H:%M"], required=True)
    post_id = forms.CharField(required=True)
    # TODO: delete after wisualisation text and photos in calendar
    name = post_id

    def set_calendar(self, calendar_id):
        event = self.instance
        event.calendar_id = calendar_id
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
        exclude = ('calendar', 'end_date', 'event_type')


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
        exclude = ("calendar",)



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