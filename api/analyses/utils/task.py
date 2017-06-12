from os import path, makedirs
from shutil import rmtree
from django.conf import settings
import requests
import logging

__all__ = ['get_analysis_object', 'fetch_file_meta', 'task_prepare_dir', 'task_download_dataset']


def get_analysis_object(analysis_id):
    from analyses.models import Analysis
    return analysis.objects.get(pk=analysis_id)


def task_prepare_dir(analysis_id):
    work_dir = path.join(settings.DATA_DIR, 'analyses', str(analysis_id))

    if path.isdir(work_dir):
        rmtree(work_dir)

    makedirs(work_dir)

    return work_dir


def fetch_file_meta(file_id):
    file_meta_url = 'https://www.filestackapi.com/api/file/%s/metadata' % file_id
    return requests.get(file_meta_url).json()


def task_download_dataset(file_id, local_file_path, meta_data):
    file_download_url = 'https://www.filestackapi.com/api/file/%s?dl=true' % file_id

    req = requests.get(file_download_url, stream=True)
    with open(local_file_path, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    logging.info('base coordinates downloaded')
    return local_file_path
