from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from datasets.models import Dataset
# from jobs.tasks import dispatch_computing


class Job(models.Model):
    name = models.CharField(max_length=128)
    params = JSONField(default={})

    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def param(self, name):
        return self.params.get(name)

    def update_progress(self, percentage):
        self.progress = percentage
        self.save()


# def create_background_job(sender, instance, created, **kwargs):
#     if created:
#         dispatch_computing.delay(instance.id)
#
#
# post_save.connect(create_background_job, sender=Job)
