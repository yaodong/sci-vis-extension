from rest_framework import viewsets
from rest_framework.response import Response
from analyses.models import Analysis
from queries.composers import composer_map
import re


class QueryViewSet(viewsets.ViewSet):

    key_name_test = re.compile('^([0-9]+)--([a-z0-9][a-z0-9-]+[a-z0-9])$')

    def list(self, request):
        return Response([])

    def retrieve(self, request, pk=None):
        return Response({
            "id": pk,
            "content": self.compose(pk)})

    def compose(self, pk):
        matches = self.key_name_test.match(pk)

        if not matches:
            return {'error': 'Invalid query item'}

        pk, item = matches.groups()
        analysis = Analysis.objects.get(pk=pk)
        composer_class = composer_map.get(analysis.params['process'], None)

        if not composer_class:
            return {'error': 'Invalid process type'}

        composer = composer_class(analysis)
        func = getattr(composer, 'query_%s' % item.replace('-', '_'), None)
        if func:
            return func()
        else:
            return {'error': 'Invalid query item function'}
