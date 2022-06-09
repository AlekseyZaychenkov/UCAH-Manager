from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from workspace_editor.forms import ScheduleForm, ScheduleSettingsForm, EventCreateForm, EventEditForm, CompilationCreateForm
from workspace_editor.models import Schedule
from workspace_editor.serializers import ScheduleSerializer, EventSerializer
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

from loader.models import *

import requests



def getEventsForSchedule(selected_schedule):
    print(f"selected_schedule: {str(selected_schedule)}")

    schedule = Schedule.objects.get(schedule_id=selected_schedule)
    print(f"schedule: {str(schedule)}")

    serializedEvents = EventSerializer(schedule.event_set.all(), many=True).data
    print(f"serializedEvents: {str(serializedEvents)}")
    return serializedEvents


@login_required
def homeView(request):
    context = {}
    createEventForm = EventCreateForm()
    editEventForm = EventEditForm()

    # Events stuff
    if "selected_schedule" in request.GET:
        selected_schedule = request.GET["selected_schedule"]
        first_schedule = True
    else:
        first_schedule = Schedule.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).first()
        if first_schedule:
            selected_schedule = first_schedule.schedule_id

    # TODO: make table compilationsOwners with compilation_id, owner and visible_for for looking for
    #  only current user compilations
    if "selected_compilation" in request.GET:
        selected_compilation = request.GET["selected_compilation"]
        firstCompilation = True
    else:
        firstCompilation = Compilation.objects.limit(0)[0]
        if firstCompilation:
            selected_compilation = firstCompilation.id

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
                    selected_schedule = first_schedule.schedule_id

        if request.POST['action'] == "create_event":
            #  TODO: check if post already added in target compilation
            #   and hide from source complilation if it was
            form = EventCreateForm(request.POST)
            if form.is_valid():
                print(f"form.is_valid()")
                print(f"form: {form}")
                form.set_schedule(selected_schedule)
                form.copy_post_to_compilation(selected_compilation)
                form.save()
                createEventForm = EventCreateForm()
            else:
                print(f"form.is_NOT_valid()")
                print(f"form: {form}")
                createEventForm = form

        if request.POST['action'] == "edit_event":
            form = EventEditForm(request.POST)
            if form.is_valid():
                form.save()
                editEventForm = EventEditForm()
            else:
                editEventForm = form


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
        #             selected_compilation = firstCompilation.id





    # schedule stuff
    queryset_visible = Schedule.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user))
    queryset_editable = Schedule.objects.filter(Q(owner=request.user.pk) | Q(editable_by=request.user))
    context["schedules"] = ScheduleSerializer(queryset_editable, many=True).data

    context["createform"] = ScheduleForm()
    context["settingsform"] = ScheduleSettingsForm(initial={"user_id": request.user.pk, "owner": request.user})
    context["my_schedule"] = queryset_visible

    # TODO: make table compilationsOwners with compilation_id, owner and visible_for for looking for
    #  only current user compilations
    context["my_compilations"] = Compilation.objects.all()

    if first_schedule:
        context["scheduled_posts"] = getEventsForSchedule(selected_schedule)
        context["selected_schedule"] = int(selected_schedule)
    context["event_createform"] = createEventForm
    context["event_editform"] = editEventForm

    # TODO: get posts only from one compilation
    all_post_entries = PostEntry.objects.all()

    # TODO: change number of items and make slider
    paginator = Paginator(all_post_entries, 8)
    page_number = request.GET.get('page')
    post_list = paginator.get_page(page_number)
    context['post_list'] = post_list

    # schedule_post_list


    return render(request, "home.html", context)
