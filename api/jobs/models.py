from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from jobs.tasks import dispatch_computing


class Job(models.Model):
    STATUS_SUBMITTED = -2
    STATUS_STARTED = -1
    STATUS_DONE = 0
    STATUS_ERROR = 1

    name = models.CharField(max_length=128)
    params = JSONField(default={})
    status = models.IntegerField(default=STATUS_SUBMITTED)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def param(self, name):
        return self.params.get(name)

    def output(self, name, value):
        pass


class JobOutput(models.Model):
    job = models.ForeignKey(Job, null=False)
    name = models.CharField(max_length=128)
    value = JSONField(default=None)

    class Meta:
        unique_together = ('job', 'name')


def create_background_job(sender, instance, created, **kwargs):
    if created:
        dispatch_computing.delay(instance.id)


post_save.connect(create_background_job, sender=Job)
