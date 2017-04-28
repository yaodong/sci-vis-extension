import numpy as np
from os import path
from celery import shared_task
from jobs.utils.files import count_file_lines
from jobs.utils.dipha import *
from jobs.utils.graph import *
from jobs.utils.sphere import *
from jobs.utils.point_cloud import project_point_cloud
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import animation


@shared_task()
def compute_graph(job_id, data_file):
    work_dir = path.dirname(data_file)

    distance_matrix = compute_distance_matrix(data_file)

    distance_matrix_file = path.join(work_dir, 'base_distance_matrix.bin')
    save_dipha_distance_matrix(distance_matrix_file, distance_matrix)

    points_file = path.join(work_dir, 'base_points')
    points = multidimensional_scaling(distance_matrix)
    make_base_preview_image(points, work_dir, 'base')

    directions = random_directions()

    for altitude, azimuth in directions:
        projected_point_cloud = project_point_cloud(points, altitude, azimuth)
        make_projection_preview_image(projected_point_cloud, work_dir, '%s_%s' % (altitude, azimuth))


def make_projection_preview_image(coordinates, work_dir, basename):
    image_file_path = path.join(work_dir, '%s-preview.png' % basename)

    from matplotlib import pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for x, y in coordinates:
        ax.scatter(x, y, s=2, alpha=0.7, c="m")

    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    plt.axis('equal')
    plt.savefig(image_file_path, dpi=150)
    plt.close()


def make_base_preview_image(coordinates, workdir, basename):
    image_file_path = path.join(workdir, '%s-preview.gif' % basename)

    from matplotlib import pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot(111, projection=Axes3D.name)

    def init():
        logging.info('init animate')
        for x, y, z in coordinates:
            ax.scatter(x, y, z, s=2, alpha=0.7, c="m")

    def animate(i):
        logging.info('frame %i' % i)
        ax.view_init(elev=i * 5, azim=i * 5)

    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=55, repeat_delay=1000)
    anim.save(image_file_path, writer='imagemagick', fps=8)
    plt.close()
