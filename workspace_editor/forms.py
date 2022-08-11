# -*- coding: utf-8 -*-
import logging

from django import forms

from loader.models import Post, Compilation
from workspace_editor.utils import copy_post_to
from workspace_editor.models import Workspace, Event, Schedule, CompilationHolder, Blog, WhiteListedBlog, \
    BlackListedBlog
from account.models import Account
from UCA_Manager.settings import PATH_TO_STORE, RESOURCES
from loader.utils import generate_storage_patch, create_empty_compilation, \
    save_files_from_request

from django.db.models import Q
from datetime import datetime
import os
import shutil


log = logging.getLogger(__name__)

class WorkspaceCreateForm(forms.ModelForm):
    visible_for = forms.CharField(required=False)
    editable_by = forms.CharField(required=False)

    class Meta:
        model = Workspace
        exclude = ("owner", "visible_for", "editable_by", "schedule", "schedule_archive",
                   "scheduled_compilation_id", "main_compilation_id", "main_compilation_archive_id", "description")

    def set_owner(self, user):
        workspace = self.instance
        workspace.owner_id = user.pk
        self.instance = workspace

    def set_schedules(self, schedule, schedule_archive):
        workspace = self.instance
        workspace.schedule_id = schedule.schedule_id
        workspace.schedule_archive_id = schedule_archive.schedule_id
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
        exclude = ("owner", "schedule", "schedule_archive",
                   "scheduled_compilation_id", "main_compilation_id", "main_compilation_archive_id", "description")

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


class CompilationHolderCreateForm(forms.ModelForm):
    name                = forms.CharField(required=True)
    resources           = forms.ChoiceField(choices=(
                                                    ("Tumbler", "Tumbler"),
                                                ))
    description         = forms.CharField(widget=forms.Textarea(attrs={"rows":2, "cols":20}), required=False)

    def set_workspace(self, workspace):
        holder = self.instance
        holder.workspace_id = workspace.workspace_id
        self.instance = holder

    def save(self, commit=True):
        holder = self.instance

        other_holders = CompilationHolder.objects.filter(workspace=holder.workspace_id)
        for holder in other_holders:
            holder.number_on_list += 1
            holder.save()
        holder.number_on_list = 1

        holder.compilation_id = create_empty_compilation().id

        if commit:
            holder.save()

        return holder


    class Meta:
        model = CompilationHolder
        exclude = ('workspace', 'whitelisted_blogs', 'blacklisted_blogs', 'whitelisted_tags', 'blacklisted_tags',
                   'number_on_list', 'compilation_id', )
        # exclude = ('workspace', 'number_on_list', 'compilation_id', )


class CompilationHolderEditForm(forms.ModelForm):
    name                = forms.CharField(required=True)
    whitelisted_blogs   = forms.CharField(widget=forms.Textarea(attrs={"rows":2, "cols":20}), required=False)
    blacklisted_blogs   = forms.CharField(widget=forms.Textarea(attrs={"rows":2, "cols":20}), required=False)
    whitelisted_tags    = forms.CharField(widget=forms.Textarea(attrs={"rows":2, "cols":20}), required=False)
    blacklisted_tags    = forms.CharField(widget=forms.Textarea(attrs={"rows":2, "cols":20}), required=False)
    resources           = forms.ChoiceField(choices=RESOURCES)
    description         = forms.CharField(widget=forms.Textarea(attrs={"rows":2, "cols":20}), required=False)

    def save_edited_holder(self, holder, commit=True):
        edited_holder = self.instance


        edited_holder.workspace_id          = holder.workspace_id
        edited_holder.compilation_holder_id = holder.compilation_holder_id

        tags = []
        for tag in self.cleaned_data["whitelisted_tags"].split():
            # TODO: checking for existing posts with this tag in selected resource
            tag = ''.join(filter(str.isalnum, tag))
            if tag not in tags:
                tags.append(tag)
        holder.whitelisted_tags = ' '.join(tags)

        tags = []
        for tag in self.cleaned_data["blacklisted_tags"].split():
            # TODO: checking for existing posts with this tag in selected resource
            tag = ''.join(filter(str.isalnum, tag))
            if tag not in tags:
                tags.append(tag)
        holder.blacklisted_tags = ' '.join(tags)

        for blog_name in self.cleaned_data["whitelisted_blogs"].split():
            blog = Blog()
            # TODO: checking for existing blog with this name in selected resource
            blog.name = blog_name
            whitelisted_blog = WhiteListedBlog()
            blog.whitelisted_blog = whitelisted_blog
            whitelisted_blog.compilation_holder = holder
            whitelisted_blog.save()
            blog.save()

            holder.whitelisted_blog.add(whitelisted_blog)

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

            holder.blacklisted_blogs.add(blog)

        # workspace = Workspace.objects.get(workspace_id=holder.workspace_id)
        other_holders = CompilationHolder.objects.filter(workspace=edited_holder.workspace_id)
        for edited_holder in other_holders:
            edited_holder.number_on_list += 1
            edited_holder.save()
        edited_holder.number_on_list = 1

        edited_holder.compilation_id = create_empty_compilation().id

        if commit:
            edited_holder.save()

        return edited_holder


    class Meta:
        model = CompilationHolder
        # exclude = ('workspace', 'whitelisted_blogs', 'blacklisted_blogs', 'whitelisted_tags', 'blacklisted_tags',
        #            'number_on_list', 'compilation_id', )
        exclude = ('workspace', 'number_on_list', 'compilation_id', 'name')


class EventCreateForm(forms.ModelForm):
    start_date  = forms.DateTimeField(input_formats=["%d.%m.%Y %H:%M"], required=True)
    post_id     = forms.CharField(required=True)

    def safe_copied_post(self, recipient_compilation_id):
        post_id = self.instance.post_id
        new_post_id = copy_post_to(post_id, recipient_compilation_id)
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


    # TODO: delete after finishing CompilationHolderCreateForm
class CompilationCreateForm(forms.Form):
    name                         = forms.CharField(required=True)
    resource                     = 'Tumbler'
    search_tag                   = forms.CharField(required=True)
    search_blogs                 = forms.CharField(required=False)
    downloaded_date              = str(datetime.now())

    print(f"search_tag: '{search_tag}'")
    search_tag  = 'paleontology'

    # TODO: check if its works
    storage                      = generate_storage_patch(PATH_TO_STORE, comp_id=id)
    post_ids                     = list()


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
                    = os.path.join(PATH_TO_STORE, str(workspace.workspace_id), str(compilation.id), str(post.id))
                saved_file_addresses = save_files_from_request(post_storage_path, images)
                post.stored_file_urls = saved_file_addresses

            if compilation.post_ids is None:
                compilation.post_ids = [post.id]
            else:
                compilation.post_ids.append(post.id)
            compilation.update()

            post.save()

        return post


class PostDeleteForm(forms.Form):
    post_id = forms.CharField(required=True)
    def delete(self):
        post_id = self.data["post_id"]
        post = Post.objects.get(id=post_id)

        if post:
            compilation_id = post.compilation_id
            compilation = Compilation.objects.get(id=compilation_id)

            if compilation:
                compilation.post_ids.remove(post.id)
                compilation.update()
            else:
                log.error(f"No compilation with id='{compilation_id}' for post id='{post.id}' ")

            if len(post.stored_file_urls) > 0:
                folder = post.stored_file_urls[0].parent
                for file in post.stored_file_urls:
                    os.remove(file)
                if len(os.listdir(folder)) == 0:
                    shutil.rmtree(folder)

            post.delete()

        else:
            log.error(f"No post with id='{post.id}' ")


def get_workspaces(user_id):
    workspaces = Workspace.objects.filter(Q(owner=user_id) | Q(editable_by=user_id))
    choices = []

    for workspace in workspaces:
        choices.append((workspace.pk, workspace.name))

    return choices


