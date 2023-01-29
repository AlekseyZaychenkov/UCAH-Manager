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
        exclude = ('', )


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
