import logging

from django import forms

from workspace_editor.services.text_services import parse_tags_from_input
from workspace_editor.models import *

log = logging.getLogger(__name__)


class BlogAddTagRuleForm(forms.ModelForm):
    blog_id = forms.IntegerField(required=True)
    tag_rule_id = forms.IntegerField(required=True)
    apply = forms.BooleanField(required=False)

    def save(self, commit=True):
        data = self.cleaned_data
        blog = Blog.objects.get(blog_id=data.get("blog_id"))
        tag_rule = TagRule.objects.get(tag_rule_id=data.get("tag_rule_id"))

        if bool(data.get("apply")):
            blog.tag_rule.add(tag_rule)
        else:
            blog.tag_rule.remove(tag_rule)

        if commit:
            blog.save()
    class Meta:
        model = Blog
        exclude = ('name', 'avatar', 'resource', 'blog_resource_number',
                   'workspace', 'url', 'controlled', 'tag_rule', 'account', 'resource_account', )


class TagRuleCreateForm(forms.ModelForm):
    event_rules_id = forms.IntegerField(required=True)
    input = forms.CharField(required=False)
    output = forms.CharField(required=False)
    for_all = forms.BooleanField(required=False)

    def save(self, commit=True):
        tag_rule = self.instance
        data = self.cleaned_data
        event_rules = EventRules.objects.get(event_rules_id=data.get("event_rules_id"))
        tag_rule.event_rules = event_rules
        tag_rule.input = parse_tags_from_input(data.get("input"))
        tag_rule.output = parse_tags_from_input(data.get("output"))

        if commit:
            tag_rule.save()
            return tag_rule

    class Meta:
        model = TagRule
        exclude = ('event_rules', )


class TagRuleDeleteForm(forms.Form):
    id = forms.IntegerField(required=True)

    def delete(self):
        data = self.cleaned_data
        tag_rule = TagRule.objects.get(tag_rule_id=data.get("id"))
        tag_rule.delete()

class PostingTimeEditForm(forms.ModelForm):
    posting_time_id = forms.IntegerField(required=True)
    time = forms.TimeField(required=False)

    def save(self, commit=True):
        data = self.cleaned_data
        posting_time = PostingTime.objects.get(posting_time_id=data.get("posting_time_id"))
        posting_time.time = data.get("time")

        if commit:
            posting_time.save()

    class Meta:
        model = PostingTime
        exclude = ('priority', 'event_rules',)


class EventRulesEditForm(forms.ModelForm):
    event_rules_id = forms.CharField(required=True)
    distribution_type = forms.ChoiceField(choices=EventRules.DISTRIBUTION_TYPE_CHOICES)
    start_type = forms.ChoiceField(choices=EventRules.START_TYPE_CHOICES)

    def save(self, commit=True):
        data = self.cleaned_data
        events_rules = EventRules.objects.get(event_rules_id=data.get("event_rules_id"))

        events_rules.distribution_type = data.get("distribution_type")
        events_rules.start_type = data.get("start_type")

        if commit:
            events_rules.save()


    class Meta:
        model = EventRules
        exclude = ('input_tag', 'output_tag',)
