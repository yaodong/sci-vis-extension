from os import path
from celery import shared_task
from jobs.utils.job import job_prepare_work_dir, job_download_data_file, job_get, get_file_meta
from jobs.tasks.point_cloud import compute_point_cloud
from jobs.tasks.graph import compute_graph

SUPPORTED_FILE_TYPES = [
    'text/tab-separated-values',
    'text/csv',
]


@shared_task()
def dispatch_computing(job_id):
    job = job_get(job_id)
    job.progress = 1
    job.status = job.STATUS_STARTED

    file_id = job.param('file')
    file_meta = get_file_meta(file_id)
    job.params['file_meta'] = file_meta

    if file_meta['mimetype'] not in SUPPORTED_FILE_TYPES:
        raise Exception("invalid base coordinates")

    job.save()

    work_dir = job_prepare_work_dir(job)
    data_file_path = path.join(work_dir, 'base.dat')
    job_download_data_file(job.param('file'), data_file_path, file_meta)

    data_format = job.param('data_format')

    if data_format == 'point_cloud':
        computing_handler = compute_point_cloud
    elif data_format == 'graph':
        computing_handler = compute_graph
    else:
        raise RuntimeError('unknown data format')

    computing_handler.delay(job.id, data_file_path)
