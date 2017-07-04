from analyses.processes import Process
from scipy.optimize import minimize
from random import random
import numpy as np


class BestLinearProjection(Process):

    CONVERTED_POINT_CLOUD_FILE_NAME = 'points.csv'

    iteration = 0
    state_b1 = None
    state_b2 = None

    def __init__(self, analysis):
        super().__init__(analysis)

        self.graph_scaling_dimentions = int(self.params.get('scaling_dimension'))
        self.searching_max_iterations = int(self.params.get('max_iterations'))

        self.points = self.convert_to_points(
            method='MDS',
            dimension=self.graph_scaling_dimentions)

        # random pick a basis
        v1 = [random() for _ in range(0, self.graph_scaling_dimentions)]
        v2 = [random() for _ in range(0, self.graph_scaling_dimentions)]

        self.current_b1, self.current_b2 = self.make_unit_basis_vec(v1, v2)

    def run(self):

        guess = self.make_unit_vec([random() for _ in range(0, self.graph_scaling_dimentions)])

        def objective_func(guess, *args):
            process = args[0]

            process.iteration += 1

            last_b1 = process.state_b1
            last_b2 = process.state_b2

            current_b1 = last_b1 - process.ortho_projection(last_b1, guess)
            current_b2 = last_b2 - process.ortho_projection(last_b2, guess)

            matrix = process.make_projection_matrix(current_b1, current_b2)

            plane_points = []
            for point in process.points:
                point_hat = process.project_on_matrix(matrix, point)
                x = process.ortho_projection(point_hat, current_b1)[0]
                y = process.ortho_projection(point_hat, current_b2)[0]
                plane_points.append((x, y))

            distance = process.calculate_distance(plane_points)

            # set states
            process.state_b1 = current_b1
            process.state_b2 = current_b2

            return distance

        minimize(fun=objective_func, x0=guess, method='Nelder-Mead', args=(self,))



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
        return random()
