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

    def when_ready(self):
        logging.info('analysis is ready')
        self.create_points_file()
        self.create_samples()
        self.contexts.write('state', self.STATE_COMPUTE_BASE)

    def when_compute_base(self):
        logging.info('create base preview gif')

        self.make_base_preview_image()
        work_dir = self.contexts.read('path.work_dir')

        logging.info('call base_graph.r')
        scripts.r('base_graph.r', work_dir)

        # decide params max_scale for projected graph
        base_diagram_file = path.join(work_dir, 'base_diagram.table')
        data_types = [('index', '|S5'), ('dimension', np.intp),
                      ('birth', np.float), ('death', np.float)]
        diagram_data = np.genfromtxt(base_diagram_file,
                                     delimiter=',',
                                     dtype=data_types,
                                     skip_header=1)

        max_scale = max([i for i in diagram_data['death'] if i != np.inf])
        max_scale = int(np.ceil(max_scale))
        self.contexts.write('scripts.projected_graph.max_scale', max_scale)
        self.contexts.write('state', self.STATE_COMPUTE_DIRECTIONS)

    def when_compute_directions(self):
        fresh_sample_size = self.count_fresh_samples()
        if fresh_sample_size == 0:
            self.contexts.write('state', self.STATE_SUMMARY)
            return

        sample = self.contexts.query()\
                              .filter(name__startswith='samples.fresh.')\
                              .first()
        self.compute_sample(sample)
        sample.delete()

    def when_summary(self):
        raise self.HasFinished()

    def count_fresh_samples(self):
        return self.contexts.query()\
                            .filter(name__startswith='samples.fresh.').count()

    def create_samples(self):
        from analyses.utils.sphere_samples import sphere_random_directions
        directions = sphere_random_directions(self.params.get('sample_size'))

        self.contexts.write('samples.size', len(directions))

        for index, direction in enumerate(directions):
            self.contexts.write('samples.fresh.%i' % index, direction)

    def create_points_file(self):
        logging.info('create points file')

        work_dir = self.contexts.read('path.work_dir')
        dataset_file_name = self.contexts.read('path.dataset_file')

        dataset_path = path.join(work_dir, dataset_file_name)
        points_path = path.join(work_dir, 'base_points')

        data_format = self.analysis.dataset.format
        if data_format == 'graph':
            from analyses.utils.graph_scaling import graph_scaling

            graph_scaling(
                dataset_path,
                points_path,
                "MDS",                  # TODO self.params['scaling_method'],
                self.FIXED_DIMENSION
            )
        else:
            points = np.genfromtxt(dataset_path, delimiter=',')
            np.save(points_path, points)

        points_path += '.npy'

        self.contexts.write('path.points_file', points_path)

    def compute_sample(self, sample):
        logging.info('compute sample %s' % sample.name)

        from analyses.utils.point_cloud import project_point_cloud

        longitude, latitude = sample.value
        work_dir = self.contexts.read('path.work_dir')

        # load base points
        points_path = self.contexts.read('path.points_file')
        points = np.load(points_path)

        # project points
        index = int(sample.name.split('.')[-1])
        protected_points = project_point_cloud(points, longitude, latitude)
        projected_points_file = path.join(work_dir,
                                          'projected_%i_points' % index)
        np.save(projected_points_file, protected_points)

        # make_projection_preview_image(protected_points, base_graph,
        #                               work_dir, index)

        # call r to generate diagram and calculate bottleneck distance
        max_scale = self.contexts.read('scripts.projected_graph.max_scale')
        scripts.r('projected_graph.r', work_dir, index, max_scale)

        result_file = path.join(work_dir,
                                'projected_%i_distance.txt' % index)
        distance = float(open(result_file).read())

        direction_result = {
            'index': index,
            'longitude': longitude,
            'latitude': latitude,
            'distance': distance
        }

        self.contexts.write('samples.result.%i' % index,
                            direction_result)

    def make_base_preview_image(self):
        points_file = self.contexts.read('path.points_file')
        points = np.load(points_file)

        work_dir = self.contexts.read('path.work_dir')
        image_file_path = path.join(work_dir, 'base_preview.gif')

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
            for x, y, z in points:
                ax.scatter(x, y, z,
                           s=4, c="#4e8bae", edgecolors='k', linewidths=0.2)

        def animate(i):
            logging.info('frame %i' % i)
            ax.view_init(elev=i * 5, azim=i * 5)

        data_format = self.analysis.dataset.format
        if data_format == 'graph':
            from analyses.utils.graph import graph_load
            dataset_file = self.contexts.read('path.dataset_file')
            base_graph = graph_load(dataset_file)
            for node_from, node_to, weight in base_graph:
                coord_from = list(points[node_from - 1])
                coord_to = list(points[node_to - 1])
                ax.plot([coord_from[0], coord_to[0]],
                        [coord_from[1], coord_to[1]],
                        [coord_from[2], coord_to[2]],
                        linewidth=1,
                        color='#4e8bae', zorder=1)

        anim = animation.FuncAnimation(fig, animate, init_func=init,
                                       frames=55, repeat_delay=1000)

        anim.save(image_file_path, writer='imagemagick', fps=8, dpi=300)
        plt.close()
