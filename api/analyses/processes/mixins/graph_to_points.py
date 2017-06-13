class GraphToPoints:

    def ensure_points_file(self, fmt, scaling_method, scaling_dimension):
        if fmt == 'graph':
            self.graph_to_points(scaling_method, scaling_dimension)
            points_file = self.CONVERTED_POINT_CLOUD_FILE_NAME
        else:
            points_file = 'base.csv' # TODO: fix hardcode

        # create initial sample data
        self.create_samples(optimization_inital_samples)


    def graph_to_points(self, scaling_method, scaling_dimention):
        pass
