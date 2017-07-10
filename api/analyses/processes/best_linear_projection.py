from analyses.processes import Process
from scipy import optimize
from random import random, randint
from os import path
from copy import deepcopy
import numpy as np
import logging
from analyses.utils import scripts


class BestLinearProjection(Process):

    CONVERTED_POINT_CLOUD_FILE_NAME = 'points.csv'

    iteration = 0
    state_b1 = None
    state_b2 = None

    def __init__(self, analysis):
        super().__init__(analysis)

        self.graph_scaling_dimentions = int(self.params.get('scaling_dimension'))
        self.searching_max_iterations = int(self.params.get('max_iterations'))
        self.searching_algorithm = self.params.get('searching_algorithm')

        self.points = self.convert_to_points(
            method='MDS',
            dimension=self.graph_scaling_dimentions)

        # random pick a basis
        v1 = self.make_random_vec()
        v2 = self.make_random_vec()

        self.state_b1, self.state_b2 = self.make_unit_basis_vec(v1, v2)

    def run(self):

        self.process_base_graph()
        self.tda_max_scale = self.compute_r_max_scale()

        guess = self.make_unit_vec(self.make_random_vec())

        process = self

        def objective_func(guess):

            process.iteration += 1

            logging.info('iteration %i' % process.iteration)

            last_b1 = process.state_b1
            last_b2 = process.state_b2

            proj_b1 = last_b1 - process.ortho_projection(last_b1, guess)[1]
            proj_b2 = last_b2 - process.ortho_projection(last_b2, guess)[1]

            b1, b2 = process.make_unit_basis_vec(proj_b1, proj_b2)

            matrix = process.make_projection_matrix(b1, b2)

            plane_points = []
            for p in process.points:
                point = deepcopy(p)
                point_hat = process.project_on_matrix(point, matrix)
                x = process.ortho_projection(point_hat, b1)[0]
                y = process.ortho_projection(point_hat, b2)[0]
                plane_points.append((x, y))

            distance = process.calculate_distance(plane_points)

            # set states
            process.state_b1 = b1
            process.state_b2 = b2

            # write result
            self.contexts.write('iteration.%i' % process.iteration, {
                'index': process.iteration,
                'b1': list(b1),
                'b2': list(b2),
                'guess': list(guess),
                'distance': float(distance)
            })

            return distance

        if self.searching_algorithm == 'nelder-mead':
            optimize.minimize(objective_func, guess, method='Nelder-Mead')
        elif self.searching_algorithm == 'basin-hopping':
            step_size = pow(5, self.graph_scaling_dimentions - 3)
            optimize.basinhopping(objective_func, guess, stepsize=step_size)
        elif self.searching_algorithm == 'downhill-simplex':
            optimize.fmin(objective_func, guess, xtol=0.1)

    def process_base_graph(self):
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

    def make_random_vec(self):
        return [randint(-10000, 10000) for _ in range(0, self.graph_scaling_dimentions)]

    @staticmethod
    def make_unit_vec(u):
        bottom = np.linalg.norm(u)
        return u / bottom

    @staticmethod
    def ortho_projection(of_vec, on_vec):
        '''
        This function will compute the length(magnitude) and vector
        projection of given two vectors. of_vector -
        vector whose projection would computed ,
        on_vector - simply the projection surface,in 2D is it s line.

        >>> ortho_projection([4,4], [1,0])
        >>> (4,[4,0])
        '''
        v1 = np.array(of_vec)
        v2 = np.array(on_vec)
        scal = np.dot(v2, v1) / np.dot(v2, v2)
        vec = scal * v2
        return round(scal, 10), np.around(vec, decimals=10)

    @classmethod
    def make_unit_basis_vec(self, v1, v2):
        # make unit vector
        b1 = self.make_unit_vec(v1)
        v2_prep = v2 - self.ortho_projection(v2, b1)[1]
        b2 = self.make_unit_vec(v2_prep)

        return b1, b2

    @staticmethod
    def make_projection_matrix(b1, b2):
        p1 = np.outer(b1, b1)
        p2 = np.outer(b2, b2)

        return p1 + p2

    @staticmethod
    def project_on_matrix(x, matrix):
        return np.dot(matrix, x)

    @classmethod
    def project_on_basis(cls, x, b1, b2):
        matrix = cls.make_projection_matrix(b1, b2)
        return np.dot(matrix, x)

    def calculate_distance(self, points):
        index = self.iteration

        # save points
        projected_points_file = path.join(self.work_dir,
                                          'projected_%i_points' % index)
        np.save(projected_points_file, points)

        self.make_projection_preview_image(points, index)

        # call R to generate diagram and calculate bottleneck distance
        scripts.r('projected_graph.r', self.work_dir, index, self.tda_max_scale)

        result_file = path.join(self.work_dir, 'projected_%i_results.csv' % index)

        import csv
        bottleneck = None
        wasserstein = None
        with open(result_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                bottleneck = float(row['bottleneck'])
                wasserstein = float(row['wasserstein'])
                break

        distance = bottleneck

        logging.info('distance %s' % distance)
        return distance

    def make_projection_preview_image(self, coordinates, index):
        name_format = 'projected_%s_preview_dots.png'
        image_path = path.join(self.work_dir, name_format % index)

        from matplotlib import pyplot as plt

        fig = plt.figure(figsize=(5, 5))
        ax = fig.add_subplot(111)

        for x, y in coordinates:
            ax.scatter(x, y, s=4, c="#4e8bae", zorder=2, edgecolors='k', linewidths=0.5)

        #ax.xaxis.set_visible(False)
        #ax.yaxis.set_visible(False)

        plt.savefig(image_path, dpi=600)

        plt.close()
