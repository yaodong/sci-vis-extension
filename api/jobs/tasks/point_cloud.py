from celery import shared_task, chord
from django.utils import timezone
from sympy import *
from celery import shared_task


@shared_task()
def compute_point_cloud(job_id, data_file):
    pass


@shared_task()
def create_job(job_id, ticket=None):
    from jobs.models import Job
    job = Job.objects.get(pk=job_id)
    job.started_at = timezone.now()
    job.percentage = 5
    job.save(update_fields=['started_at', 'percentage'])

    work_dir = prepare_work_dir(job, ticket)
    base_coordinates_file = download_base_coordinates(work_dir, job.inputs['file'])
    point_number = count_points(base_coordinates_file)

    base_distance_matrix = generate_distance_matrix(base_coordinates_file, point_number, 'base-dipha')
    base_dipha_out_file = dipha(base_distance_matrix)
    extract_persistence_diagram(base_dipha_out_file, 'base')

    chord(
        header=preparing_dipha_input_tasks(base_coordinates_file, point_number),
        body=dispath_dipha.s(job_id)
    ).apply_async()
