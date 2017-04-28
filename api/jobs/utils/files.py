from os import path, makedirs
from shutil import rmtree
from django.conf import settings
import requests
import logging

BASE_COORDINATE_FILENAME = 'base.tsv'


def make_work_folder(job):
    work_dir = path.join(settings.DATA_DIR, 'jobs', str(job.id))

    if path.isdir(work_dir):
        rmtree(work_dir)

    makedirs(work_dir)

    return work_dir


def download_data_file(work_dir, file_id):
    file_path = path.join(work_dir, BASE_COORDINATE_FILENAME)

    if path.isfile(file_path):
        logging.info('skip downloading coordinates')
        return file_path

    file_meta_url = 'https://www.filestackapi.com/api/file/%s/metadata' % file_id
    file_download_url = 'https://www.filestackapi.com/api/file/%s?dl=true' % file_id

    meta_data = requests.get(file_meta_url).json()
    if meta_data['mimetype'] != 'text/tab-separated-values':
        raise Exception("invalid base coordinates")

    req = requests.get(file_download_url, stream=True)
    with open(file_path, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    logging.info('base coordinates downloaded')
    return file_path


def count_file_lines(file):
    with open(file) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
