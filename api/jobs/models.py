from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from jobs.tasks import create_job


class Job(models.Model):
    name = models.CharField(max_length=128)
    method = models.CharField(max_length=64)
    inputs = JSONField(default={})
    outputs = JSONField(default={})
    percentage = models.FloatField(default=0.)
    status = models.IntegerField(null=True)
    ticket = models.CharField(max_length=128, null=True)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)

    class Meta:
        ordering = ['-id']


def create_background_job(sender, instance, created, **kwargs):
    if created:
        create_job.delay(instance.id)


post_save.connect(create_background_job, sender=Job)
