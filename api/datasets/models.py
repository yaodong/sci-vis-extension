from django.db import models


class Dataset(models.Model):
    name = models.CharField(max_length=128)
    filename = models.CharField(max_length=32)
    format = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)
