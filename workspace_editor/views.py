from django.contrib.auth.decorators import login_required
import logging

from workspace_editor.forms import EventCreateForm, EventEditForm, CompilationCreateForm
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
from loader.utils import delete_dir

from loader.models import *

log = logging.getLogger(__name__)



@login_required
def home(request, workspace_id=None, post_id=None):
    workspace = __workspace_choice(request, workspace_id)

    if request.POST:
        workspace = __workspace_request_handler(request, workspace)

        if workspace:
            schedule = Schedule.objects.get(schedule_id=int(workspace.schedule_id))
            __event_request_handler(request, workspace, schedule)
            __post_request_handler(request, workspace, post_id)

        return redirect(f'workspace_by_id', workspace_id=workspace.workspace_id)


    context = __prepare_workspace_context(request, workspace, post_id)

    return render(request, "workspace.html", context)


def downloading(request, workspace_id=None, post_id=None):
    workspace = __workspace_choice(request, workspace_id)

    if request.POST:
        workspace = __workspace_request_handler(request, workspace)

        if workspace:
            schedule = Schedule.objects.get(schedule_id=int(workspace.schedule_id))
            __event_request_handler(request, workspace, schedule)
            __post_request_handler(request, workspace, post_id)
            __compilation_request_handler(request, workspace)

        return redirect(f'downloading_workspace_by_id', workspace_id=workspace.workspace_id)

    context = __prepare_downloading_context(request, workspace, post_id)

    return render(request, "downloading.html", context)


def __workspace_choice(request, workspace_id=None):
    workspace = None

    if 'workspace_id' in request.GET:
        workspace_id = int(request.GET['workspace_id'])

    if workspace_id and Workspace.objects.filter(workspace_id=workspace_id) \
            .filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).exists():
        workspace = Workspace.objects.get(workspace_id=workspace_id)

    elif workspace_id is None and Workspace.objects \
            .filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).exists():
        first_workspace = Workspace.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).first()
        workspace = first_workspace
        log.warning(f"Redirect to first available workspace")
        return redirect(f'workspace_by_id', workspace_id=workspace.workspace_id)

    elif workspace_id is not None and not Workspace.objects \
            .filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).exists():
        log.warning(f"Workspace with id workspace_id={workspace_id} doesn't exists or you don't have access to it")

    else:
        log.info(f"You don't have available workspaces")

    return workspace

def __workspace_request_handler(request, workspace=None):
    if request.POST['action'] == 'create':
        form = WorkspaceCreateForm(request.POST)
        if form.is_valid():
            form.set_owner(request.user)
            schedule = Schedule()
            schedule.save()
            schedule_archive = ScheduleArchive()
            schedule_archive.save()
            form.set_schedules(schedule, schedule_archive)
            workspace = form.save()
        else:
            log.error(form.errors.as_data())

    elif workspace and request.POST['action'] == 'edit':
        form = WorkspaceEditForm(request.POST)
        if form.is_valid():
            workspace = Workspace.objects.get(workspace_id=form.data['workspace_id'])
            form.save_edited_workspace(workspace)
        else:
            log.error(form.errors.as_data())

    elif workspace and request.POST['action'] == 'delete':
        workspace = Workspace.objects.get(workspace_id=request.POST["workspace_id"])
        if workspace.owner == request.user:
            workspace.delete()
            workspace = __workspace_choice(request)

    return workspace


def __compilation_request_handler(request, workspace):
    if request.POST['action'] == 'create_compilation':
        form = CompilationHolderCreateForm(request.POST)
        if form.is_valid():
            form.set_workspace(workspace)
            form.save()
        else:
            log.error(form.errors.as_data())


def __event_request_handler(request, workspace, schedule):
    if request.POST['action'] == "create_event":
        form = EventCreateForm(request.POST)
        if form.is_valid():
            form.safe_copied_post(workspace.scheduled_compilation_id)
            form.set_schedule(schedule)
            form.save()
        else:
            log.error(form.errors.as_data())

    elif request.POST['action'] == "edit_event":
        form = EventEditForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            log.error(form.errors.as_data())

def __post_request_handler(request, workspace, post_id=None):
    if request.POST['action'] == 'create_post':
        form = PostCreateForm(request.POST)
        if form.is_valid():
            compilation = Compilation.objects.get(id=workspace.main_compilation_id)
            form.save(workspace=workspace, compilation=compilation, images=request.FILES.getlist('images'))
        else:
            log.error(form.errors.as_data())

    elif post_id and request.POST['action'] == 'delete_post':
        form = PostDeleteForm(request.POST)
        if form.is_valid():
            form.delete()
        else:
            log.error(form.errors.as_data())


def __prepare_workspace_context(request, workspace=None, post_id=None):
    context = __prepare_mutual_context(request, workspace, post_id)
    return context


def __prepare_downloading_context(request, workspace=None, post_id=None):
    context = __prepare_mutual_context(request, workspace, post_id)

    if workspace:
        context['compilation_create_form'] = CompilationHolderCreateForm()
        context['compilation_edit_form']   = CompilationHolderCreateForm()

        holders = CompilationHolder.objects.filter(workspace=workspace.workspace_id).order_by('number_on_list')

        holder_to_posts = dict()
        for holder in holders:
            compilation = Compilation.objects.get(id=holder.compilation_id)
            post_ids = compilation.post_ids
            posts = []
            for id in post_ids:
                posts.append(Post.objects.get(id=id))
            holder_to_posts[holder] = posts
        context['holder_to_posts'] = holder_to_posts

        holder_indexes = []
        count = 1
        for holder in holders:
            holder_indexes.append(count)
            count += 1
        context['holder_indexes'] = holder_indexes


    return context


# TODO: investigate and move part of methods to __prepare_workspace_context()
def __prepare_mutual_context(request, workspace=None, post_id=None):
    context = {}

    context["resources"] = RESOURCES

    queryset_visible = Workspace.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user))
    # TODO: rename to visible_workspaces
    context["my_workspaces"] = queryset_visible

    queryset_editable = Workspace.objects.filter(Q(owner=request.user.pk) | Q(editable_by=request.user))
    # TODO: rename to editable_workspaces
    context["workspaces"] = WorkspaceSerializer(queryset_editable, many=True).data

    context["create_form"] = WorkspaceCreateForm()
    context["edit_form"] = WorkspaceEditForm(initial={"user_id": request.user.pk, "owner": request.user})

    context["selected_workspace_id"] = workspace.workspace_id
    context["workspace"] = workspace


    if workspace:
        schedule = Schedule.objects.get(schedule_id=int(workspace.schedule_id))

        # TODO: make table compilationsOwners with compilation_id, owner and visible_for for looking for
        #  only current user compilations
        context["my_compilations"] = Compilation.objects.all()
        context["schedule_events"] = __get_events_for_schedule(schedule.schedule_id)
        context["selected_schedule_id"] = int(schedule.schedule_id)

        # TODO: rename event_createform to event_create_form
        context["event_create_form"] = EventCreateForm()
        # TODO: rename event_edit_form to event_create_form
        context["edit_event_form"] = EventEditForm()
        context["post_create_form"] = PostCreateForm()

        context["post_delete_form"] = PostDeleteForm()


        main_compilation = Compilation.objects.get(id=uuid.UUID(workspace.main_compilation_id))
        post_ids = main_compilation.post_ids
        posts = list()
        for id in post_ids:
            posts.append(Post.objects.get(id=id))

        # TODO: make slider
        paginator = Paginator(posts, 6)

        page_number = request.GET.get('page')
        main_compilation = paginator.get_page(page_number)
        context["main_compilation"] = main_compilation

        context["selected_post_id"] = post_id



    return context


def __get_events_for_schedule(selected_schedule_id):
    dates_to_events = dict()
    count = 0
    date = datetime.date.today()
    days_to_show = 7

    while (True):
        day_of_week = calendar.day_name[date.weekday()]
        #  TODO: make more compact and remove db retry
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
