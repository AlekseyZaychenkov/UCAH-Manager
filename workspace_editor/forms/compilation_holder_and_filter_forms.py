import logging

from django import forms
from workspace_editor.services.text_services import parse_tags_from_input
from workspace_editor.utils.utils import delete_compilation_holder
from workspace_editor.models import CompilationHolder, Blog, WhiteListedBlog, \
    BlackListedBlog, SelectedBlog, CompilationHolderFilterDownloader, CompilationHolderFilterMixer

from UCA_Manager.settings import RESOURCES
from loader.utils import create_empty_compilation

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


class CompilationHolderCreateForm(forms.ModelForm):
    name                = forms.CharField(required=True)

    type_by_post_source = forms.ChoiceField(choices=CompilationHolder.TYPE_BY_POST_SOURCE_CHOICES)
    posts_per_download  = forms.ChoiceField(initial=25, choices=POSTS_PER_DOWNLOAD_CHOICES)
    description         = forms.CharField(widget=forms.Textarea(attrs={"rows":2, "cols":20}), required=False)

    class Meta:
        model = CompilationHolder
        exclude = ('workspace', 'number_on_list', 'compilation_id', )


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

        if commit:
            holder.save()

        return holder


class CompilationHolderEditForm(forms.ModelForm):
    name                = forms.CharField(required=True)
    posts_per_download  = forms.ChoiceField(choices=POSTS_PER_DOWNLOAD_CHOICES)
    number_on_list      = forms.IntegerField(required=False)
    description         = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}), required=False)

    def save_edited_holder(self, holder, commit=True):
        edited_holder = self.instance

        edited_holder.workspace_id          = holder.workspace_id
        edited_holder.compilation_holder_id = holder.compilation_holder_id
        edited_holder.compilation_id        = holder.compilation_id

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
        exclude = ('workspace',  'compilation_id', 'type_by_post_source', )


class CompilationHolderDeleteForm(forms.Form):
    compilation_holder_id = forms.IntegerField(required=True)

    def delete(self):
        holder_id = self.data["compilation_holder_id"]
        delete_compilation_holder(holder_id)


class CompilationHolderGetIdForm(forms.Form):
    compilation_holder_id = forms.IntegerField(required=True)

    def get_holder_id(self):
        return self.data["compilation_holder_id"]


class CompilationHolderFilterDownloaderCreateForm(forms.ModelForm):

    def set_holder(self, holder):
        filter_downloader = self.instance
        filter_downloader.workspace_id = holder.workspace_id
        self.instance = filter_downloader

    # def save(self, commit=True):
    #     filter_downloader = self.instance
    #
    #     if commit:
    #         filter_downloader.save()
    #
    #     return filter_downloader

    class Meta:
        model = CompilationHolderFilterDownloader
        exclude = ('compilation_holder', 'whitelisted_tags', 'selected_tags', 'blacklisted_tags', 'resources', )


class CompilationHolderFilterDownloaderEditForm(forms.ModelForm):
    # TODO: implement mechanism for creating list of all blogs urls and blog names in resource - two dicts
    #  (call asynchron before each downloading context recreation)
    # TODO: implement mechanism for hints during printing blogs names (from variant from the list)
    whitelisted_blogs   = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}), required=False)
    selected_blogs      = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}), required=False)
    blacklisted_blogs   = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}), required=False)
    whitelisted_tags    = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}), required=False)
    selected_tags       = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}), required=False)
    blacklisted_tags    = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}), required=False)
    resource            = forms.ChoiceField(choices=RESOURCES)

    def save_edited_filter(self, filter_downloader, commit=True):
        edited_filter_downloader = self.instance

        edited_filter_downloader.compilation_holder = filter_downloader.compilation_holder

        edited_filter_downloader.whitelisted_tags = parse_tags_from_input(self.cleaned_data["whitelisted_tags"])
        edited_filter_downloader.selected_tags = parse_tags_from_input(self.cleaned_data["selected_tags"])
        edited_filter_downloader.blacklisted_tags = parse_tags_from_input(self.cleaned_data["blacklisted_tags"])

        for blog_name in self.cleaned_data["whitelisted_blogs"].split():
            blog = Blog()
            # TODO: checking for existing blog with this name in selected resource
            blog.name = blog_name
            whitelisted_blog = WhiteListedBlog()
            blog.whitelisted_blog = whitelisted_blog
            whitelisted_blog.compilation_holder = filter_downloader
            whitelisted_blog.save()
            blog.save()

            edited_filter_downloader.whitelisted_blog.add(whitelisted_blog)

        for blog_name in self.cleaned_data["selected_blogs"].split():
            blog = Blog()
            # TODO: checking for existing blog with this name in selected resource
            blog.name = blog_name
            selected_blogs = SelectedBlog()
            blog.whitelisted_blog = selected_blogs
            selected_blogs.compilation_holder = filter_downloader
            selected_blogs.save()
            blog.save()

            edited_filter_downloader.whitelisted_blog.add(selected_blogs)

        for blog_name in self.cleaned_data["blacklisted_blogs"].split():
            blog = Blog()
            # TODO: checking for existing blog with this name in selected resource
            blog.name = blog_name
            blacklisted_blog = BlackListedBlog()
            blog.blacklisted_blog = blacklisted_blog
            blacklisted_blog.compilation_holder = filter_downloader
            blacklisted_blog.save()
            blog.save()
            filter_downloader.blacklisted_blog.add(blacklisted_blog)

            edited_filter_downloader.blacklisted_blogs.add(blog)

        if commit:
            edited_filter_downloader.save()

        return edited_filter_downloader

    class Meta:
        model = CompilationHolderFilterDownloader
        exclude = ('compilation_holder_filter_id', 'compilation_holder', )


class CompilationHolderFilterDownloaderDeleteForm(forms.Form):
    compilation_holder_id = forms.IntegerField(required=True)

    def delete(self):
        filter_downloader_id = self.data["compilation_holder_filter_id"]
        CompilationHolderFilterDownloader.objects.get(compilation_holder_filter_id=filter_downloader_id).delete()


class CompilationHolderFilterMixerCreateForm(forms.ModelForm):

    def set_holder(self, holder):
        filter_mixer = self.instance
        filter_mixer.workspace_id = holder.workspace_id
        self.instance = filter_mixer

    # def save(self, commit=True):
    #     filter_mixer = self.instance
    #
    #     if commit:
    #         filter_mixer.save()
    #
    #     return filter_mixer

    class Meta:
        model = CompilationHolderFilterMixer
        exclude = ('compilation_holder', 'posts_likes_minimum', 'posts_likes_expected', 'source_compilation_holder', 'priority', )


class CompilationHolderFilterMixerEditForm(forms.ModelForm):
    # TODO: filter by workspace
    source_compilation_holder     = forms.ModelChoiceField(CompilationHolder.objects.all(), required=False)
    posts_likes_minimum           = forms.IntegerField()
    posts_likes_expected          = forms.IntegerField()
    priority                      = forms.FloatField()

    def save_edited_filter(self, filter_mixer, commit=True):
        edited_filter_mixer = self.instance

        edited_filter_mixer.compilation_holder = filter_mixer.compilation_holder

        edited_filter_mixer.posts_likes_minimum = parse_tags_from_input(self.cleaned_data["posts_likes_minimum"])
        edited_filter_mixer.posts_likes_expected = parse_tags_from_input(self.cleaned_data["posts_likes_expected"])
        edited_filter_mixer.source_compilation_holder = parse_tags_from_input(self.cleaned_data["source_compilation_holder"])
        edited_filter_mixer.priority = parse_tags_from_input(self.cleaned_data["priority"])

        if commit:
            edited_filter_mixer.save()

        return edited_filter_mixer

    class Meta:
        model = CompilationHolderFilterMixer
        exclude = ('compilation_holder_filter_id', 'compilation_holder', )


class CompilationHolderFilterMixerDeleteForm(forms.Form):
    compilation_holder_id = forms.IntegerField(required=True)

    def delete(self):
        filter_mixer_id = self.data["compilation_holder_filter_id"]
        CompilationHolderFilterMixer.objects.get(compilation_holder_filter_id=filter_mixer_id).delete()
