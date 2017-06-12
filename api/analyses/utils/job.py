from os import path, makedirs
from shutil import rmtree
from django.conf import settings
import requests
import logging

BASE_COORDINATE_FILENAME = 'base.tsv'

def job_get(job_id):
    from jobs.models import Job
    return Job.objects.get(pk=job_id)


def job_prepare_work_dir(job):
    work_dir = path.join(settings.DATA_DIR, 'jobs', str(job.id))

    if path.isdir(work_dir):
        rmtree(work_dir)

    makedirs(work_dir)

    return work_dir


def get_file_meta(file_id):
    file_meta_url = 'https://www.filestackapi.com/api/file/%s/metadata' % file_id
    return requests.get(file_meta_url).json()


def job_download_data_file(file_id, local_file_path, meta_data):
    file_download_url = 'https://www.filestackapi.com/api/file/%s?dl=true' % file_id

    req = requests.get(file_download_url, stream=True)
    with open(local_file_path, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    logging.info('base coordinates downloaded')
    return local_file_path
