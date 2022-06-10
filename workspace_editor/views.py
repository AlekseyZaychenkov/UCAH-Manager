from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from workspace_editor.forms import ScheduleForm, ScheduleSettingsForm, EventCreateForm, EventEditForm, CompilationCreateForm
from workspace_editor.models import Schedule
from workspace_editor.serializers import ScheduleSerializer\
    # , PostSerializer
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



def getPostsForCalender(selected_schedule):
    posts = list()
    schedule = Schedule.objects.get(schedule_id=selected_schedule)
    # TODO: (hard) investigate, why compilation.id from cassandra could be saved to saved to schedule.compilation_id with different encoding
    if not schedule.compilation_id:
        comp_id = createCompilation().id
        schedule.compilation_id = comp_id
    compilation = Compilation.objects.get(id=schedule.compilation_id)

    if compilation:
        post_ids = compilation.post_ids
        for id in post_ids:
            posts.append(PostEntry.objects.get(id=id))

    return posts


@login_required
def homeView(request):
    context = {}
    createEventForm = EventCreateForm()
    editEventForm = EventEditForm()

    # Events stuff
    if "selected_schedule" in request.GET:
        selected_schedule = request.GET["selected_schedule"]
        firstSchedule = True
    else:
        firstSchedule = Schedule.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).first()
        if firstSchedule:
            selected_schedule = firstSchedule.schedule_id
            firstSchedule.compilation_id = createCompilation().id
            # TODO: (hard) investigate, why compilation.id from cassandra could be saved to saved to schedule.compilation_id with different encoding





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
                firstschedule = Schedule.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).first()
                if firstSchedule:
                    selected_schedule = firstSchedule.schedule_id

        if request.POST['action'] == "create_event":
            form = EventCreateForm(request.POST)
            if form.is_valid():
                print("create_event form.is_valid()")
                form.set_schedule(selected_schedule)
                form.add_to_compilation(selected_schedule)
                form.save()
                createEventForm = EventCreateForm()
            else:
                createEventForm = form
                print("create_event form.is NOT valid()")

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

    if firstSchedule:
        context["schedule_posts"] = getPostsForCalender(selected_schedule)
        context["selected_schedule"] = int(selected_schedule)
    context["event_createform"] = createEventForm
    context["event_editform"] = editEventForm


    all_post_entries = PostEntry.objects.all()
    # TODO: change number of items and make slider
    paginator = Paginator(all_post_entries, 8)

    page_number = request.GET.get('page')
    post_list = paginator.get_page(page_number)
    context['post_list'] = post_list





    return render(request, "home.html", context)
