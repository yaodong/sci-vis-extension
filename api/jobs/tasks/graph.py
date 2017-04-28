import numpy as np
from os import path
from celery import shared_task
from jobs.utils.files import count_file_lines
from jobs.utils.dipha import *
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path


@shared_task()
def compute_graph(job_id, data_file):
    distance_matrix_file = generate_distance_matrix_file(data_file)
    dipha_out_file = dipha_exec(distance_matrix_file)
    diagram = parse_dipha_output(dipha_out_file, 'base')

    # def dispath_dipha(distance_matrix_files, job_id):
    #     out_files = []
    #     for bin_file in distance_matrix_files:
    #         out_files.append(dipha(bin_file))
    #
    #     work_dir = path.dirname(distance_matrix_files[0])
    #     base_diagram_file = path.join(work_dir, 'base.diagram')
    #
    #     tasks = []
    #
    #     for zx_angle, zy_angle in ANGLE_RANGE:
    #         base_name = 'rotated_%s__%s' % (zx_angle, zy_angle)
    #         dipha_out_file = path.join(work_dir, base_name + '-dipha.out')
    #         tasks.append(direction_task.s(base_diagram_file, dipha_out_file, zx_angle, zy_angle, base_name))
    #
    #     chord(
    #         header=tasks,
    #         body=compose_results.s(job_id)
    #     ).apply_async()
    #
    # point_number = count_points(base_coordinates_file)
    # base_distance_matrix = generate_distance_matrix(base_coordinates_file, point_number, 'base-dipha')
    # base_dipha_out_file = dipha(base_distance_matrix)
    # extract_persistence_diagram(base_dipha_out_file, 'base')
    #
    # chord(
    #     header=preparing_dipha_input_tasks(base_coordinates_file, point_number),
    #     body=dispath_dipha.s(job_id)
    # ).apply_async()


def generate_distance_matrix_file(file):
    data = np.genfromtxt(file, dtype=[('from', np.intp), ('to', np.intp), ('weight', np.float)])

    max_node_id = 0
    for row in data:
        bigger_node = max([row[0], row[1]])
        if max_node_id < bigger_node:
            max_node_id = bigger_node

    graph = csr_matrix((max_node_id, max_node_id))
    for node_from, node_to, weight in data:
        graph[node_from - 1, node_to - 1] = weight

    distance_matrix = shortest_path(graph, method='D', directed=False, unweighted=False)
    matrix_file = path.join(path.dirname(file), 'base_distance_matrix')

    # save as numpy binary for debugging
    np.save(matrix_file, distance_matrix)

    dipha_matrix_file = matrix_file + '.bin'
    save_dipha_distance_matrix(dipha_matrix_file, distance_matrix)

    return dipha_matrix_file
