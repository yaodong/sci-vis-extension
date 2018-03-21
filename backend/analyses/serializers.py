from rest_framework_json_api import serializers
from analyses.models import Analysis
from datasets.models import Dataset


class AnalysisSerializer(serializers.ModelSerializer):

    dataset = serializers.PrimaryKeyRelatedField(
        queryset=Dataset.objects
    )

    class Meta:
        model = Analysis
        fields = '__all__'
        validators = []
        depth = 2
