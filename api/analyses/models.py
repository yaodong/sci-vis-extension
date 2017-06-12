from django.db import models
from datasets.models import Dataset
from django.contrib.postgres.fields import JSONField
from analyses.process import analysis_process
from django.db.models.signals import post_save


class Analysis(models.Model):
    title = models.CharField(max_length=64)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    params = JSONField(default={})
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)

    class Meta:
        ordering = ['-id']

def create_background_job(sender, instance, created, **kwargs):
    if created:
        analysis_process(instance.id)

post_save.connect(create_background_job, sender=Analysis)

class Item(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    value = JSONField(null=True)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)

    class Meta:
        unique_together = ('analysis', 'name')

