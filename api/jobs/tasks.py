from os import path, mkdir, chdir, listdir
from celery import shared_task
from singer.settings import BASE_DIR
from math import sin, cos, pi
from datetime import datetime


def rotate(row, angle, dim1, dim2):
    radian = angle * pi / 180.
    cos_alpha, sin_alpha = cos(radian), sin(radian)
    x, y = row[dim1], row[dim2]
    row[dim1] = cos_alpha * x - sin_alpha * y
    row[dim2] = sin_alpha * x + cos_alpha * y
    return row


@shared_task()
def create_job(instance_id):
    from subprocess import Popen, PIPE
    from jobs.models import Job
    import time
    import requests

    job = Job.objects.get(pk=instance_id)
    job.started_at = datetime.now()
    job.save(update_fields=['started_at'])

    file_id = job.inputs['file']
    file_meta_url = 'https://www.filestackapi.com/api/file/%s/metadata' % file_id
    file_download_url = 'https://www.filestackapi.com/api/file/%s?dl=true' % file_id
    dir_id = '%s_%s' % (job.id, time.time())
    job_dir = path.join(BASE_DIR, 'tmp', dir_id)

    meta_data = requests.get(file_meta_url).json()
    if meta_data['mimetype'] != 'text/csv':
        return

    mkdir(job_dir)
    mkdir(path.join(job_dir, 'distance'))
    mkdir(path.join(job_dir, 'rotated'))
    mkdir(path.join(job_dir, 'preview'))

    # download file
    base_file_path = path.join(job_dir, 'base.csv')

    r = requests.get(file_download_url, stream=True)

    with open(base_file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    r.close()

    # create rotated xyz
    angle_range = range(-90, 90, 5)

    for zx_angle in angle_range:
        for zy_angle in angle_range:
            rotated_file = path.join(job_dir, 'rotated', '%s__%s.csv' % (zx_angle, zy_angle))

            create_preview_image.delay(zx_angle, zy_angle, path.join(job_dir, 'preview'), rotated_file)

            with open(base_file_path) as f, open(rotated_file, 'w') as rf:
                for line in f:
                    row = [float(i) for i in line.strip().split(',')]

                    rotated_row = rotate(row, zx_angle, dim1=0, dim2=1)
                    rotated_row = rotate(rotated_row, zy_angle, dim1=0, dim2=2)
                    rf.write('{},{},{}\n'.format(*[round(i, 6) for i in rotated_row]))

    # computing all bottleneck distance
    chdir(path.join(BASE_DIR, 'scripts'))
    distance_dir = path.join(job_dir, 'distance')
    total_angles = pow(len(angle_range), 2)

    command = 'Rscript calc.r %s' % dir_id
    p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    while p.poll() is None:
        result_file_count = len([name for name in listdir(distance_dir) if path.isfile(path.join(distance_dir, name))])
        percentage = round(result_file_count / total_angles * (95 - 10) + 10, 3)
        job.percentage = percentage
        job.save(update_fields=['percentage'])
        time.sleep(10)

    job.percentage = 95
    job.status = p.returncode
    job.completed_at = datetime.now()
    job.save(update_fields=['percentage', 'status', 'completed_at'])

    # find best projection direction
    results = []
    for zy_angle in angle_range:
        for zx_angle in angle_range:
            result_file = path.join(job_dir, 'distance', '%s__%s.txt' % (zx_angle, zy_angle))
            value = float(open(result_file).read())
            results.append([zx_angle, zy_angle, value])

    job.percentage = 100
    job.outputs = {
        'best_projection': min(results, key=lambda p: p[2]),
        'worst_projection': max(results, key=lambda p: p[2]),
        'bottleneck_distances': results,
    }
    job.save()


@shared_task()
def create_preview_image(zx_angle, zy_angle, preview_dir, file):
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Qt5Agg')
    plt.axis('equal')

    fig = plt.figure()
    ax = fig.add_subplot(111)

    with open(file) as f:
        for line in f:
            x, y, z = line.rstrip().split(',')
            ax.scatter(x, y)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    plt.savefig(path.join(preview_dir, '%s__%s.png' % (zx_angle, zy_angle)))
