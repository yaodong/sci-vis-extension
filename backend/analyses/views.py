from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from analyses.models import Analysis
from analyses.serializers import AnalysisSerializer
from datasets.serializers import DatasetSerializer
from analyses import queries
import re


class AnalysisViewSet(viewsets.ModelViewSet):
    queryset = Analysis.objects.all()
    serializer_class = AnalysisSerializer

    filter_backends = (filters.OrderingFilter, filters.SearchFilter)

    search_fields = ('title',)
    ordering_fields = ('id',)
    ordering = ('-id',)

    def create(self, request, *args, **kwargs):
        print('=' * 20)
        dataset = DatasetSerializer(request.data['dataset'])

        print(dataset)
        print('=' * 20)

        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Analysis.objects.all()

        dataset_id = self.request.query_params.get('dataset', None)
        if dataset_id is not None:
            queryset = queryset.filter(dataset_id=dataset_id)

        return queryset


@api_view(['POST'])
def query(request):
    data = request.data

    if 'analysis_id' not in data:
        raise RuntimeError('Unknown analysis id')

    if 'function' not in data:
        raise RuntimeError('No function name provide')

    analysis = Analysis.objects.get(pk=data['analysis_id'])
    func = getattr(queries, data['function'])

    if not callable(func):
        raise RuntimeError('Not callable')

    result = func(analysis, **data.get('arguments', {}))

    return Response(result)
