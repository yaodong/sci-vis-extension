import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path
from sklearn import manifold
from sklearn.metrics import euclidean_distances
from sklearn.decomposition import PCA


def compute_distance_matrix(file):
    """
    :param file:
    :return:
        dist_matrix : ndarray
            The N x N matrix of distances between graph nodes. dist_matrix[i,j]
            gives the shortest distance from point i to point j along the graph.
    """
    data = np.genfromtxt(file, dtype=[('from', np.intp), ('to', np.intp), ('weight', np.float)])

    max_node_id = 0
    for row in data:
        bigger_node = max([row[0], row[1]])
        if max_node_id < bigger_node:
            max_node_id = bigger_node

    graph = csr_matrix((max_node_id, max_node_id))
    for node_from, node_to, weight in data:
        graph[node_from - 1, node_to - 1] = weight

    return shortest_path(graph, method='D', directed=False, unweighted=False)


def multidimensional_scaling(distance_matrix, dimensional=3, max_iter=3000):
    seed = np.random.RandomState(seed=3)
    mds = manifold.MDS(n_components=dimensional, max_iter=max_iter, eps=1e-9, random_state=seed,
                       dissimilarity="precomputed", n_jobs=1)
    return mds.fit(distance_matrix).embedding_
