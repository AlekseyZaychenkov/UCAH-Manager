import logging

from django import forms

from workspace_editor.models import *

log = logging.getLogger(__name__)



class TagRuleCreateForm(forms.ModelForm):
    input_tag = forms.CharField(required=False)
    output_tag = forms.CharField(required=False)
    events_rules = forms.CharField(required=True)

    class Meta:
        model = TagRule
        # exclude = ()


class PostingTimeCreateForm(forms.ModelForm):
    time = forms.TimeField(required=True)
    events_rules = forms.CharField(required=True)
    priority = forms.IntegerField(required=True)

    class Meta:
        model = PostingTime


class EventRulesEditForm(forms.ModelForm):
    input_tag = forms.CharField(required=False)
    output_tag = forms.CharField(required=False)
    events_rules = forms.CharField(required=True)
    distribution_type = forms.ChoiceField(choices=TagRule.DISTRIBUTION_TYPE_CHOICES)
    start_from_first_free_date = forms.BooleanField()

    class Meta:
        model = EventRules