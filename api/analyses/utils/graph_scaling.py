from sklearn import manifold
from analyses.utils.graph import graph_load, graph_distance_matrix
import numpy as np


def graph_scaling(graph_file, points_file, method, dimension):
    if method != 'MDS':
        raise NotImplementedError()

    base_graph = graph_load(graph_file)
    matrix = graph_distance_matrix(base_graph)
    return multidimensional_scaling(matrix, dimension)


def multidimensional_scaling(distance_matrix, dimensional=3, max_iter=3000):
    seed = np.random.RandomState(seed=3)
    mds = manifold.MDS(n_components=dimensional,
                       max_iter=max_iter,
                       eps=1e-9,
                       random_state=seed,
                       dissimilarity="precomputed",
                       n_jobs=1)
    return mds.fit(distance_matrix).embedding_
