from os import path, mkdir, chdir, listdir, makedirs
from celery import shared_task
from math import sin, cos, pi
from django.conf import settings
from django.utils import timezone
import time
import requests


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
    from time import sleep

    job = Job.objects.get(pk=instance_id)
    job.started_at = timezone.now()
    job.percentage = 5
    job.save(update_fields=['started_at', 'percentage'])

    # dir
    job.ticket = '%s_%s' % (job.id, int(time.time()))
    job.save(update_fields=['ticket'])
    work_dir = path.join(settings.DATA_DIR, 'jobs', job.ticket)
    makedirs(work_dir)

    # prepare dir
    distance_dir = path.join(work_dir, 'distance')
    rotated_dir = path.join(work_dir, 'rotated')
    image_dir = path.join(work_dir, 'images')
    mkdir(distance_dir)
    mkdir(rotated_dir)
    mkdir(image_dir)

    # download data file
    file_id = job.inputs['file']
    file_meta_url = 'https://www.filestackapi.com/api/file/%s/metadata' % file_id
    file_download_url = 'https://www.filestackapi.com/api/file/%s?dl=true' % file_id

    meta_data = requests.get(file_meta_url).json()
    if meta_data['mimetype'] != 'text/csv':
        return

    base_file_path = path.join(work_dir, 'base.csv')
    r = requests.get(file_download_url, stream=True)
    with open(base_file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    # create 3d preview image
    create_3d_preview_image(image_dir, base_file_path)

    # process angles
    chdir(path.join(settings.BASE_DIR, 'scripts'))

    angle_range = range(-90, 90, 5)
    total_angles = pow(len(angle_range), 2)

    count = 0
    for zx_angle in angle_range:
        for zy_angle in angle_range:
            print(['=', zx_angle, zy_angle])

            rotated_file = path.join(rotated_dir, '%s__%s.csv' % (zx_angle, zy_angle))

            with open(base_file_path) as f, open(rotated_file, 'w') as rf:
                for line in f:
                    row = [float(i) for i in line.strip().split(',')]

                    rotated_row = rotate(row, zx_angle, dim1=0, dim2=1)
                    rotated_row = rotate(rotated_row, zy_angle, dim1=0, dim2=2)
                    rf.write('{},{},{}\n'.format(*[round(i, 6) for i in rotated_row]))

            command = 'Rscript calc.r %s %s %s' % (work_dir, zx_angle, zy_angle)
            p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)

            # create preview image before checking sub process status
            create_preview_image(zx_angle, zy_angle, image_dir, rotated_file)

            while p.poll() is None:
                sleep(1)

            if p.returncode != 0:
                raise "error"

            count += 1
            job.percentage = round(5 + count / total_angles * 95, 2)
            job.save(update_fields=['percentage'])

    # find best direction
    results = []
    for zy_angle in angle_range:
        for zx_angle in angle_range:
            result_file = path.join(distance_dir, '%s__%s.txt' % (zx_angle, zy_angle))
            value = float(open(result_file).read())
            results.append([zx_angle, zy_angle, value])

    job.status = 0
    job.percentage = 100
    job.outputs = {
        'best_projection': min(results, key=lambda item: item[2]),
        'worst_projection': max(results, key=lambda item: item[2]),
        'bottleneck_distances': results,
    }
    job.save()


def create_preview_image(zx_angle, zy_angle, preview_dir, file):
    import matplotlib.pyplot as plt
    plt.axis('equal')

    fig = plt.figure()
    ax = fig.add_subplot(111)

    with open(file) as f:
        for line in f:
            x, y, z = line.rstrip().split(',')
            ax.scatter(x, y, s=2, alpha=0.7, c="m")

    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    plt.savefig(path.join(preview_dir, '%s__%s.png' % (zx_angle, zy_angle)))
    plt.close()


def create_3d_preview_image(image_dir, file):
    from matplotlib import pyplot as plt
    from matplotlib import animation
    from mpl_toolkits.mplot3d import Axes3D

    plt.axis('equal')

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.set_axis_off()

    def init():
        with open(file) as f:
            for line in f:
                x, y, z = [float(i) for i in line.rstrip().split(',')]
                ax.scatter(x, y, z, s=2, alpha=0.7, c="m")

    def animate(i):
        ax.view_init(elev=i * 5, azim=i * 5)

    # Animate
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=55, repeat_delay=1000)
    # Save
    anim.save(path.join(image_dir, 'preview.gif'), writer='imagemagick', fps=8)
    plt.close()
