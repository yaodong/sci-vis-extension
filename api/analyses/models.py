from django.db import models
from datasets.models import Dataset
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save


class Analysis(models.Model):
    title = models.CharField(max_length=64)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    params = JSONField(default={})
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)

    class Meta:
        ordering = ['-id']

    @property
    def contexts(self):
        return ContextHandler(self)


def create_background_job(sender, instance, created, **kwargs):
    from analyses.tasks import analysis_process
    if created:
        analysis_process.delay(instance.id)


post_save.connect(create_background_job, sender=Analysis)


class Context(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    value = JSONField(null=True)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)

    class Meta:
        unique_together = ('analysis', 'name')


UNDEFINED_CONTEXT_PLACEHOLDER = '__undefined_context_placeholder__'


class ContextHandler(object):
    def __init__(self, analysis):
        self.analysis = analysis

    def write(self, name, value):
        try:
            context = self.query().filter(name=name).get()
            context.value = value
        except Context.DoesNotExist:
            context = Context(analysis=self.analysis, name=name, value=value)

        context.save()

    def read(self, name, default=UNDEFINED_CONTEXT_PLACEHOLDER):
        try:
            context = self.query().filter(name=name).get()
            return context.value
        except Context.DoesNotExist:
            if default != UNDEFINED_CONTEXT_PLACEHOLDER:
                return default
            else:
                raise RuntimeError()

    def remove_all(self):
        self.query().delete()

    def query(self):
        return Context.objects.filter(analysis_id=self.analysis.id)
