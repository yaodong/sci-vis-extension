from rest_framework import viewsets
from jobs.models import Job
from jobs.serializers import JobSerializer


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
