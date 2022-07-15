from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from workspace_editor.forms import ScheduleForm, ScheduleSettingsForm, EventCreateForm, EventEditForm, CompilationCreateForm
from workspace_editor.models import Schedule
from workspace_editor.serializers import ScheduleSerializer
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
from .models import *
from .forms import *
import datetime

from loader.models import *

import requests



def get_events_for_schedule(selected_schedule_id):
    dates_to_events = dict()
    count = 0
    date = datetime.date.today()

    while (True):
        if Event.objects.filter(schedule_id=selected_schedule_id, start_date__year=date.year,
                                start_date__month=date.month, start_date__day=date.day).exists():
            events = Event.objects.filter(schedule_id=selected_schedule_id,start_date__year=date.year,
                                          start_date__month=date.month, start_date__day=date.day) \
                                                            .order_by('start_date')
            events_to_posts = dict()
            for event in events:
                events_to_posts[event] = PostEntry.objects.get(id=event.post_id)
            dates_to_events[date] = events_to_posts
        else:
            dates_to_events[date] = []

        date += datetime.timedelta(days=1)
        count += 1
        if count >= 6 and not Event.objects.filter(start_date__range=[date, date + datetime.timedelta(days=365)]).exists():
            break

    return dates_to_events


@login_required
def homeView(request):
    context = {}
    create_event_form = EventCreateForm()
    edit_event_form = EventEditForm()

    # Events stuff
    if "selected_schedule_id" in request.GET:
        selected_schedule_id = request.GET["selected_schedule_id"]
        first_schedule = True
    else:
        first_schedule = Schedule.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).first()
        if first_schedule:
            selected_schedule_id = first_schedule.schedule_id


    if request.POST:
        if request.POST['action'] == 'create':
            form = ScheduleForm(request.POST)
            if form.is_valid():
                form.set_owner(request.user)
                form.save()


        if request.POST['action'] == 'edit':
            form = ScheduleSettingsForm(request.POST)
            if form.is_valid():
                form.save(commit=True)


        if request.POST['action'] == 'delete':
            schedule = Schedule.objects.get(schedule_id=request.POST["schedule_id"])
            if schedule.owner == request.user:
                schedule.delete()
                first_schedule = Schedule.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).first()
                if first_schedule:
                    selected_schedule_id = first_schedule.schedule_id


        if request.POST['action'] == "create_event":
            form = EventCreateForm(request.POST)
            if form.is_valid():
                schedule = Schedule.objects.get(schedule_id=selected_schedule_id)
                form.safe_copied_post(schedule.scheduled_compilation_id)
                form.set_schedule(schedule)
                form.save()
                create_event_form = EventCreateForm()
            else:
                create_event_form = form


        if request.POST['action'] == "edit_event":
            form = EventEditForm(request.POST)
            if form.is_valid():
                form.save()
                edit_event_form = EventEditForm()
            else:
                edit_event_form = form


        if request.POST['action'] == 'create_compilation':
            form = CompilationCreateForm(request.POST)
            if form.is_valid():
                 form.save()


        # if request.POST['action'] == 'edit_compilation':
        #     form = CompilationForm(request.POST)
        #     if form.is_valid():
        #         form.save(commit=True)
        #
        # if request.POST['action'] == 'delete_compilation':
        #     schedule = Compilation.objects.get(id=request.POST["compilation_id"])
        #     if schedule:
        #         schedule.delete()
        #         print("Getting firstCompilation")
        #         firstCompilation = Compilation.objects.limit(0)[0]
        #         print(f"firstCompilation: '{firstCompilation}'")
        #         if firstCompilation:
        #             selected_compilation_id = firstCompilation.id





    # schedule stuff
    queryset_visible = Schedule.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user))
    queryset_editable = Schedule.objects.filter(Q(owner=request.user.pk) | Q(editable_by=request.user))
    context["schedules"] = ScheduleSerializer(queryset_editable, many=True).data

    context["createform"] = ScheduleForm()
    context["settingsform"] = ScheduleSettingsForm(initial={"user_id": request.user.pk, "owner": request.user})
    context["my_schedules"] = queryset_visible

    # TODO: make table compilationsOwners with compilation_id, owner and visible_for for looking for
    #  only current user compilations
    context["my_compilations"] = Compilation.objects.all()

    if first_schedule:
        context["schedule_events"] = get_events_for_schedule(selected_schedule_id)
        context["selected_schedule_id"] = int(selected_schedule_id)
    context["event_createform"] = create_event_form
    context["event_editform"] = edit_event_form


    all_post_entries = PostEntry.objects.all()
    # TODO: change number of items and make slider
    paginator = Paginator(all_post_entries, 8)

    page_number = request.GET.get('page')
    post_list = paginator.get_page(page_number)
    context['post_list'] = post_list





    return render(request, "home.html", context)
