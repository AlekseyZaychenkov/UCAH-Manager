from django.db import models
from account.models import Account


class Schedule(models.Model):
    schedule_id                  = models.AutoField(primary_key=True)

    def __str__(self):
        return self.name


class ScheduleArchive(models.Model):
    schedule_id                  = models.AutoField(primary_key=True)

    def __str__(self):
        return self.name


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
    schedule_archive             = models.OneToOneField(ScheduleArchive, on_delete=models.CASCADE)

    # TODO: uncomment after changing field
    # description                  = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class CompilationHolder(models.Model):
    compilation_holder_id        = models.AutoField(primary_key=True)

    workspace                    = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    name                         = models.CharField(max_length=255)
    posts_per_download           = models.IntegerField()
    number_on_list               = models.IntegerField()
    compilation_id               = models.CharField(max_length=128)
    whitelisted_tags             = models.TextField(null=True, blank=True)
    selected_tags                = models.TextField(null=True, blank=True)
    blacklisted_tags             = models.TextField(null=True, blank=True)
    resources                    = models.CharField(max_length=4095, null=True, blank=True)
    description                  = models.TextField(null=True, blank=True)


class WhiteListedBlog(models.Model):
    whitelisted_blog_id          = models.AutoField(primary_key=True)
    compilation_holder           = models.ForeignKey(CompilationHolder, on_delete=models.CASCADE)


class SelectedBlog(models.Model):
    selected_blog_id             = models.AutoField(primary_key=True)
    compilation_holder           = models.ForeignKey(CompilationHolder, on_delete=models.CASCADE)


class BlackListedBlog(models.Model):
    blacklisted_blog_id          = models.AutoField(primary_key=True)
    compilation_holder           = models.ForeignKey(CompilationHolder, on_delete=models.CASCADE)


class ArchiveEvent(models.Model):
    event_id                     = models.AutoField(primary_key=True)
    schedule                     = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    post_id                      = models.CharField(max_length=128, null=True, blank=True)
    start_date                   = models.DateTimeField()


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


class Blog(models.Model):
    blog_id                      = models.AutoField(primary_key=True)
    name                         = models.CharField(max_length=255)
    avatar                       = models.CharField(max_length=2047, null=True)
    resource                     = models.CharField(max_length=63)
    blog_resource_number         = models.BigIntegerField(null=True, blank=True)
    workspace                    = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    controlled                   = models.BooleanField(default=False)
    account                      = models.ForeignKey(Account, on_delete=models.CASCADE)
    resource_account             = models.ForeignKey(ResourceAccount, on_delete=models.CASCADE, null=True, default=None)
    url                          = models.CharField(max_length=2047, null=True, blank=True)

    # TODO: figure out: Is it really need to have whitelisted and blacklisted blogs here?
    whitelisted_blog             = models.OneToOneField(WhiteListedBlog, on_delete=models.SET_NULL, null=True, blank=True)
    blacklisted_blog             = models.OneToOneField(BlackListedBlog, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return str(self.name) + " " + str(self.resource)


class Event(models.Model):
    event_id                     = models.AutoField(primary_key=True)
    schedule                     = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    blog                         = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True)
    post_id                      = models.CharField(max_length=128, null=True, blank=True)
    start_date                   = models.DateTimeField()


# TODO: implement special structure for storing
#  published each post in each blog with statistic about them
#  (postUrl1, likes, comments, likes under comments)
