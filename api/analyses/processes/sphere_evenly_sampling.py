import logging
from os import path
import numpy as np
from analyses.processes import Process
from analyses.utils import scripts


class SphereEvenlySampling(Process):
    """
    params:
      - sample_size
      - scaling_method  <- TODO
    """
    FIXED_DIMENSION = 3  # only process 3D data

    STATE_COMPUTE_BASE = 'compute_base'
    STATE_COMPUTE_DIRECTIONS = 'compute_directions'
    STATE_SUMMARY = 'summary'

    dataset_is_graph = None

    def __init__(self, analysis):
        super().__init__(analysis)

        self.dataset_is_graph = (self.analysis.dataset.format == 'graph')

        if self.dataset_is_graph:
            self.points = self.convert_to_points('MDS')
        else:
            dataset_file_name = self.contexts.read('path.dataset_file')
            dataset_path = path.join(self.work_dir, dataset_file_name)
            self.points = np.genfromtxt(dataset_path, delimiter=',')

        if self.dataset_is_graph:
            self.base_graph = self.read_base_graph()
        else:
            self.base_graph = None

    def run(self):
        self.make_base_preview_image()
        self.run_base_r()

        self.contexts.write("preview.is_ready", True)

        max_scale = self.compute_r_max_scale()
        directions = self.generate_random_directions()

        for index, (longitude, latitude) in enumerate(directions):
            self.compute_sample(index, longitude, latitude, max_scale)

    def run_base_r(self):
        logging.info('call base_graph.r')
        scripts.r('base_graph.r', self.work_dir)

    def compute_r_max_scale(self):
        base_diagram_file = path.join(self.work_dir, 'base_diagram.table')
        data_types = [('index', '|S5'), ('dimension', np.intp),
                      ('birth', np.float), ('death', np.float)]
        diagram_data = np.genfromtxt(base_diagram_file,
                                     delimiter=',',
                                     dtype=data_types,
                                     skip_header=1)

        max_scale = max([i for i in diagram_data['death'] if i != np.inf])
        max_scale = int(np.ceil(max_scale))

        self.contexts.write('scripts.projected_graph.max_scale', max_scale)

        return max_scale

    def count_fresh_samples(self):
        return self.contexts.query() \
            .filter(name__startswith='samples.fresh.').count()

    def generate_random_directions(self):
        from analyses.utils.sphere_samples import sphere_random_directions
        size = int(self.params.get('sample_size'))
        self.contexts.write('samples.size', size)
        return sphere_random_directions(size)

    def compute_sample(self, index, longitude, latitude, max_scale):
        logging.info('compute direction %i' % index)

        import csv
        from analyses.utils.point_cloud import project_point_cloud

        # project points
        protected_points = project_point_cloud(self.points, longitude, latitude)
        projected_points_file = path.join(self.work_dir,
                                          'projected_%i_points' % index)
        np.save(projected_points_file, protected_points)

        self.make_projection_preview_image(protected_points, index)

        # call r to generate diagram and calculate bottleneck distance
        scripts.r('projected_graph.r', self.work_dir, index, max_scale)

        result_file = path.join(self.work_dir,
                                'projected_%i_results.csv' % index)

        bottleneck = None
        wasserstein = None
        with open(result_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                bottleneck = float(row['bottleneck'])
                wasserstein = float(row['wasserstein'])
                break

        if bottleneck is None or wasserstein is None:
            raise RuntimeError('error occurred when computing index %i' % index)

        direction_result = {
            'index': index,
            'longitude': longitude,
            'latitude': latitude,
            'distance_bottleneck': bottleneck,
            'distance_wasserstein': wasserstein,
        }

        self.contexts.write('projected.result.%i' % index,
                            direction_result)

    def make_projection_preview_image(self, coordinates, index):
        name_format = 'projected_%s_preview_dots.png' 
        image_path = path.join(self.work_dir, name_format % index)

        from matplotlib import pyplot as plt

        fig = plt.figure(figsize=(5, 5))
        ax = fig.add_subplot(111)

        for x, y in coordinates:
            ax.scatter(x, y, s=4, c="#4e8bae", zorder=2, edgecolors='k', linewidths=0.5)

        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

        plt.savefig(image_path, dpi=600)

        if self.dataset_is_graph:
            linked_image_path = path.join(self.work_dir, 'projected_%s_preview_graph.png' % index)
            for node_from, node_to, weight in self.base_graph:
                coord_from = list(coordinates[node_from - 1])
                coord_to = list(coordinates[node_to - 1])
                ax.plot([coord_from[0], coord_to[0]],
                        [coord_from[1], coord_to[1]],
                        linewidth=0.5,
                        color='#4e8bae',
                        zorder=1)
            plt.savefig(linked_image_path, dpi=600)

        plt.close()

    def make_base_preview_image(self):
        logging.info('create base preview gif')

        image_file_path = path.join(self.work_dir, 'base_preview.gif')

        from matplotlib import pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        from matplotlib import animation

        fig = plt.figure()
        ax = fig.add_subplot(111, projection=Axes3D.name)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_zticklabels([])

        def init():
            logging.info('init animate')
            for x, y, z in self.points:
                ax.scatter(x, y, z,
                           s=4, c="#4e8bae", edgecolors='k', linewidths=0.2)

        def animate(i):
            logging.info('frame %i' % i)
            ax.view_init(elev=i * 5, azim=i * 5)

        if self.dataset_is_graph:
            for node_from, node_to, weight in self.base_graph:
                coord_from = list(self.points[node_from - 1])
                coord_to = list(self.points[node_to - 1])
                ax.plot([coord_from[0], coord_to[0]],
                        [coord_from[1], coord_to[1]],
                        [coord_from[2], coord_to[2]],
                        linewidth=1,
                        color='#4e8bae', zorder=1)

        anim = animation.FuncAnimation(fig, animate, init_func=init,
                                       frames=55, repeat_delay=1000)

        anim.save(image_file_path, writer='imagemagick', fps=8, dpi=300)
        plt.close()

    def read_base_graph(self):
        from analyses.utils.graph import graph_load
        dataset_file = self.contexts.read('path.dataset_file')
        return graph_load(dataset_file)
