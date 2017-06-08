from rest_framework import viewsets
from datasets.models import Dataset
from datasets.serializers import DatasetSerializer


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
