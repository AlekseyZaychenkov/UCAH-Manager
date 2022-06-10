from django.db import models
from account.models import Account


class Schedule(models.Model):
    schedule_id     = models.AutoField(primary_key=True)
    compilation_id  = models.CharField(max_length=128, null=True, blank=True)
    post_id         = models.CharField(max_length=128, null=True, blank=True)
    name            = models.CharField(max_length=255)
    owner           = models.ForeignKey(Account, on_delete=models.CASCADE)
    visible_for     = models.ManyToManyField(Account, related_name="visible_for")
    editable_by     = models.ManyToManyField(Account, related_name="editable_by")

    def __str__(self):
        return self.name


class Event(models.Model):
    TYPE_CHOICES = [
        ("AR", 'Arbeit'),
        ("FR", 'Freizeit'),
    ]
    event_id        = models.AutoField(primary_key=True)
    schedule        = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    post_id         = models.CharField(max_length=128, null=True, blank=True)
    name            = models.CharField(max_length=255, null=True, blank=True)
    start_date      = models.DateTimeField()
    end_date        = models.DateTimeField(null=True, blank=True)
    event_type      = models.CharField(max_length=2, choices=TYPE_CHOICES, default="FR")

    def __str__(self):
        return self.name