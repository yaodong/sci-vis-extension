from analyses.processes import Process
from analyses.processes.mixins.graph_to_points import GraphToPoints


class BestLinearProjection(Process, GraphToPoints):

    CONVERTED_POINT_CLOUD_FILE_NAME = 'points.csv'

    def init(self):
        # TODO: params from user input
        graph_scaling_method = 'MDS'
        graph_scaling_dimension = 3
        optimization_method = 'downhill'
        optimization_sample_size = 1

        # ensure the base data is a point cloud
        data_format = self.analysis.dataset.format
        points_file = self.ensure_points_file(
            data_format,
            graph_scaling_method,
            graph_scaling_dimension
        )

        # create initial sample data
        self.create_samples(optimization_sample_size)

    def tick(self):
        pass

    def create_samples(amount):
        for index in range(0, amount):
            pass
