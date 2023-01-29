from django.contrib.auth.decorators import login_required

from loader.tumblr_loader import TumblrLoader
from UCA_Manager.settings import PATH_TO_STORE
from workspace_editor.utils import copy_compilation_posts
from workspace_editor.serializers import WorkspaceSerializer
from django.shortcuts import render, redirect

from django.core.paginator import Paginator
from workspace_editor.models import *
import calendar
from workspace_editor.forms.forms import *
import datetime

from loader.models import *

log = logging.getLogger(__name__)

RESOURCES_PER_NAMES = {
    "Tumbler": TumblrLoader()
}


@login_required
def resource_accounts(request, workspace_id=None, resource_account_id=None):
    context = dict()
    workspace = __workspace_choice(request, workspace_id)

    # TODO: add if-else for workspace like in method event_rules (event_rules_view.py)
    if workspace:
        accounts = ResourceAccount.objects.filter(owner=request.user)
        resource_accounts_to_resource = dict()
        for account in accounts:
            resource_accounts_to_resource[account] = account.credentials

        context["resource_accounts"] = ResourceAccount.objects.filter(owner=request.user)

    if request.POST:
        if request.POST['action'] == 'resource_account_create':
            form = ResourceAccountCreateForm(request.POST)
            if form.is_valid():
                form.save(owner=request.user, avatar=request.FILES.getlist('avatar'))
            else:
                log.error(form.errors.as_data())

        if resource_account_id:
            if request.POST['action'] == 'resource_account_edit':
                pass
            elif request.POST['action'] == 'resource_account_delete':
                form = ResourceAccountDeleteForm(request.POST)
                if form.is_valid():
                    form.delete()
                else:
                    log.error(form.errors.as_data())

        return redirect(f'resource_accounts', workspace_id=workspace.workspace_id)

    context["MEDIA_LOCATION"] = "../../media"
    context["workspace"] = workspace
    if resource_account_id:
        context["resource_account_id"] = resource_account_id

    context["resource_account_create_form"] = ResourceAccountCreateForm()
    context["resource_account_delete_form"] = ResourceAccountDeleteForm()

    return render(request, "resource_accounts/resource_accounts.html", context)


@login_required
def resource_account_add_blog(request, workspace_id, resource_account_id):
    context = dict()

    resource_account = ResourceAccount.objects.get(resource_account_id=resource_account_id)
    context["resource_account"] = resource_account
    context["workspace"] = Workspace.objects.get(workspace_id=workspace_id)
    context["owner"] = request.user

    blogs_info = dict()
    if resource_account.credentials.resource == "VKontakte":
        vk_loader = VKLoader(vk_app_token=resource_account.credentials.token)
        blogs_resource_numbers = vk_loader.get_controlled_blogs_resource_numbers()
        blogs_info = vk_loader.get_blogs_info(blogs_resource_numbers)
        for blog in blogs_info.values():
            if Blog.objects.filter(blog_resource_number=blog.blog_resource_number).exists():
                blog.added = True
                blog.id = Blog.objects.get(blog_resource_number=blog.blog_resource_number).blog_id
            else:
                blog.added = False
    context["blogs"] = blogs_info

    if request.POST:
        if request.POST['action'] == 'blog_create':
            resource_account = ResourceAccount.objects.get(resource_account_id=resource_account_id)
            form = BlogCreateForm(request.POST)
            if form.is_valid():
                form.save(resource_account=resource_account,
                          account=request.user)
            else:
                log.error(form.errors.as_data())

        elif request.POST['action'] == 'blog_delete':
            form = BlogDeleteForm(request.POST)
            if form.is_valid():
                form.delete()
            else:
                log.error(form.errors.as_data())
        return redirect(f'resource_account_add_blog', workspace_id=workspace_id, resource_account_id=resource_account_id)

    context["blog_create_form"] = BlogCreateForm()
    context["blog_delete_form"] = BlogDeleteForm()

    return render(request, "resource_account_add_blog/resource_account_add_blog.html", context)


@login_required
def blogs(request, workspace_id=None, blog_id=None):
    context = dict()
    workspace = __workspace_choice(request, workspace_id)

    # TODO: add if-else for workspace like in method event_rules (event_rules_view.py)
    if request.POST:
        if blog_id and request.POST['action'] == 'blog_delete':
            form = BlogDeleteForm(request.POST)
            if form.is_valid():
                form.delete()
            else:
                log.error(form.errors.as_data())
        return redirect(f'blogs', workspace_id=workspace.workspace_id)

    context["MEDIA_LOCATION"] = "../../media"
    # TODO: rename POSTS_FILES_DIRECTORY to FILES_STORAGE_DIRECTORY
    context["BLOGS_MEDIA_LOCATION"] \
        = os.path.join("../../media", str(request.user), 'blogs')
    context["workspace"] = workspace
    if workspace:
        context["blogs"] = Blog.objects.filter(Q(workspace=workspace) | Q(controlled=True))
    if blog_id:
        context["blog_id"] = blog_id

    # TODO: make initials for blogs, that this account can moderate
    context["blog_delete_form"] = BlogDeleteForm()

    return render(request, "blogs/blogs.html", context)


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


    context = __prepare_workspace_context(request=request, workspace=workspace, post_id=post_id)

    return render(request, "workspace.html", context)


@login_required
def downloading(request, workspace_id=None, holder_id=None, holder_id_to_delete=None, post_id=None):
    workspace = __workspace_choice(request, workspace_id)

    if request.POST:
        workspace = __workspace_request_handler(request, workspace)

        if workspace:
            schedule = Schedule.objects.get(schedule_id=int(workspace.schedule_id))
            # TODO: check if __event_request_handler need here
            __event_request_handler(request, workspace, schedule)
            __post_request_handler(request, workspace, post_id)
            __compilation_holder_request_handler(request, workspace, holder_id, holder_id_to_delete)

        return redirect(f'downloading_workspace_by_id', workspace_id=workspace.workspace_id)

    context = __prepare_downloading_context(request=request, workspace=workspace, holder_id=holder_id,
                                            holder_id_to_delete=holder_id_to_delete, post_id=post_id)

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
        redirect(f'workspace_by_id', workspace_id=workspace.workspace_id)

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
            event_rules = EventRules.objects.create()
            for i in range(0, 7):
                for j in range(0, i):
                    PostingTime.objects.create(time=datetime.time(hour=0, minute=0, second=0),
                                               event_rules=event_rules, priority=i).save()
            form.set_event_rules(event_rules)
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

    elif workspace and request.POST['action'] == 'upload_posts':
        form = WorkspaceUploadPostsForm(request.POST)
        if form.is_valid():
            schedule_id = workspace.schedule.schedule_id
            form.upload_posts(schedule_id)
        else:
            log.error(form.errors.as_data())

    return workspace


def __compilation_holder_request_handler(request, workspace, holder_id=None, holder_id_to_delete=None,):
    if request.POST['action'] == 'create_holder':
        form = CompilationHolderCreateForm(request.POST,
                                           initial={'name': "Compilation holder",
                                                    'posts_per_download': 25})
        if form.is_valid():
            form.set_workspace(workspace)
            form.save()
        else:
            log.error(form.errors.as_data())

    elif holder_id and request.POST['action'] == 'edit_holder':
        holder = CompilationHolder.objects.get(compilation_holder_id=holder_id)

        form = CompilationHolderEditForm(request.POST)
        if form.is_valid():
            form.save_edited_holder(holder)
        else:
            log.error(form.errors.as_data())

    elif request.POST['action'] == 'download_posts':
        form = CompilationHolderGetIdForm(request.POST)
        if form.is_valid():
            holder = CompilationHolder.objects.get(compilation_holder_id=form.get_holder_id())

            loader = RESOURCES_PER_NAMES[holder.resources]
            loader.print_user_info()

            # TODO: use holder.selected_blogs in condition
            if holder.selected_tags:
                # TODO: use array after realisation multiple tag downloading
                tag = holder.selected_tags.split()[0]
                number = holder.posts_per_download
                # TODO: use downloading from specific blogs:
                #  blogs = holder.selected_blog

                compilation = Compilation.objects.get(id=holder.compilation_id)

                path = generate_storage_path(PATH_TO_STORE, work_sp_id=workspace.workspace_id, comp_id=compilation.id)
                compilation.storage = path

                # TODO: made asynchronous
                loader.download(compilation, number, tag=tag, storage_path=path)
        else:
            log.error(form.errors.as_data())

    elif request.POST['action'] == 'copy_posts_to_main_compilation':
        form = CompilationHolderGetIdForm(request.POST)
        if form.is_valid():
            holder = CompilationHolder.objects.get(compilation_holder_id=form.get_holder_id())
            compilation = Compilation.objects.get(id=holder.compilation_id)
            copy_compilation_posts(workspace_id=workspace.workspace_id,
                                   sender_compilation_id=compilation.id,
                                   recipient_compilation_id=uuid.UUID(workspace.main_compilation_id))
        else:
            log.error(form.errors.as_data())
    elif holder_id_to_delete and request.POST['action'] == 'delete_holder':
        form = CompilationHolderDeleteForm(request.POST)
        if form.is_valid():
            form.delete()
        else:
            log.error(form.errors.as_data())


def __event_request_handler(request, workspace, schedule):
    if request.POST['action'] == "create_event":
        form = EventCreateForm(request.POST)
        if form.is_valid():
            form.safe_copied_post(workspace.workspace_id, workspace.scheduled_compilation_id, delete_original_post=True)
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

    elif request.POST['action'] == 'clean_post_text':
        form = PostEditForm(request.POST)
        if form.is_valid():
            compilation = Compilation.objects.get(id=workspace.main_compilation_id)
            # form.text = ""
            form.save(workspace=workspace, compilation=compilation)
        else:
            log.error(form.errors.as_data())

    elif post_id and request.POST['action'] == 'edit_post':
        form = PostEditForm(request.POST)
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
    context = __prepare_mutual_context(request=request, workspace=workspace, post_id=post_id)

    if workspace:
        schedule = Schedule.objects.get(schedule_id=int(workspace.schedule_id))

        # TODO: make table compilationsOwners with compilation_id, owner and visible_for for looking for
        #  only current user compilations
        context["my_compilations"] = Compilation.objects.all()
        context["post_in_schedule"], context["schedule_events"] = __get_events_for_schedule(schedule.schedule_id)
        context["selected_schedule_id"] = int(schedule.schedule_id)

        context["blogs"] = Blog.objects.filter(Q(workspace=workspace) | Q(controlled=True))
        context["BLOGS_MEDIA_LOCATION"] = os.path.join("../../media", str(request.user), 'blogs')

        context["event_create_form"] = EventCreateForm()
        # TODO: rename event_edit_form to event_edit_form
        context["edit_event_form"] = EventEditForm()

        context["workspace_upload_posts_form"] = WorkspaceUploadPostsForm()

    return context



def __prepare_downloading_context(request, workspace=None, holder_id=None, holder_id_to_delete=None, post_id=None):
    context = __prepare_mutual_context(request=request, workspace=workspace, post_id=post_id)

    if workspace:
        context['compilation_create_form'] = CompilationHolderCreateForm()
        if holder_id:
            holder = CompilationHolder.objects.get(compilation_holder_id=holder_id)
            whitelisted_blogs_names = ' '.join(list(map(lambda blog: blog.name,
                                               WhiteListedBlog.objects.filter(compilation_holder=holder))))
            selected_blogs_names = ' '.join(list(map(lambda blog: blog.name,
                                               SelectedBlog.objects.filter(compilation_holder=holder))))
            blacklisted_blogs_names = ' '.join(list(map(lambda blog: blog.name,
                                               BlackListedBlog.objects.filter(compilation_holder=holder))))

            context['compilation_edit_form'] = CompilationHolderEditForm(
                 initial={'name': holder.name,
                          'whitelisted_blogs': whitelisted_blogs_names,
                          'selected_blogs': selected_blogs_names,
                          'blacklisted_blogs': blacklisted_blogs_names,
                          'whitelisted_tags': holder.whitelisted_tags,
                          'selected_tags': holder.selected_tags,
                          'blacklisted_tags': holder.blacklisted_tags,
                          'resources': holder.resources,
                          'posts_per_download': holder.posts_per_download,
                          # TODO: make constraints for number_on_list from 1 to N_holders - 1
                          'number_on_list':  holder.number_on_list,
                          'description': holder.description})
        context['compilation_get_id_form'] = CompilationHolderGetIdForm()
        context['compilation_delete_form'] = CompilationHolderDeleteForm()

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

        if holder_id:
            context['selected_holder'] = CompilationHolder.objects.get(compilation_holder_id=holder_id)

        if holder_id_to_delete:
            context['selected_for_delete_holder'] = CompilationHolder.objects.get(compilation_holder_id=holder_id_to_delete)

    return context


# TODO: investigate and move part of methods to __prepare_workspace_context()
def __prepare_mutual_context(request, workspace=None, post_id=None):
    context = dict()

    context["resources"] = RESOURCES

    queryset_visible = Workspace.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user))
    # TODO: rename to visible_workspaces
    context["my_workspaces"] = queryset_visible

    queryset_editable = Workspace.objects.filter(Q(owner=request.user.pk) | Q(editable_by=request.user))
    # TODO: rename to editable_workspaces
    context["workspaces"] = WorkspaceSerializer(queryset_editable, many=True).data

    context["create_form"] = WorkspaceCreateForm()
    context["edit_form"] = WorkspaceEditForm(initial={"user_id": request.user.pk, "owner": request.user})


    if workspace:
        context["workspace"] = workspace
        context["selected_workspace_id"] = workspace.workspace_id

        context["post_create_form"] = PostCreateForm()
        if post_id:
            post = Post.objects.get(id=post_id)
            context["post_edit_form"] = PostEditForm(initial={"tags": '#' + ' #'.join(post.tags),
                                                              "text": post.text,
                                                              "description": post.description})
        else:
            context["post_edit_form"] = PostEditForm()

        context["post_delete_form"] = PostDeleteForm()

        # TODO: use MEDIA_URL for cloud storage and MEDIA_ROOT for local
        context["MEDIA_LOCATION"] = "../media"

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


def __get_events_for_schedule(schedule_id):
    dates_to_events = dict()
    days_count = 0
    days_to_show = 7
    post_in_schedule = 0
    date = datetime.date.today()

    while True:
        day_of_week = calendar.day_name[date.weekday()]
        #  TODO: make more compact and remove db retry
        if Event.objects.filter(schedule_id=schedule_id, start_date__year=date.year,
                                start_date__month=date.month, start_date__day=date.day).exists():
            events = Event.objects.filter(schedule_id=schedule_id, start_date__year=date.year,
                                          start_date__month=date.month, start_date__day=date.day).order_by('start_date')
            events_to_posts = dict()
            for event in events:
                if Post.objects.filter(id=event.post_id).count() == 0:
                    logging.error(f"For event with id='{event.event_id}' "
                                  f"post with id='{event.post_id}' was haven't found in cassandra")
                else:
                    events_to_posts[event] = Post.objects.get(id=event.post_id)

            dates_to_events[(date, day_of_week)] = events_to_posts
            post_in_schedule += len(events_to_posts)
        else:
            dates_to_events[(date, day_of_week)] = []

        date += datetime.timedelta(days=1)
        days_count += 1
        if days_count >= days_to_show \
                and not Event.objects.filter(start_date__range=[date, date + datetime.timedelta(days=365)]).exists():
            break

    return post_in_schedule, dates_to_events
