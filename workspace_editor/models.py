from django.db import models
from account.models import Account
from django.db.models.signals import post_delete
from django.dispatch import receiver


class Schedule(models.Model):
    schedule_id                  = models.AutoField(primary_key=True)


class ScheduleArchived(models.Model):
    schedule_id                  = models.AutoField(primary_key=True)


class EventRules(models.Model):
    event_rules_id              = models.AutoField(primary_key=True)
    DISTRIBUTION_TYPE_CHOICES = (
        (1.0, "1 per day"),
        (2.0, "2 per day"),
        (3.0, "3 per day"),
        (4.0, "4 per day"),
        (5.0, "5 per day"),
        (6.0, "6 per day"),
        (0.333, "over 3 days"),
        (0.142, "over 1 week"),
        (0.071, "over 1 weeks"),
        (0.033, "over 1 month"),
        (0.016, "over 2 months"),
        (0.011, "over 3 months"),
    )
    distribution_type            = models.FloatField(max_length=12,
                                                     choices=DISTRIBUTION_TYPE_CHOICES,
                                                     default="over 1 week")
    START_TYPE_CHOICES = (
        ("Add to empty slots", "Add to empty slots"),
    )
    start_type                   = models.CharField(max_length=20,
                                                    choices=START_TYPE_CHOICES,
                                                    default="Add to empty slots")


class TagRule(models.Model):
    tag_rule_id                  = models.AutoField(primary_key=True)
    event_rules                  = models.ForeignKey(EventRules, on_delete=models.CASCADE)
    input                        = models.CharField(max_length=4095, default='', blank=True)
    output                       = models.CharField(max_length=4095, default='', blank=True)
    for_all                      = models.BooleanField(default=False)


class PostingTime(models.Model):
    posting_time_id             = models.AutoField(primary_key=True)
    time                        = models.TimeField()
    event_rules                 = models.ForeignKey(EventRules, on_delete=models.CASCADE)
    priority                    = models.IntegerField()


class Workspace(models.Model):
    workspace_id                 = models.AutoField(primary_key=True)
    name                         = models.CharField(max_length=255)
    owner                        = models.ForeignKey(Account, on_delete=models.CASCADE)
    visible_for                  = models.ManyToManyField(Account, related_name="visible_for")
    editable_by                  = models.ManyToManyField(Account, related_name="editable_by")

    scheduled_compilation_id     = models.CharField(max_length=128)
    main_compilation_id          = models.CharField(max_length=128)
    main_compilation_archive_id  = models.CharField(max_length=128)

    schedule                     = models.OneToOneField(Schedule, on_delete=models.CASCADE)
    schedule_archive             = models.OneToOneField(ScheduleArchived, on_delete=models.CASCADE, null=True)

    event_rules                  = models.OneToOneField(EventRules, on_delete=models.CASCADE)

    description                  = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

@receiver(post_delete, sender=Workspace)
def auto_delete_schedules_and_event_rules_with_workspace(sender, instance, **kwargs):
    instance.schedule.delete()
    instance.schedule_archive.delete()
    instance.event_rules.delete()


class CompilationHolder(models.Model):
    compilation_holder_id        = models.AutoField(primary_key=True)
    workspace                    = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    compilation_id               = models.CharField(max_length=128)
    name                         = models.CharField(max_length=255)

    posts_per_download           = models.IntegerField()
    number_on_list               = models.IntegerField()
    whitelisted_tags             = models.TextField(null=True, blank=True)
    selected_tags                = models.TextField(null=True, blank=True)
    blacklisted_tags             = models.TextField(null=True, blank=True)
    resources                    = models.CharField(max_length=4095, null=True, blank=True)

    recipient                    = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    keep_posts_after_sending     = models.BooleanField(default=False)

    description                  = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class WhiteListedBlog(models.Model):
    whitelisted_blog_id          = models.AutoField(primary_key=True)
    compilation_holder           = models.ForeignKey(CompilationHolder, on_delete=models.CASCADE)


class SelectedBlog(models.Model):
    selected_blog_id             = models.AutoField(primary_key=True)
    compilation_holder           = models.ForeignKey(CompilationHolder, on_delete=models.CASCADE)


class BlackListedBlog(models.Model):
    blacklisted_blog_id          = models.AutoField(primary_key=True)
    compilation_holder           = models.ForeignKey(CompilationHolder, on_delete=models.CASCADE)


class EventArchived(models.Model):
    event_id                     = models.AutoField(primary_key=True)
    schedule                     = models.ForeignKey(ScheduleArchived, on_delete=models.CASCADE)
    post_id                      = models.CharField(max_length=128, null=True, blank=True)
    datetime                     = models.DateTimeField()


class Credentials(models.Model):
    credentials_id               = models.AutoField(primary_key=True)
    resource                     = models.CharField(max_length=63, null=True, blank=True)
    login                        = models.CharField(max_length=255, null=True, blank=True)
    password                     = models.CharField(max_length=255, null=True, blank=True)
    consumer_key                 = models.CharField(max_length=255, null=True, blank=True)
    consumer_secret              = models.CharField(max_length=255, null=True, blank=True)
    token                        = models.CharField(max_length=255, null=True, blank=True)
    secret                       = models.CharField(max_length=255, null=True, blank=True)


class ResourceAccount(models.Model):
    resource_account_id = models.AutoField(primary_key=True)
    name                = models.CharField(max_length=255, null=True, blank=True)
    owner               = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, default=False)
    avatar              = models.ImageField(null=True)
    credentials         = models.OneToOneField(Credentials, on_delete=models.CASCADE, null=True, default=False)
    url                 = models.CharField(max_length=255, null=True, blank=True)

@receiver(post_delete, sender=ResourceAccount)
def auto_delete_credentials_with_resource_account(sender, instance, **kwargs):
    instance.credentials.delete()


class Blog(models.Model):
    blog_id                      = models.AutoField(primary_key=True)
    name                         = models.CharField(max_length=255)
    avatar                       = models.CharField(max_length=2047, null=True)
    resource                     = models.CharField(max_length=63)
    blog_resource_number         = models.BigIntegerField(null=True, blank=True)
    workspace                    = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    url                          = models.CharField(max_length=2047, null=True, blank=True)

    controlled                   = models.BooleanField(default=False)
    tag_rule                     = models.ManyToManyField(TagRule)
    account                      = models.ForeignKey(Account, on_delete=models.CASCADE)
    resource_account             = models.ForeignKey(ResourceAccount, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return str(self.name) + " " + str(self.resource)


class Event(models.Model):
    event_id                     = models.AutoField(primary_key=True)
    schedule                     = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    blogs                        = models.ManyToManyField(Blog)
    post_id                      = models.CharField(max_length=128, null=True, blank=True)
    datetime                     = models.DateTimeField()


# TODO: implement special structure for storing
#  published each post in each blog with statistic about them
#  (postUrl1, likes, comments, likes under comments)
