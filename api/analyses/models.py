from django.db import models
from datasets.models import Dataset
from django.contrib.postgres.fields import JSONField


class Analysis(models.Model):
    name = models.CharField(max_length=64)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    params = JSONField(default={})
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)

    class Meta:
        ordering = ['-id']


class Item(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    value = JSONField(null=True)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)

    class Meta:
        unique_together = ('analysis', 'name')
