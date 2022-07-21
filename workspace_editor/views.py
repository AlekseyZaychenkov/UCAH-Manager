from django.contrib.auth.decorators import login_required
import logging

from workspace_editor.forms import ScheduleForm, EventCreateForm, EventEditForm, CompilationCreateForm
from workspace_editor.models import Workspace
from workspace_editor.serializers import WorkspaceSerializer
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse

from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.http import JsonResponse
from .models import *
import calendar
from .forms import *
import datetime

from loader.models import *

log = logging.getLogger(__name__)



@login_required
def home(request):

    workspace = None
    schedule = None
    create_event_form = None
    edit_event_form = None
    first_workspace = None
    workspace_id = None
    if 'workspace_id' in request.GET:
        workspace_id = int(request.GET['workspace_id'])


    # Events stuff
    if workspace_id and Workspace.objects.filter(workspace_id=workspace_id) \
            .filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).exists():
        workspace = Workspace.objects.get(workspace_id=workspace_id)
    elif workspace_id is not None:
        log.warning(f"Workspace with id workspace_id={workspace_id} doesn't exists or you don't have access to it")
    else:
        log.info(f"You don't have available workspaces")
        first_workspace = Workspace.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).first()
        if first_workspace:
            workspace_id = first_workspace.workspace_id
            workspace = Workspace.objects.get(workspace_id=workspace_id)

    if workspace:
        schedule = Schedule.objects.get(schedule_id=workspace.schedule_id)


    if request.POST:
        if request.POST['action'] == 'create':
            form = WorkspaceForm(request.POST)

            if form.is_valid():
                form.set_owner(request.user)
                workspace = form.save()

                schedule = Schedule(workspace = workspace)
                schedule.save()
                workspace.schedule_id = schedule.schedule_id

                schedule_archive = ScheduleArchive(workspace = workspace)
                schedule_archive.save()
                workspace.schedulearchive_id = schedule_archive.schedule_id

                workspace.save()
            else:
                log.error(form.errors.as_data())


        elif workspace and request.POST['action'] == 'edit':
            form = WorkspaceSettingsForm(request.POST)
            if form.is_valid():
                form.save(commit=True)
            else:
                log.error(form.errors.as_data())


        elif workspace and request.POST['action'] == 'delete':
            workspace = Workspace.objects.get(workspace_id=request.POST["workspace_id"])
            if workspace.owner == request.user:
                workspace.delete()
                first_workspace = Workspace.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).first()
                if first_workspace:
                    workspace_id = first_workspace.workspace_id


        elif workspace and request.POST['action'] == "create_event":
            form = EventCreateForm(request.POST)
            if form.is_valid():
                form.safe_copied_post(workspace.scheduled_compilation_id)
                form.set_schedule(schedule)
                form.save()
                create_event_form = EventCreateForm()
            else:
                log.error(form.errors.as_data())
                create_event_form = form


        elif workspace and request.POST['action'] == "edit_event":
            form = EventEditForm(request.POST)
            if form.is_valid():
                form.save()
                edit_event_form = EventEditForm()
            else:
                log.error(form.errors.as_data())
                edit_event_form = form


        elif workspace and request.POST['action'] == 'create_compilation':
            form = CompilationCreateForm(request.POST)
            if form.is_valid():
                 form.save()
            else:
                log.error(form.errors.as_data())

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


    context = prepare_context(request, schedule, create_event_form, edit_event_form, workspace_id)


    return render(request, "workspace.html", context)


def prepare_context(request, schedule, create_event_form, edit_event_form, workspace_id):
    context = {}

    queryset_visible = Workspace.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user))
    context["my_workspaces"] = queryset_visible

    queryset_editable = Workspace.objects.filter(Q(owner=request.user.pk) | Q(editable_by=request.user))
    context["workspaces"] = WorkspaceSerializer(queryset_editable, many=True).data

    context["createform"] = WorkspaceForm()

    context["selected_workspace_id"] = workspace_id

    if schedule:
        context["settingsform"] = WorkspaceSettingsForm(initial={"user_id": request.user.pk, "owner": request.user})

        # TODO: make table compilationsOwners with compilation_id, owner and visible_for for looking for
        #  only current user compilations
        context["my_compilations"] = Compilation.objects.all()
        context["schedule_events"] = get_events_for_schedule(schedule.schedule_id)
        context["selected_schedule_id"] = int(schedule.schedule_id)
        if create_event_form:
            context["event_createform"] = create_event_form
        if create_event_form:
            context["edit_event_form"] = edit_event_form

        all_post_entries = Post.objects.all()
        # TODO: change number of items and make slider
        paginator = Paginator(all_post_entries, 8)

        page_number = request.GET.get('page')
        post_list = paginator.get_page(page_number)
        context['post_list'] = post_list

    return context


def get_events_for_schedule(selected_schedule_id):
    dates_to_events = dict()
    count = 0
    date = datetime.date.today()
    days_to_show = 7

    while (True):
        day_of_week = calendar.day_name[date.weekday()]

        if Event.objects.filter(schedule_id=selected_schedule_id, start_date__year=date.year,
                                start_date__month=date.month, start_date__day=date.day).exists():
            events = Event.objects.filter(schedule_id=selected_schedule_id, start_date__year=date.year,
                                          start_date__month=date.month, start_date__day=date.day) \
                .order_by('start_date')
            events_to_posts = dict()
            for event in events:
                events_to_posts[event] = Post.objects.get(id=event.post_id)

            dates_to_events[(date, day_of_week)] = events_to_posts
        else:
            dates_to_events[(date, day_of_week)] = []

        date += datetime.timedelta(days=1)
        count += 1
        if count >= days_to_show \
                and not Event.objects.filter(start_date__range=[date, date + datetime.timedelta(days=365)]).exists():
            break

    return dates_to_events
