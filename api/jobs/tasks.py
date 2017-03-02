from os import path, makedirs, chdir, remove
from celery import shared_task
from math import sin, cos, pi
from django.conf import settings
from django.utils import timezone
from subprocess import Popen, PIPE
from time import sleep, time
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import scipy.spatial as spatial
import requests

BASE_COORDINATE_FILENAME = 'base.scv'


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

    print('data file downloaded')

    make_base_preview_image(base_coord_file, 'base')
    distance_matrix_file = make_dipha_distance_matrix(base_coord_file, point_count, 'base')
    print('base distance matrix created')

    proc, output_file = make_dipha_process(distance_matrix_file, 'base')
    proc.communicate()
    if proc.returncode != 0:
        raise Exception("DIPHA error")
    base_diagram_file = extract_persistence_diagram(output_file, 'base')
    print('base diagram created')

    # process by angle
    results = []
    count = 0
    angle_range = range(-90, 90, 5)
    total_angles = pow(len(angle_range), 2)
    for zx_angle in angle_range:
        for zy_angle in angle_range:
            print(['processing angle', zx_angle, zy_angle])
            proj_basename = 'rotated_%s__%s' % (zx_angle, zy_angle)
            rotated_coordinate_file = make_rotated_coordinate_file(base_coord_file, zx_angle, zy_angle, proj_basename)

            print('[%f] created rotated file' % time())
            rotated_dipha_input_file = make_dipha_distance_matrix(rotated_coordinate_file, point_count, proj_basename)

            print('[%f] created dipha input file' % time())
            proc, rotated_output_file = make_dipha_process(rotated_dipha_input_file, proj_basename)

            # create preview image before checking sub process status
            make_projection_preview_image(rotated_coordinate_file, proj_basename)

            while proc.poll() is None:
                sleep(0.5)

            print('[%f] DIPHA completed' % time())
            if proc.returncode != 0:
                raise Exception("error")

            project_diagram_file = extract_persistence_diagram(rotated_output_file, proj_basename)
            dis = calculate_bottleneck_distance(base_diagram_file, project_diagram_file, proj_basename)
            results.append([zx_angle, zy_angle, dis])

            count += 1
            job.percentage = round(5 + count / total_angles * 95, 2)
            job.save(update_fields=['percentage'])

    job.status = 0
    job.percentage = 100
    job.completed_at = timezone.now()
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
    job.ticket = '%s_%s' % (job.id, int(time()))
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


def make_rotated_coordinate_file(coordinate_file, zx_angle, zy_angle, basename):
    rotated_file_path = path.join(path.dirname(coordinate_file), '%s.csv' % basename)

    with open(coordinate_file) as base_file, open(rotated_file_path, 'w') as rotated_file:
        for line in base_file:
            row = [float(i) for i in line.strip().split(',')]
            rotated_row = rotate_coordinates(row, zx_angle, dim1=0, dim2=1)
            rotated_row = rotate_coordinates(rotated_row, zy_angle, dim1=0, dim2=2)
            rotated_file.write('{},{}\n'.format(*[round(i, 6) for i in rotated_row]))

    return rotated_file_path


def make_projection_preview_image(coordinates_file, basename):
    image_file_path = path.join(path.dirname(coordinates_file), '%s-preview.png' % basename)

    from matplotlib import pyplot as plt

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


def make_base_preview_image(coordinates_file, basename):
    image_file_path = path.join(path.dirname(coordinates_file), '%s-preview.gif' % basename)

    from matplotlib import pyplot as plt

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


def make_dipha_distance_matrix(coordinate_file, point_count, basename):
    input_file = path.join(path.dirname(coordinate_file), '%s-dipha-input.bin' % basename)

    dis_file = open(input_file, 'wb')

    dis_file.write(np.int64(8067171840).tobytes())  # DIPHA magic number
    dis_file.write(np.int64(7).tobytes())  # DIPHA file type code
    dis_file.write(np.int64(point_count).tobytes())

    with open(coordinate_file) as col_file:
        for col_line in col_file:
            point_col = [float(i) for i in col_line.strip().split(",")]
            with open(coordinate_file) as row_file:
                for row_line in row_file:
                    point_row = [float(i) for i in row_line.strip().split(",")]
                    distance = spatial.distance.euclidean(point_col, point_row)
                    dis_file.write(np.double(distance).tobytes())

    dis_file.close()

    return input_file


def make_dipha_process(input_file, basename, upper_dims=2):
    output_file = path.join(path.dirname(input_file), '%s-dipha-output.bin' % basename)
    command = 'mpiexec -n 8 dipha --upper_dim %i %s %s' % (upper_dims, input_file, output_file)
    return Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True), output_file


def extract_persistence_diagram(file_path, basename):
    work_dir = path.dirname(file_path)
    f = open(file_path, 'rb')

    dipha_identifier = np.fromfile(f, dtype=np.int64, count=1)
    if dipha_identifier[0] != 8067171840:
        raise Exception('invalid dipha_identifier: %s' % dipha_identifier)

    diagram_identifier = np.fromfile(f, dtype=np.int64, count=1)
    if diagram_identifier[0] != 2:
        raise Exception('invalid diagram_identifier: %s' % diagram_identifier)

    point_number = np.fromfile(f, dtype=np.int64, count=1)
    point_number = point_number[0]

    dims_file_path = path.join(work_dir, '%s-dims.csv' % basename)
    birth_file_path = path.join(work_dir, '%s-birth.csv' % basename)
    death_file_path = path.join(work_dir, '%s-death.csv' % basename)

    with open(dims_file_path, 'w') as dims_file, \
            open(birth_file_path, 'w') as birth_file, \
            open(death_file_path, 'w') as death_file:

        for _ in range(0, point_number):
            dim = np.fromfile(f, dtype=np.int64, count=1)[0]
            dims_file.write("%s\n" % dim)
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

    diagram_file_path = path.join(work_dir, '%s-diagram.csv' % basename)

    with open(diagram_file_path, 'w') as diagram, \
            open(dims_file_path) as dim, \
            open(birth_file_path) as birth, \
            open(death_file_path) as death:

        for _ in range(0, point_number):
            dim_value = dim.readline().strip()
            birth_value = birth.readline().strip()
            death_value = death.readline().strip()
            diagram.write("{},{},{}\n".format(dim_value, birth_value, death_value))

    remove(dims_file_path)
    remove(birth_file_path)
    remove(death_file_path)

    return diagram_file_path


def calculate_bottleneck_distance(base_diagram_file, project_diagram_file, basename):
    work_dir = path.dirname(base_diagram_file)
    base_filename = path.basename(base_diagram_file)
    proj_filename = path.basename(project_diagram_file)
    pic_filename = '%s-diagram.png' % basename
    out_filename = '%s.txt' % basename

    chdir(path.join(settings.BASE_DIR, 'scripts'))
    command = 'Rscript bottleneck_distance.r %s %s %s %s %s' % (work_dir, base_filename, proj_filename, out_filename, pic_filename)
    print(command)
    proc = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    proc.communicate()

    out_file_path = path.join(work_dir, out_filename)
    with open(out_file_path) as f:
        value = float(f.read())

    return value
