from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse


ACCOUNT_TYPE = [
        ('st', 'Standard'),
        ('pr', 'Premium'),
        ('n', 'None'),
        ]


class NairalandAccount(models.Model):
    username = models.CharField(max_length=60)
    password = models.CharField(max_length=60)
    has_job = models.BooleanField(default=False)

    def __str__(self):
        return self.username


    def get_absolute_url(self):
        return reverse('nairaland-account-detail', kwargs = {'pk':self.pk})






class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    activated = models.BooleanField(default=False)
    account_type = models.CharField(max_length=2, choices=ACCOUNT_TYPE, default='n')
    license_key = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username



class BoardReplyJob(models.Model):
    board_name = models.CharField(max_length=60)
    board_uri = models.CharField(max_length=200)
    reply = models.TextField()
    activated = models.BooleanField(default=False)
    nl_account_pk = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f' {self.board_name} reply job'

    def get_absolute_url(self):
        return reverse('boardreplyjob-detail', kwargs = {'pk':self.pk})


class ThreadReplyJob(models.Model):
    thread_title = models.CharField(max_length=200)
    reply = models.TextField()
    topic_code = models.PositiveIntegerField()
    activated = models.BooleanField(default=False)
    nl_account_pk = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.thread_title


    def get_absolute_url(self):
        return reverse('threadreplyjob-detail', kwargs = {'pk':self.pk})



class FrontPageMonitorJob(models.Model):
    board_name = models.CharField(max_length=60, default="Frontpage")
    board_uri = models.CharField(max_length=200, default="https://www.nairaland.com/")
    reply = models.TextField()
    activated = models.BooleanField(default=False)
    nl_account_pk = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f' {self.board_name} {self.pk} reply job'

    def get_absolute_url(self):
        return reverse('frontpagemonitorjob-detail', kwargs = {'pk':self.pk})




@receiver(user_logged_in)
def createProfile(sender, user, request, **kwargs):
    try:
        if user.profile:
            pass
    except ObjectDoesNotExist:
        profile = Profile.objects.create(
                user=user,
                activated=False,
                account_type='n',)
        profile.save()





