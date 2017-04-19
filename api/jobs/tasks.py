from os import path, makedirs, chdir, remove
from celery import shared_task, chord, chain, group
from math import sin, cos, pi
from django.conf import settings
from django.utils import timezone
from subprocess import Popen, PIPE
from time import sleep, time
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import multiprocessing, logging
import numpy as np
import scipy.spatial as spatial
import requests
import itertools

BASE_COORDINATE_FILENAME = 'base.csv'
CPU_CORE_COUNT = multiprocessing.cpu_count() - 1

ANGLE_RANGE = list(itertools.product(range(-90, 90, 5), repeat=2))


@shared_task()
def drop_args(*args):
    return None


@shared_task()
def direction_task(base_diagram_file, dipha_out_file, zx_angle, zy_angle, base_name):
    rotated_diagram = extract_persistence_diagram(dipha_out_file, base_name)
    return calculate_bottleneck_distance(rotated_diagram, base_diagram_file, [zx_angle, zy_angle])


@shared_task()
def dispath_dipha(distance_matrix_files, job_id):
    out_files = []
    for bin_file in distance_matrix_files:
        out_files.append(dipha(bin_file))

    work_dir = path.dirname(distance_matrix_files[0])
    base_diagram_file = path.join(work_dir, 'base.diagram')

    tasks = []

    for zx_angle, zy_angle in ANGLE_RANGE:
        base_name = 'rotated_%s__%s' % (zx_angle, zy_angle)
        dipha_out_file = path.join(work_dir, base_name + '-dipha.out')
        tasks.append(direction_task.s(base_diagram_file, dipha_out_file, zx_angle, zy_angle, base_name))

    chord(
        header=tasks,
        body=compose_results.s(job_id)
    ).apply_async()


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


@shared_task()
def compose_results(results, job_id):
    from jobs.models import Job
    job = Job.objects.get(pk=job_id)
    job.status = 0
    job.percentage = 100
    job.completed_at = timezone.now()
    job.outputs = {
        'best_projection': min(results, key=lambda item: float(item[2])),
        'worst_projection': max(results, key=lambda item: float(item[2])),
        'bottleneck_distances': results
    }
    job.save()


@shared_task()
def workflow_test(*args, name="", time=2):
    print([name, args])
    sleep(time)
    return name


@shared_task()
def pass_args(*args):
    logging.debug('pass args\n [%s]' % ','.join(map(str, args)))
    return args


def preparing_dipha_input_tasks(base_coordinates_file, point_count):
    tasks = []
    for zx_angle, zy_angle in ANGLE_RANGE:
        base_name = 'rotated_%s__%s' % (zx_angle, zy_angle)
        logging.info('before dipha: %s' % base_name)
        tasks.append(before_dipha_task.s(base_coordinates_file, zx_angle, zy_angle, point_count, base_name))

    return tasks


@shared_task()
def before_dipha_task(base_coordinates_file, zx_angle, zy_angle, point_count, base_name):
    rotated_coordinates_file = make_rotated_coordinate_file(base_coordinates_file, zx_angle, zy_angle, base_name)
    return generate_distance_matrix(rotated_coordinates_file, point_count, base_name + '-dipha')


@shared_task()
def dipha_tasks(input_files):
    input_files = list(input_files)

    for input_file in input_files:
        logging.info('dipha %s' % path.basename(input_file))
        dipha(input_file)

    return None


def download_base_coordinates(work_dir, file_id):
    file_path = path.join(work_dir, BASE_COORDINATE_FILENAME)

    if path.isfile(file_path):
        logging.info('skip downloading coordinates')
        return file_path

    file_meta_url = 'https://www.filestackapi.com/api/file/%s/metadata' % file_id
    file_download_url = 'https://www.filestackapi.com/api/file/%s?dl=true' % file_id

    meta_data = requests.get(file_meta_url).json()
    if meta_data['mimetype'] != 'text/csv':
        raise Exception("invalid base coordinates")

    req = requests.get(file_download_url, stream=True)
    with open(file_path, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    logging.info('base coordinates downloaded')
    return file_path


def rotate_coordinates(row, angle, dim1, dim2):
    radian = angle * pi / 180.
    cos_alpha, sin_alpha = cos(radian), sin(radian)
    x, y = row[dim1], row[dim2]
    row[dim1] = cos_alpha * x - sin_alpha * y
    row[dim2] = sin_alpha * x + cos_alpha * y
    return row


def prepare_work_dir(job, ticket=None):
    if ticket is None:
        ticket = '%s_%s' % (job.id, int(time()))
        job.ticket = ticket
        job.save(update_fields=['ticket'])

    work_dir = path.join(settings.DATA_DIR, 'jobs', ticket)
    makedirs(work_dir, exist_ok=True)

    return work_dir


def count_points(coordinates_file):
    count = 0
    with open(coordinates_file) as f:
        for line in f:
            if line.strip() != "":
                count += 1

    logging.info('point count: %i' % count)

    return count


def make_rotated_coordinate_file(base_coordinates_file, zx_angle, zy_angle, basename):
    rotated_file_path = path.join(path.dirname(base_coordinates_file), '%s.csv' % basename)

    if path.isfile(rotated_file_path):
        logging.info('skip rotated coordinates %s' % basename)
        return rotated_file_path

    with open(base_coordinates_file) as base_file, open(rotated_file_path, 'w') as rotated_file:
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
        logging.info('init animate')
        with open(coordinates_file) as f:
            for line in f:
                x, y, z = [float(i) for i in line.rstrip().split(',')]
                ax.scatter(x, y, z, s=2, alpha=0.7, c="m")

    def animate(i):
        logging.info('frame %i' % i)
        ax.view_init(elev=i * 5, azim=i * 5)

    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=55, repeat_delay=1000)
    anim.save(image_file_path, writer='imagemagick', fps=8)
    plt.close()


def generate_distance_matrix(coordinates_file, point_number, basename):
    file_path = path.join(path.dirname(coordinates_file), '%s.bin' % basename)

    if path.isfile(file_path):
        logging.info('skip distance matrix: %s' % basename)
        return file_path

    logging.info('generating distance matrix %s' % file_path)
    dis_file = open(file_path, 'wb')
    dis_file.write(np.int64(8067171840).tobytes())  # DIPHA magic number
    dis_file.write(np.int64(7).tobytes())  # DIPHA file type code
    dis_file.write(np.int64(point_number).tobytes())

    count = 1
    with open(coordinates_file) as col_file:
        for col_line in col_file:
            point_col = [float(i) for i in col_line.strip().split(",")]
            count += 1
            with open(coordinates_file) as row_file:
                for row_line in row_file:
                    point_row = [float(i) for i in row_line.strip().split(",")]
                    distance = spatial.distance.euclidean(point_col, point_row)
                    dis_file.write(np.double(distance).tobytes())

    dis_file.close()

    return file_path


def dipha(input_file):
    out_file = path.splitext(input_file)[0] + '.out'

    if path.isfile(out_file):
        logging.info('skip dipha')
        return out_file

    command = 'mpiexec -n %i dipha --upper_dim 2 %s %s' % (CPU_CORE_COUNT, input_file, out_file)
    proc = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)

    print('dipha %s' % path.basename(input_file))

    while proc.poll() is None:
        sleep(0.5)

    return out_file


def extract_persistence_diagram(dipha_out_file, base_name):
    diagram_file_path = path.join(path.dirname(dipha_out_file), '%s.diagram' % base_name)

    if path.isfile(diagram_file_path):
        logging.info('skip diagram file')
        return diagram_file_path

    basename = path.splitext(path.basename(dipha_out_file))[0]
    work_dir = path.dirname(dipha_out_file)

    f = open(dipha_out_file, 'rb')

    dipha_identifier = np.fromfile(f, dtype=np.int64, count=1)
    if dipha_identifier[0] != 8067171840:
        raise Exception('invalid dipha_identifier: %s' % dipha_out_file)

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


def calculate_bottleneck_distance(diagram_file, base_diagram_file, result_data):
    work_dir = path.dirname(base_diagram_file)
    base_filename = path.basename(base_diagram_file)
    proj_filename = path.basename(diagram_file)
    basename = path.splitext(path.basename(diagram_file))[0]
    pic_filename = basename + '-diagram.png'
    val_filename = basename + '.txt'
    val_filepath = path.join(work_dir, val_filename)

    if path.isfile(val_filename) and path.isfile(pic_filename):
        logging.info('skip bottleneck distance %s' % val_filename)
    else:
        chdir(path.join(settings.BASE_DIR, 'scripts'))
        command = 'Rscript bottleneck_distance.r %s %s %s %s %s' % (
            work_dir, base_filename, proj_filename, val_filename, pic_filename)
        proc = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        while proc.poll() is None:
            sleep(0.3)

    with open(val_filepath) as f:
        result_data.append(float(f.read()))

    return result_data
