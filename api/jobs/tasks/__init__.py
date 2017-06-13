from os import path
from celery import shared_task
from analyses.utils.job import *
from analyses.utils.point_cloud import compute_point_cloud
from analyses.utils.graph import compute_graph

SUPPORTED_FILE_TYPES = [
    'text/csv',
]


@shared_task()
def dispatch_computing(analysis_id):
    analysis = get_analysis_object(analysis_id)

    file_name = analysis.dataset.file_name
    file_meta = fetch_file_mate(file_name)

    if file_meta['mimetype'] not in SUPPORTED_FILE_TYPES:
        raise Exception("invalid base coordinates")

    work_dir = task_prepare_dir(analysis.id)
    data_file_path = path.join(work_dir, 'base.dat')


    task_download_dataset(job.param('file'), data_file_path)

    data_format = job.param('data_format')

    if data_format == 'point_cloud':
        computing_handler = compute_point_cloud
    elif data_format == 'graph':
        computing_handler = compute_graph
    else:
        raise RuntimeError('unknown data format')

    computing_handler.delay(job.id, data_file_path)
