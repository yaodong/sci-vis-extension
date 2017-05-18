import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.csgraph import shortest_path
from sklearn import manifold
from sklearn.metrics.pairwise import euclidean_distances
from os import path, chdir
from django.conf import settings
from subprocess import Popen, PIPE
from time import sleep
import logging
import numpy as np


def graph_load(file):
    """
        :param file:
        :return: lil_matrix
        """
    return np.genfromtxt(file, delimiter='\t', dtype=[('from', np.intp), ('to', np.intp), ('weight', np.float)])


def graph_distance_matrix(data):
    """
    :param 
    :return:
        dist_matrix : ndarray
            The N x N matrix of distances between graph nodes. dist_matrix[i,j]
            gives the shortest distance from point i to point j along the graph.
    """
    max_node_id = 0
    for row in data:
        bigger_node = max([row[0], row[1]])
        if max_node_id < bigger_node:
            max_node_id = bigger_node

    graph = lil_matrix((max_node_id, max_node_id))
    for node_from, node_to, weight in data:
        graph[node_from - 1, node_to - 1] = weight

    return shortest_path(graph, method='D', directed=False, unweighted=False)


def compute_points_distance_matrix(points):
    """
    :param points: like [[0, 1], [1, 1]]
    :return: 
    """
    return euclidean_distances(points)


def multidimensional_scaling(distance_matrix, dimensional=3, max_iter=3000):
    seed = np.random.RandomState(seed=3)
    mds = manifold.MDS(n_components=dimensional, max_iter=max_iter, eps=1e-9, random_state=seed,
                       dissimilarity="precomputed", n_jobs=1)
    return mds.fit(distance_matrix).embedding_


def calculate_bottleneck_distance(diagram_file, base_diagram_file):
    work_dir = path.dirname(base_diagram_file)
    base_filename = path.basename(base_diagram_file)
    proj_filename = path.basename(diagram_file)
    basename = path.splitext(path.basename(diagram_file))[0]
    pic_filename = basename + '_diagram.png'
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
        result = float(f.read())

    return result


def call_r_script(file, *args):
    chdir(path.join(settings.BASE_DIR, 'scripts'))
    command = 'Rscript %s ' % file
    command += ' '.join([str(i) for i in args])

    logging.info(command)

    proc = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    while proc.poll() is None:
        sleep(0.3)
