from rest_framework_json_api import serializers
from datasets.models import Dataset
import requests


class DatasetSerializer(serializers.ModelSerializer):

    FILE_META_URL_TPL = 'https://www.filestackapi.com/api/file/%s/metadata'

    class Meta:
        model = Dataset
        fields = '__all__'
        validators = []

    def create(self, validated_data):
        file_name = validated_data.get('file_name')
        file_meta_url = self.FILE_META_URL_TPL % file_name

        file_meta = requests.get(file_meta_url).json()
        validated_data['file_meta'] = file_meta

        return super().create(validated_data)
