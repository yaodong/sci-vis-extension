from rest_framework import viewsets
from analyses.models import Analysis
from analyses.serializers import AnalysisSerializer
from datasets.serializers import DatasetSerializer


class AnalysisViewSet(viewsets.ModelViewSet):
    queryset = Analysis.objects.all()
    serializer_class = AnalysisSerializer

    def create(self, request, *args, **kwargs):

        print('=' * 20)
        dataset = DatasetSerializer(request.data['dataset'])

        print(dataset)
        print('=' * 20)



        return super().create(request, *args, **kwargs)
