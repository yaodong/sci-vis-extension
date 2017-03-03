import networkx as nx
import igraph as gh
import time

g = gh.Graph()
g.as_undirected()

with open('4elt.graph') as f:
    node_count, edge_count = [int(i) for i in f.readline().strip().split(" ")]

    """
    add vertex with empty name.
    """
    [g.add_vertex() for _ in range(0, node_count)]

    """
    vertex id from 4elt are enumerated from one.
    vertex id in Graph are enumerated from zero.
    """
    for vertex_id in range(0, node_count):
        others = f.readline().strip().split(" ")
        g.add_edges([(vertex_id, int(other) - 1) for other in others])

start_time = time.time()
print(time.time())
layout = g.layout_kamada_kawai_3d()
print("layout spend time: %s" % (time.time() - start_time))

with open("coordinates.csv", "w") as f:
    for xyz in layout.coords:
        f.write('%s,%s,%s' % xyz)
