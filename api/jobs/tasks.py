from os import path, makedirs
from celery import shared_task
from math import sin, cos, pi
from django.conf import settings
from django.utils import timezone
from subprocess import Popen, PIPE
from time import sleep
from matplotlib import pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import time
import numpy as np
import scipy.spatial as spatial
import requests

BASE_COORDINATE_FILENAME = 'base_coordinate.scv'


@shared_task()
def create_job(instance_id):
    from jobs.models import Job

    job = Job.objects.get(pk=instance_id)
    job.started_at = timezone.now()
    job.percentage = 5
    job.save(update_fields=['started_at', 'percentage'])

    work_dir = create_work_dir(job)
    base_coord_file = download_base_coordinates(job, work_dir)
    point_count = count_points(base_coord_file)

    make_base_preview_image(base_coord_file)
    distance_matrix_file = make_dipha_distance_matrix(base_coord_file, point_count)
    proc, output_file = make_dipha_process(distance_matrix_file)
    proc.communicate()
    if proc.returncode != 0:
        raise Exception("DIPHA error")
    base_diagram_file = extract_persistence_diagram(distance_matrix_file)

    # process by angle
    results = []
    angle_range = range(-90, 90, 5)
    for zx_angle in angle_range:
        for zy_angle in angle_range:
            print(['processing angle', zx_angle, zy_angle])
            rotated_coordinate_file = make_rotated_coordinate_file(base_coord_file, zx_angle, zy_angle)
            rotated_dipha_input_file = make_dipha_distance_matrix(rotated_coordinate_file, point_count)
            proc, rotated_output_file = make_dipha_process(rotated_dipha_input_file)

            # create preview image before checking sub process status
            make_projection_preview_image(rotated_coordinate_file)

            while proc.poll() is None:
                sleep(1)

            if proc.returncode != 0:
                raise Exception("error")

            project_diagram_file = extract_persistence_diagram(rotated_output_file)
            b_distance = bottleneck_distance(base_diagram_file, project_diagram_file)
            results.append([zx_angle, zy_angle, b_distance])
            break
        break

        # count += 1
        # job.percentage = round(5 + count / total_angles * 95, 2)
        # job.save(update_fields=['percentage'])

    job.status = 0
    job.percentage = 100
    job.outputs = {
        'best_projection': min(results, key=lambda item: item[2]),
        'worst_projection': max(results, key=lambda item: item[2]),
        'bottleneck_distances': results,
    }
    job.save()


def rotate_coordinates(row, angle, dim1, dim2):
    radian = angle * pi / 180.
    cos_alpha, sin_alpha = cos(radian), sin(radian)
    x, y = row[dim1], row[dim2]
    row[dim1] = cos_alpha * x - sin_alpha * y
    row[dim2] = sin_alpha * x + cos_alpha * y
    return row


def create_work_dir(job):
    job.ticket = '%s_%s' % (job.id, int(time.time()))
    job.save(update_fields=['ticket'])
    work_dir = path.join(settings.DATA_DIR, 'jobs', job.ticket)
    makedirs(work_dir)
    return work_dir


def download_base_coordinates(job, work_dir):
    file_id = job.inputs['file']
    file_meta_url = 'https://www.filestackapi.com/api/file/%s/metadata' % file_id
    file_download_url = 'https://www.filestackapi.com/api/file/%s?dl=true' % file_id
    file_path = path.join(work_dir, BASE_COORDINATE_FILENAME)

    meta_data = requests.get(file_meta_url).json()
    if meta_data['mimetype'] != 'text/csv':
        raise Exception("invalid base coordinates")

    req = requests.get(file_download_url, stream=True)
    with open(file_path, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    return file_path


def count_points(coordinates_file):
    count = 0
    with open(coordinates_file) as f:
        for line in f:
            if line.strip() != "":
                count += 1

    return count


def make_rotated_coordinate_file(coordinate_file, zx_angle, zy_angle, ):
    rotated_file_path = path.join(path.dirname(coordinate_file), 'rotated_%s__%s.csv' % (zx_angle, zy_angle))

    with open(coordinate_file) as base_file, open(rotated_file_path, 'w') as rotated_file:
        for line in base_file:
            row = [float(i) for i in line.strip().split(',')]
            rotated_row = rotate_coordinates(row, zx_angle, dim1=0, dim2=1)
            rotated_row = rotate_coordinates(rotated_row, zy_angle, dim1=0, dim2=2)
            rotated_file.write('{},{}\n'.format(*[round(i, 6) for i in rotated_row]))

    return rotated_file_path


def make_projection_preview_image(coordinates_file):
    image_file_path = path.join(path.splitext(coordinates_file)[0], '-preview.png')

    fig = plt.figure()
    ax = fig.add_subplot(111)

    with open(coordinates_file) as f:
        for line in f:
            x, y = line.rstrip().split(',')
            ax.scatter(x, y, s=2, alpha=0.7, c="m")

    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    plt.axis('equal')
    plt.savefig(image_file_path, dpi=150)
    plt.close()


def make_base_preview_image(coordinates_file):
    image_file_path = path.join(path.dirname(coordinates_file), 'base_preview.gif')

    fig = plt.figure()
    ax = fig.add_subplot(111, projection=Axes3D.name)

    def init():
        with open(coordinates_file) as f:
            for line in f:
                x, y, z = [float(i) for i in line.rstrip().split(',')]
                ax.scatter(x, y, z, s=2, alpha=0.7, c="m")

    def animate(i):
        ax.view_init(elev=i * 5, azim=i * 5)

    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=55, repeat_delay=1000)
    anim.save(image_file_path, writer='imagemagick', fps=8)
    plt.close()


def make_dipha_distance_matrix(coordinate_file, point_count):
    input_file = path.splitext(coordinate_file)[0] + "-dipha-input.bin"

    col_file = open(coordinate_file)
    row_file = open(coordinate_file)
    dis_file = open(input_file, 'wb')

    dis_file.write(np.int64(8067171840).tobytes())  # DIPHA magic number
    dis_file.write(np.int64(7).tobytes())  # DIPHA file type code
    dis_file.write(np.int64(point_count).tobytes())

    for col_line in col_file.readlines():
        point_col = [float(i) for i in col_line.strip().split(",")]
        for row_line in row_file.readlines():
            point_row = [float(i) for i in row_line.strip().split(",")]
            distance = spatial.distance.euclidean(point_col, point_row)
            dis_file.write(np.float64(distance).tobytes())
        row_file.seek(0)

    col_file.close()
    row_file.close()
    dis_file.close()

    return input_file


def make_dipha_process(input_file, upper_dims=2):
    output_file = path.splitext(input_file)[0] + '-dipha-output.bin'
    command = 'dipha --upper_dim %i %s %s' % (upper_dims, input_file, output_file)
    return Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True), output_file


def extract_persistence_diagram(file_path):
    f = open(file_path, 'rb')

    dipha_identifier = np.fromfile(f, dtype=np.int64, count=1)
    if dipha_identifier[0] != 8067171840:
        raise Exception('invalid dipha_identifier')

    diagram_identifier = np.fromfile(f, dtype=np.int64, count=1)
    if diagram_identifier[0] != 2:
        raise Exception('invalid diagram_identifier')

    point_number = np.fromfile(f, dtype=np.int64, count=1)
    point_number = point_number[0]

    name_prefix = path.splitext(file_path)[0]
    dim_file = open(name_prefix + "-dims.val", 'w')
    birth_file = open(name_prefix + "-birth.val", 'w')
    death_file = open(name_prefix + "-death.val", 'w')

    for _ in range(0, point_number):
        dim = np.fromfile(f, dtype=np.int64, count=1)[0]
        dim_file.write("%s\n" % dim)
        f.read(16)

    f.seek(32)
    for _ in range(0, point_number):
        birth = np.fromfile(f, dtype=np.double, count=1)[0]
        birth_file.write("%s\n" % birth)
        f.read(16)

    f.seek(40)
    for _ in range(0, point_number):
        death = np.fromfile(f, dtype=np.double, count=1)[0]
        death_file.write("%s\n" % death)
        f.read(16)

    dim_file.close()
    birth_file.close()
    death_file.close()

    diagram_file_path = name_prefix + '-diagram.csv'

    with open(diagram_file_path, 'w') as diagram, \
            open(name_prefix + "-dims.csv") as dim, \
            open(name_prefix + "-birth.csv") as birth, \
            open(name_prefix + "-death.csv") as death:
        for _ in range(0, point_number):
            dim_value = dim.readline().strip()
            birth_value = birth.readline().strip()
            death_value = death.readline().strip()
            diagram.write("{},{},{}\n".format(dim_value, birth_value, death_value))

    return diagram_file_path


def bottleneck_distance(base_diagram, project_diagram):
    return 0
