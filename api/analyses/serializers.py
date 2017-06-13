from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from analyses.models import Analysis
from datasets.models import Dataset


class AnalysisSerializer(serializers.ModelSerializer):

    dataset = ResourceRelatedField(
        queryset=Dataset.objects  # queryset argument is required
    )

    class Meta:
        model = Analysis
        fields = '__all__'
        validators = []
        depth = 2
