from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Job(models.Model):
    STATE_CHOICES = (
        (0, 'open'),
        (1, 'close'),
    )
    
    name = models.CharField(max_length=100, null=False)
    date = models.DateTimeField(auto_now_add=True)
    state = models.SmallIntegerField(choices=STATE_CHOICES, default=0)
    closed = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_time_open(self):
        if self.closed:
            time_open = (self.closed - self.date).days
        else:
            time_open = (timezone.now() - self.date).days
        return time_open


class Page(models.Model):
    STATE_CHOICES = (
        (0, 'open'),
        (1, 'approved'),
        (2, 'rejected'),
    )

    name = models.CharField(max_length=100, null=False)
    date = models.DateTimeField(auto_now_add=True)
    state = models.SmallIntegerField(choices=STATE_CHOICES, default=0)
    job = models.ForeignKey(Job, null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Version(models.Model):
    tag = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.tag


class Comentario(models.Model):
    version = models.ForeignKey(Version, on_delete=models.CASCADE, related_name='comentarios')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    texto = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.version.tag} - {self.user}'
