from django.db import models
from account.models import Account


class Schedule(models.Model):
    schedule_id                 = models.AutoField(primary_key=True)
    name                        = models.CharField(max_length=255)
    owner                       = models.ForeignKey(Account, on_delete=models.CASCADE)
    visible_for                 = models.ManyToManyField(Account, related_name="visible_for")
    editable_by                 = models.ManyToManyField(Account, related_name="editable_by")

    # workspace
    scheduled_compilation_id    = models.CharField(max_length=128)
    main_compilation_id         = models.CharField(max_length=128)
    main_compilation_archive_id = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Workspace(models.Model):
    workspace_id                = models.AutoField(primary_key=True)
    name                        = models.CharField(max_length=255)
    owner                       = models.ForeignKey(Account, on_delete=models.CASCADE)
    visible_for                 = models.ManyToManyField(Account, related_name="visible_for")
    editable_by                 = models.ManyToManyField(Account, related_name="editable_by")

    scheduled_compilation_id    = models.CharField(max_length=128)
    main_compilation_id         = models.CharField(max_length=128)
    main_compilation_archive_id = models.CharField(max_length=128)

    # TODO: delete after creating Schedule and ScheduleArchive and foreign keys
    schedule_id                 = models.CharField(max_length=255)
    schedulearchive_id           = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Schedule(models.Model):
    schedule_id                 = models.AutoField(primary_key=True)
    workspace                   = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ScheduleArchive(models.Model):
    schedule_id                 = models.AutoField(primary_key=True)
    workspace                   = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Event(models.Model):
    # TODO: remove
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


class ArchiveEvent(models.Model):
    # TODO: remove
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


class Blog(models.Model):
    blog_id         = models.AutoField(primary_key=True)
    workspace       = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    resource        = models.CharField(max_length=63, null=True, blank=True)
    name            = models.CharField(max_length=255, null=True, blank=True)
    url             = models.CharField(max_length=2048, null=True, blank=True)
    owner_url       = models.CharField(max_length=255, null=True, blank=True)
    owner_nickname  = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Credentials(models.Model):
    credentials_id  = models.AutoField(primary_key=True)
    owner           = models.ForeignKey(Account, on_delete=models.CASCADE)
    name            = models.CharField(max_length=255, null=True, blank=True)
    resource        = models.CharField(max_length=63, null=True, blank=True)
    login           = models.CharField(max_length=255, null=True, blank=True)
    password        = models.CharField(max_length=255, null=True, blank=True)
    consumer_key    = models.CharField(max_length=255, null=True, blank=True)
    consumer_secret = models.CharField(max_length=255, null=True, blank=True)
    token           = models.CharField(max_length=255, null=True, blank=True)
    secret          = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name