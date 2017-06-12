from analyses.processes import Process
from os import path
import numpy as np


class SphereEvenlySampling(Process):
    FIXED_DIMENSION = 3  # only process 3D data

    STATE_COMPUTING = 'computing'
    STATE_SUMMARY = 'summary'

    params = {
        'graph_scaling_method': 'MDS',
        'sample_size': 100
    }

    def init(self):
        # TODO: params from user input

        # create initial sample data
        self.create_samples()

    def when_ready(self):
        data_format = self.analysis.dataset.format
        work_dir = self.contexts.read('path.work_dir')
        dataset_file_name = self.contexts.read('path.dataset_file')

        dataset_path = path.join(work_dir, dataset_file_name)
        points_path = path.join(work_dir, 'points')

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

        self.contexts.write('points_file_path', points_path)
        self.contexts.write('state', self.STATE_COMPUTING)

    def when_computing(self):
        raise NotImplementedError()
        
        # fresh_sample_size = self.count_fresh_samples()
        # if fresh_sample_size == 0:
        #     self.analysis.write_item('state', self.STATE_SUMMARY)
        #     return

        # TODO fetch and compute a sample

    def summary(self):
        pass

    def count_fresh_samples(self):
        return self.analysis.item_query.filter(name__startswith='samples.fresh.').count()

    def create_samples(self):
        from analyses.utils.sphere_samples import sphere_random_directions
        directions = sphere_random_directions(self.params.get('sample_size'))
        for index, direction in enumerate(directions):
            self.contexts.write('samples.fresh.%i' % index, direction)

        raise self.HasFinished()
