# -*- coding: utf-8 -*-
import logging
import shutil
import urllib
from pathlib import Path

from django import forms

from credentials import VK_APP_TOKEN
from loader.models import Post, Compilation

from loader.vk_loader import VKLoader
from utils_text import parse_tags_from_input
from workspace_editor.utils import copy_post_to, delete_post, delete_compilation_holder
from workspace_editor.models import Workspace, Event, Schedule, CompilationHolder, Blog, WhiteListedBlog, \
    BlackListedBlog, SelectedBlog, ResourceAccount, Credentials
from account.models import Account
from UCA_Manager.settings import POSTS_FILES_DIRECTORY, RESOURCES, MEDIA_DIRECTORY_NAME, MEDIA_ROOT
from loader.utils import generate_storage_path, create_empty_compilation, \
    save_files_from_request, save_files_from_urls

from django.db.models import Q
import datetime
import os


log = logging.getLogger(__name__)

POSTS_PER_DOWNLOAD_CHOICES = (
            (5, 5),
            (10, 10),
            (15, 15),
            (20, 20),
            (25, 25),
            (30, 30),
            (35, 35),
            (40, 40),
            (45, 45),
            (50, 50),
        )


class WorkspaceCreateForm(forms.ModelForm):
    visible_for = forms.CharField(required=False)
    editable_by = forms.CharField(required=False)

    class Meta:
        model = Workspace
        exclude = ("owner", "visible_for", "editable_by", "schedule", "schedule_archive", "scheduled_compilation_id",
                   "main_compilation_id", "main_compilation_archive_id", "event_rules", "description")

    def set_owner(self, user):
        workspace = self.instance
        workspace.owner_id = user.pk
        self.instance = workspace

    def set_schedules(self, schedule, schedule_archive):
        workspace = self.instance
        workspace.schedule_id = schedule.schedule_id
        workspace.schedule_archive_id = schedule_archive.schedule_id
        self.instance = workspace

    def set_event_rules(self, event_rules):
        workspace = self.instance
        workspace.event_rules = event_rules
        self.instance = workspace

    def save(self, commit=True):
        workspace = self.instance

        workspace.scheduled_compilation_id = create_empty_compilation().id
        workspace.main_compilation_id = create_empty_compilation().id
        workspace.main_compilation_archive_id = create_empty_compilation().id

        if commit:
            workspace.save()

        for email in self.cleaned_data["visible_for"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                workspace.visible_for.add(user.pk)
        for email in self.cleaned_data["editable_by"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                workspace.editable_by.add(user.pk)

        return workspace


class WorkspaceEditForm(WorkspaceCreateForm):
    workspace_id = forms.CharField(required=True)
    name         = forms.CharField(required=True)
    visible_for  = forms.CharField(required=False)
    editable_by  = forms.CharField(required=False)


    class Meta:
        model = Workspace
        exclude = ("owner", "schedule", "schedule_archive", "scheduled_compilation_id", "main_compilation_id",
                   "main_compilation_archive_id", "event_rules", "description")

    def __init__(self, *args, **kwargs):
        super(WorkspaceEditForm, self).__init__(*args, **kwargs)
        if self.initial:
            self.fields["workspaces"] = forms.ChoiceField(choices=get_workspaces(self.initial["user_id"]), required=True)

    def save_edited_workspace(self, workspace, commit=True):
        edited_workspace = self.instance

        edited_workspace.owner = workspace.owner
        edited_workspace.workspace_id = workspace.workspace_id
        edited_workspace.schedule = workspace.schedule
        edited_workspace.schedule_archive = workspace.schedule_archive
        edited_workspace.scheduled_compilation_id = workspace.scheduled_compilation_id
        edited_workspace.main_compilation_id = workspace.main_compilation_id
        edited_workspace.main_compilation_archive_id = workspace.main_compilation_archive_id

        edited_workspace.editable_by.clear()
        edited_workspace.visible_for.clear()

        for email in self.cleaned_data["visible_for"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                edited_workspace.visible_for.add(user.pk)

        for email in self.cleaned_data["editable_by"].split(";"):
            if Account.objects.filter(email=email).exists():
                user = Account.objects.filter(email=email).get()
                edited_workspace.editable_by.add(user.pk)

        if commit:
            edited_workspace.save()

        return edited_workspace


class WorkspaceUploadPostsForm(forms.Form):

    def upload_posts(self, schedule_id):
        # TODO: implement checking for events with late datetime and show error on frontend
        if Event.objects.filter(schedule_id=schedule_id).exists():
            events = Event.objects.filter(schedule_id=schedule_id).order_by('start_date')

            vk_loader = VKLoader(vk_app_token=VK_APP_TOKEN)
            for event in events:
                vk_loader.upload(event)


    class Meta:
        widgets = {'empty_field': forms.HiddenInput(),}


class CompilationHolderCreateForm(forms.ModelForm):
    name                = forms.CharField(required=True)
    resources           = forms.ChoiceField(choices=RESOURCES)
    posts_per_download  = forms.ChoiceField(initial=25, choices=POSTS_PER_DOWNLOAD_CHOICES)
    description         = forms.CharField(widget=forms.Textarea(attrs={"rows":2, "cols":20}), required=False)


    class Meta:
        model = CompilationHolder
        exclude = ('workspace', 'whitelisted_blog_id', 'blacklisted_blog_id', 'whitelisted_tags', 'blacklisted_tags',
                   'number_on_list', 'compilation_id', )


    def set_workspace(self, workspace):
        holder = self.instance
        holder.workspace_id = workspace.workspace_id
        self.instance = holder

    def save(self, commit=True):
        holder = self.instance

        other_holders = CompilationHolder.objects.filter(workspace=holder.workspace_id)
        for oh in other_holders:
            oh.number_on_list += 1
            oh.save()
        holder.number_on_list = 1

        holder.compilation_id = create_empty_compilation().id

        # TODO: delete after migrations of db
        holder.whitelisted_tags = ""
        holder.blacklisted_tags = ""

        if commit:
            holder.save()

        return holder


class CompilationHolderEditForm(forms.ModelForm):
    # TODO: implement mechanism for creating list of all blogs urls and blog names in resource - two dicts
    #  (call asynchron before each downloading context recreation)
    # TODO: implement mechanism for hints during printing blogs names (from variant from the list)
    name                = forms.CharField(required=True)
    whitelisted_blogs   = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}), required=False)
    selected_blogs      = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}), required=False)
    blacklisted_blogs   = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}), required=False)
    whitelisted_tags    = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}), required=False)
    selected_tags       = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}), required=False)
    blacklisted_tags    = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}), required=False)
    resources           = forms.ChoiceField(choices=RESOURCES)
    posts_per_download  = forms.ChoiceField(choices=POSTS_PER_DOWNLOAD_CHOICES)
    number_on_list      = forms.IntegerField(required=False)
    description         = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}), required=False)

    def save_edited_holder(self, holder, commit=True):
        edited_holder = self.instance

        edited_holder.workspace_id          = holder.workspace_id
        edited_holder.compilation_holder_id = holder.compilation_holder_id
        edited_holder.compilation_id        = holder.compilation_id

        edited_holder.whitelisted_tags = parse_tags_from_input(self.cleaned_data["whitelisted_tags"])
        edited_holder.selected_tags = parse_tags_from_input(self.cleaned_data["selected_tags"])
        edited_holder.blacklisted_tags = parse_tags_from_input(self.cleaned_data["blacklisted_tags"])

        for blog_name in self.cleaned_data["whitelisted_blogs"].split():
            blog = Blog()
            # TODO: checking for existing blog with this name in selected resource
            blog.name = blog_name
            whitelisted_blog = WhiteListedBlog()
            blog.whitelisted_blog = whitelisted_blog
            whitelisted_blog.compilation_holder = holder
            whitelisted_blog.save()
            blog.save()

            edited_holder.whitelisted_blog.add(whitelisted_blog)

        for blog_name in self.cleaned_data["selected_blogs"].split():
            blog = Blog()
            # TODO: checking for existing blog with this name in selected resource
            blog.name = blog_name
            selected_blogs = SelectedBlog()
            blog.whitelisted_blog = selected_blogs
            selected_blogs.compilation_holder = holder
            selected_blogs.save()
            blog.save()

            edited_holder.whitelisted_blog.add(selected_blogs)

        for blog_name in self.cleaned_data["blacklisted_blogs"].split():
            blog = Blog()
            # TODO: checking for existing blog with this name in selected resource
            blog.name = blog_name
            blacklisted_blog = BlackListedBlog()
            blog.blacklisted_blog = blacklisted_blog
            blacklisted_blog.compilation_holder = holder
            blacklisted_blog.save()
            blog.save()
            holder.blacklisted_blog.add(blacklisted_blog)

            edited_holder.blacklisted_blogs.add(blog)

        edited_holder.number_on_list = self.cleaned_data["number_on_list"]
        other_holders = CompilationHolder.objects.filter(workspace=edited_holder.workspace_id)
        for oh in other_holders:
            if oh.number_on_list >= edited_holder.number_on_list:
                oh.number_on_list += 1
                oh.save()

        if commit:
            edited_holder.save()

        return edited_holder


    class Meta:
        model = CompilationHolder
        exclude = ('workspace',
                   'compilation_id',
                   )


class CompilationHolderDeleteForm(forms.Form):
    compilation_holder_id = forms.IntegerField(required=True)

    def delete(self):
        holder_id = self.data["compilation_holder_id"]
        delete_compilation_holder(holder_id)


class CompilationHolderGetIdForm(forms.Form):
    compilation_holder_id = forms.IntegerField(required=True)

    def get_holder_id(self):
        return self.data["compilation_holder_id"]


class EventCreateForm(forms.ModelForm):
    start_date  = forms.DateTimeField(input_formats=["%d.%m.%Y %H:%M"], required=True)
    post_id     = forms.CharField(required=True)

    def safe_copied_post(self, workspace_id, recipient_compilation_id, delete_original_post=False):
        post_id = self.instance.post_id
        new_post_id = copy_post_to(workspace_id, recipient_compilation_id, post_id)
        if delete_original_post:
            delete_post(post_id, delete_files=False)
        self.instance.post_id = new_post_id

    def set_schedule(self, schedule):
        event = self.instance
        event.schedule = schedule
        self.instance = event


    class Meta:
        model = Event
        exclude = ('schedule', )


class EventEditForm(forms.ModelForm):
    start_date = forms.DateTimeField(input_formats=["%d.%m.%Y %H:%M"], required=True)

    # TODO: check and fix
    def save(self, commit=True):
        event = self.instance
        event.start_date = self.cleaned_data["start_date"]
        if commit:
            event.save()

        return event

    class Meta:
        model = Event
        exclude = ('post_id', 'schedule_id', )


class PostCreateForm(forms.Form):
    tags            = forms.CharField(required=False)
    text            = forms.CharField(widget=forms.Textarea(attrs={"rows":3, "cols":10}), required=False)
    images          = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    description     = forms.CharField(widget=forms.Textarea(attrs={"rows":3, "cols":10}), required=False)

    def save(self, workspace, compilation, images=None, commit=True):
        tags = list()
        for tag in self.data["tags"].split():
            tags.append(tag)

        post = Post.create(
            # information about original post
            posted_date           = str(datetime.now()),
            posted_timestamp      = datetime.now().timestamp(),
            tags                  = tags,
            text                  = str(self.data["text"]),
            compilation_id        = compilation.id,
            description           = str(self.data["description"])
        )

        if commit:
            if images:
                post_storage_path \
                    = os.path.join(MEDIA_DIRECTORY_NAME, POSTS_FILES_DIRECTORY, str(workspace.workspace_id), str(compilation.id), str(post.id))
                saved_file_addresses = save_files_from_request(post_storage_path, images)
                post.stored_file_urls = saved_file_addresses

            if compilation.post_ids is None:
                compilation.post_ids = [post.id]
            else:
                compilation.post_ids.append(post.id)
            compilation.update()

            post.save()

        return post


class PostEditForm(forms.Form):
    post_id         = forms.CharField(required=True)
    tags            = forms.CharField(required=False)
    text            = forms.CharField(widget=forms.Textarea(attrs={"rows":3, "cols":10}), required=False)
    images          = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    description     = forms.CharField(widget=forms.Textarea(attrs={"rows":3, "cols":10}), required=False)

    def save(self, workspace, compilation, images=None, commit=True):
        post = Post.objects.get(id=self.cleaned_data["post_id"])
        post.tags = parse_tags_from_input(self.cleaned_data["tags"])
        post.text = self.cleaned_data["text"]

        if images:
            post_storage_path \
                = os.path.join(MEDIA_DIRECTORY_NAME, POSTS_FILES_DIRECTORY, str(workspace.workspace_id), str(compilation.id), str(post.id))
            saved_file_addresses = save_files_from_request(post_storage_path, images)
            post.stored_file_urls = saved_file_addresses

        post.description = self.cleaned_data["description"]

        if commit:
            post.save()

        return post


class PostDeleteForm(forms.Form):
    post_id = forms.CharField(required=True)

    def delete(self):
        post_id = self.data["post_id"]
        delete_post(post_id)


class ResourceAccountCreateForm(forms.Form):
    name                         = forms.CharField(max_length=255)
    avatar                       = forms.FileField(widget=forms.ClearableFileInput(), required=False)
    resource                     = forms.ChoiceField(choices=RESOURCES)
    login                        = forms.CharField(max_length=255, required=False)
    password                     = forms.CharField(max_length=255, required=False)
    consumer_key                 = forms.CharField(max_length=255, required=False)
    consumer_secret              = forms.CharField(max_length=255, required=False)
    token                        = forms.CharField(max_length=255, required=False)
    secret                       = forms.CharField(max_length=255, required=False)

    def save(self, owner=None, avatar=None, commit=True):
        data = self.data
        credentials = Credentials(
            resource = data.get('resource'),
            login = data.get('login'),
            password = data.get('password'),
            consumer_key = data.get('consumer_key'),
            consumer_secret = data.get('consumer_secret'),
            token = data.get('token'),
            secret = data.get('secret'))

        if commit:
            credentials.save()
            account = ResourceAccount(
                name = data.get('name'),
                owner = owner,
                credentials = credentials)
            account.save()

            if avatar:
                post_storage_path \
                    = os.path.join(MEDIA_DIRECTORY_NAME, POSTS_FILES_DIRECTORY, str(owner), 'accounts', str(account.name))
                # TODO: rename POSTS_FILES_DIRECTORY to FILES_STORAGE_DIRECTORY
                saved_file_addresses = save_files_from_request(post_storage_path, avatar)
                account.avatar = saved_file_addresses[0]

                account.save()


class ResourceAccountDeleteForm(forms.Form):
    id = forms.CharField(required=True)

    def delete(self):
        account = ResourceAccount.objects.get(resource_account_id=self.data["id"])
        if account.avatar:
            # TODO: use MEDIA_URL for cloud storage and MEDIA_ROOT for local
            folder = os.path.join(MEDIA_ROOT, Path(str(account.avatar)).parent)
            shutil.rmtree(folder)
        account.delete()


class BlogAddFromResourceAccountForm1(forms.Form):
    resource_account = forms.ModelChoiceField(queryset=ResourceAccount.objects.all())

    def get_blogs_list(self):
        data = self.data

        if data.get('resource_account').resource == ("VKontakte", "VKontakte"):
            vk_loader = VKLoader(vk_app_token=data.get('resource_account').token)
            blogs_resource_numbers = vk_loader.get_controlled_blogs_resource_numbers()
            return vk_loader.get_blogs_info(blogs_resource_numbers)


            # context["blog_create_form"] = BlogCreateForm(initial={'name':})


class BlogCreateForm(forms.Form):
    name                         = forms.CharField(max_length=255, required=False)
    avatar_url                   = forms.CharField(max_length=2047, required=False)
    blog_resource_number         = forms.IntegerField(required=False)
    workspace_id                 = forms.IntegerField(required=False)
    url                          = forms.CharField(max_length=2047, required=False)

    def save(self, account=None, resource_account=None, commit=True):
        data = self.cleaned_data

        blog = Blog(
            name = data.get('name'),
            resource=resource_account.credentials.resource,
            blog_resource_number = data.get('blog_resource_number'),
            workspace = Workspace.objects.get(workspace_id=data.get('workspace_id')),
            controlled = True,
            account = account,
            resource_account = resource_account,
            url = data.get('url'))

        if commit:
            blog.save()

            if data.get('avatar_url'):
                new_storage_dir = os.path.join(MEDIA_DIRECTORY_NAME, str(account), 'blogs', str(blog.blog_id))
                print(f"Trying to create directory '{new_storage_dir}'")
                os.makedirs(new_storage_dir, exist_ok=True)

                safe_as = os.path.basename(data.get('avatar_url')).split('?')[0]
                path_to_image = os.path.join(new_storage_dir, safe_as)

                opener = urllib.request.URLopener()
                opener.addheader('User-Agent', 'Mozilla/5.0')
                opener.retrieve(data.get('avatar_url'), path_to_image)

                blog.avatar = safe_as
                blog.save()

            return blog


class BlogDeleteForm(forms.Form):
    id = forms.CharField(required=True)

    def delete(self):
        blog = Blog.objects.get(blog_id=self.data["id"])
        if blog.avatar:
            # TODO: use MEDIA_URL for cloud storage and MEDIA_ROOT for local
            blog_folder = os.path.join(MEDIA_ROOT, str(blog.account), 'blogs', str(blog.blog_id))
            shutil.rmtree(blog_folder)
        blog.delete()


# TODO: move method to utils
def get_workspaces(user_id):
    workspaces = Workspace.objects.filter(Q(owner=user_id) | Q(editable_by=user_id))
    choices = []

    for workspace in workspaces:
        choices.append((workspace.pk, workspace.name))

    return choices
