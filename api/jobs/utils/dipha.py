from os import path, remove
from subprocess import Popen, PIPE
from time import sleep
import numpy as np
import logging
import multiprocessing


def save_dipha_distance_matrix(filename, distance_matrix):
    logging.info('generating distance matrix')
    dis_file = open(filename, 'wb')
    dis_file.write(np.int64(8067171840).tobytes())  # DIPHA magic number
    dis_file.write(np.int64(7).tobytes())  # DIPHA file type code
    dis_file.write(np.int64(len(distance_matrix)).tobytes())

    for row in distance_matrix:
        for distance in row:
            dis_file.write(np.double(distance).tobytes())

    dis_file.close()


def dipha_exec(input_file):
    out_file = path.splitext(input_file)[0] + '.out'
    max_processes = multiprocessing.cpu_count() - 1

    command = 'mpiexec -n %i dipha --upper_dim 2 %s %s' % (max_processes, input_file, out_file)
    proc = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)

    while proc.poll() is None:
        sleep(1)

    return out_file


def parse_dipha_output(dipha_out_file, base_name):
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
