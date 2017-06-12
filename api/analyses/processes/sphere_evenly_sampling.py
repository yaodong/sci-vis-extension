from analyses.processes import Process
from analyses.utils import scripts
from os import path
import numpy as np
import logging


class SphereEvenlySampling(Process):
    FIXED_DIMENSION = 3  # only process 3D data

    STATE_COMPUTE_BASE = 'compute_base'
    STATE_COMPUTE_DIRECTIONS = 'compute_directions'
    STATE_SUMMARY = 'summary'

    params = {
        'graph_scaling_method': 'MDS',
        'sample_size': 100
    }

    def when_ready(self):
        logging.info('analysis is ready')
        self.create_points_file()
        self.create_samples()
        self.contexts.write('state', self.STATE_COMPUTE_BASE)

    def when_compute_base(self):
        logging.info('create base preview gif')
        # make_base_preview_image(points, base_graph, work_dir)
        work_dir = self.contexts.read('path.work_dir')

        logging.info('call base_graph.r')
        scripts.r('base_graph.r', work_dir)

        # decide params max_scale for projected graph
        base_diagram_file = path.join(work_dir, 'base_diagram.table')
        diagram_data = np.genfromtxt(base_diagram_file,
                                     delimiter=',',
                                     dtype=[('index', '|S5'), ('dimension', np.intp),
                                            ('birth', np.float), ('death', np.float)],
                                     skip_header=1)

        max_scale = int(np.ceil(max([i for i in diagram_data['death'] if i != np.inf])))
        self.contexts.write('scripts.projected_graph.max_scale', max_scale)
        self.contexts.write('state', self.STATE_COMPUTE_DIRECTIONS)

    def when_compute_directions(self):
        fresh_sample_size = self.count_fresh_samples()
        if fresh_sample_size == 0:
            self.contexts.write('state', self.STATE_SUMMARY)
            return

        sample = self.contexts.query().filter(name__startswith='samples.fresh.').first()
        self.compute_sample(sample)
        sample.delete()

    def when_summary(self):
        raise self.HasFinished()

    def count_fresh_samples(self):
        return self.contexts.query().filter(name__startswith='samples.fresh.').count()

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
                self.params['graph_scaling_method'],
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
        direction_index = int(sample.name.split('.')[-1])
        protected_points = project_point_cloud(points, longitude, latitude)
        projected_points_file = path.join(work_dir, 'projected_%i_points' % direction_index)
        np.save(projected_points_file, protected_points)

        # make_projection_preview_image(protected_points, base_graph, work_dir, index)

        # call r to generate diagram and calculate bottleneck distance
        max_scale = self.contexts.read('scripts.projected_graph.max_scale')
        scripts.r('projected_graph.r', work_dir, direction_index, max_scale)

        result_file = path.join(work_dir, 'projected_%i_distance.txt' % direction_index)
        distance = float(open(result_file).read())

        direction_result = {
            'index': direction_index,
            'longitude': longitude,
            'latitude': latitude,
            'distance': distance
        }

        self.contexts.write('samples.result.%i' % direction_index, direction_result)
