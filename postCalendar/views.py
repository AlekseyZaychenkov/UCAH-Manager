from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from postCalendar.forms import CalendarForm, CalendarSettingsForm, EventCreateForm, EventEditForm, CompilationCreateForm
from postCalendar.models import Calendar
from postCalendar.serializers import CalendarSerializer\
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



def getPostsForCalender(selected_calendar):
    posts = list()
    calendar = Calendar.objects.get(calendar_id=selected_calendar)
    compilation = Compilation.objects.get(id=calendar.compilation_id)
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
    if "selected_calendar" in request.GET:
        selected_calendar = request.GET["selected_calendar"]
        firstCalendar = True
    else:
        firstCalendar = Calendar.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).first()
        if firstCalendar:
            selected_calendar = firstCalendar.calendar_id

    # TODO: make table compilationsOwners with compilation_id, owner and visible_for for looking for
    #  only current user compilations
    if "selected_compilation_id" in request.GET:
        selected_compilation_id = request.GET["selected_compilation_id"]
        firstCompilation = True
    else:
        print("Getting firstCompilation")
        firstCompilation = Compilation.objects.limit(0)[0]
        print(f"firstCompilation: '{firstCompilation}'")
        if firstCompilation:
            selected_compilation_id = firstCompilation.id


    if request.POST:
        if request.POST['action'] == 'create':
            form = CalendarForm(request.POST)
            if form.is_valid():
                form.set_owner(request.user)
                form.save()




        if request.POST['action'] == 'edit':
            form = CalendarSettingsForm(request.POST)
            if form.is_valid():
                form.save(commit=True)

        if request.POST['action'] == 'delete':
            calendar = Calendar.objects.get(calendar_id=request.POST["calendar_id"])
            if calendar.owner == request.user:
                calendar.delete()
                firstCalendar = Calendar.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).first()
                if firstCalendar:
                    selected_calendar = firstCalendar.calendar_id

        if request.POST['action'] == "create_event":
            form = EventCreateForm(request.POST)
            if form.is_valid():
                print("create_event form.is_valid()")
                form.set_calendar(selected_calendar)
                form.add_to_compilation(selected_calendar)
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
        #     calendar = Compilation.objects.get(id=request.POST["compilation_id"])
        #     if calendar:
        #         calendar.delete()
        #         print("Getting firstCompilation")
        #         firstCompilation = Compilation.objects.limit(0)[0]
        #         print(f"firstCompilation: '{firstCompilation}'")
        #         if firstCompilation:
        #             selected_compilation_id = firstCompilation.id





    # calendar stuff
    queryset_visible = Calendar.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user))
    queryset_editable = Calendar.objects.filter(Q(owner=request.user.pk) | Q(editable_by=request.user))
    context["calendars"] = CalendarSerializer(queryset_editable, many=True).data

    context["createform"] = CalendarForm()
    context["settingsform"] = CalendarSettingsForm(initial={"user_id": request.user.pk, "owner": request.user})
    context["my_calendars"] = queryset_visible

    # TODO: make table compilationsOwners with compilation_id, owner and visible_for for looking for
    #  only current user compilations
    context["my_compilations"] = Compilation.objects.all()

    if firstCalendar:
        context["schedule_posts"] = getPostsForCalender(selected_calendar)
        context["selected_calendar"] = int(selected_calendar)
    context["event_createform"] = createEventForm
    context["event_editform"] = editEventForm


    all_post_entries = PostEntry.objects.all()
    # TODO: change number of items and make slider
    paginator = Paginator(all_post_entries, 8)

    page_number = request.GET.get('page')
    post_list = paginator.get_page(page_number)
    context['post_list'] = post_list





    return render(request, "home.html", context)
