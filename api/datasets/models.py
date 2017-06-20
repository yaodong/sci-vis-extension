from django.db import models
from django.contrib.postgres.fields import JSONField


class Dataset(models.Model):
    name = models.CharField(max_length=128)
    file_name = models.CharField(max_length=32)
    file_meta = JSONField(null=True)
    format = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)
