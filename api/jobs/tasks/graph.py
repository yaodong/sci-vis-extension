from celery import shared_task
from jobs.utils.graph import *
from jobs.utils.job import job_get
from jobs.utils.sphere import sphere_random_directions
from jobs.utils.point_cloud import project_point_cloud
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import animation
import numpy as np
import logging

PROGRESS_PREVIEW_READY = 5
PROGRESS_ALMOST_DONE = 95

FILE_TYPE_DELIMITERS = {
    'text/tab-separated-values': '\t',
    'text/csv': ',',
}


@shared_task()
def compute_graph(job_id, data_file):
    job = job_get(job_id)

    logging.info('start job %i' % job_id)

    work_dir = path.dirname(data_file)
    distance_matrix_file = path.join(work_dir, 'base_distance_matrix')

    data_delimiter = FILE_TYPE_DELIMITERS[job.params['file_meta']['mimetype']]
    base_graph = graph_load(data_file, delimiter=data_delimiter)

    distance_matrix = graph_distance_matrix(base_graph)
    np.save(distance_matrix_file, distance_matrix)

    points = multidimensional_scaling(distance_matrix)
    points_file = path.join(work_dir, 'base_points')
    np.save(points_file, points)

    make_base_preview_image(points, base_graph, work_dir)

    call_r_script('base_graph.r', work_dir)

    directions = sphere_random_directions(300)
    direction_results = {}

    progress_step = round((PROGRESS_ALMOST_DONE - PROGRESS_PREVIEW_READY) / len(directions), 2)

    for index, (longitude, latitude) in enumerate(directions):

        protected_points = project_point_cloud(points, longitude, latitude)
        projected_points_file = path.join(work_dir, 'projected_%i_points' % index)
        np.save(projected_points_file, protected_points)

        make_projection_preview_image(protected_points, base_graph, work_dir, index)

        # call r to generate diagram and calculate bottleneck distance
        call_r_script('projected_graph.r', work_dir, index)

        result_file = path.join(work_dir, 'projected_%i_distance.txt' % index)
        distance = float(open(result_file).read())

        direction_results[index] = {
            'index': index,
            'longitude': longitude,
            'latitude': latitude,
            'distance': distance
        }

        if job.progress < PROGRESS_PREVIEW_READY:
            job.progress = PROGRESS_PREVIEW_READY
        else:
            job.progress = round(job.progress + progress_step, 2)
        job.save()

    job.results = {
        'best': min(direction_results.values(), key=lambda d: d['distance'])['index'],
        'worst': max(direction_results.values(), key=lambda d: d['distance'])['index'],
        'directions': direction_results
    }
    job.progress = 100
    job.status = job.STATUS_DONE
    job.save()


def make_projection_preview_image(coordinates, base_graph, work_dir, index):
    image_path = path.join(work_dir, 'projected_%s_preview_dots.png' % index)
    linked_image_path = path.join(work_dir, 'projected_%s_preview_graph.png' % index)

    from matplotlib import pyplot as plt

    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111)

    for x, y in coordinates:
        ax.scatter(x, y, s=4, c="#4e8bae", zorder=2, edgecolors='k', linewidths=0.5)

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    plt.savefig(image_path, dpi=600)

    for node_from, node_to, weight in base_graph:
        coord_from = list(coordinates[node_from - 1])
        coord_to = list(coordinates[node_to - 1])
        ax.plot([coord_from[0], coord_to[0]], [coord_from[1], coord_to[1]], linewidth=0.5, color='#4e8bae', zorder=1)

    plt.savefig(linked_image_path, dpi=600)

    plt.close()


def make_base_preview_image(coordinates, base_graph, workdir):
    image_file_path = path.join(workdir, 'base_preview.gif')

    from matplotlib import pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot(111, projection=Axes3D.name)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])

    def init():
        logging.info('init animate')
        for x, y, z in coordinates:
            ax.scatter(x, y, z, s=4, c="#4e8bae", edgecolors='k', linewidths=0.2)

    def animate(i):
        logging.info('frame %i' % i)
        ax.view_init(elev=i * 5, azim=i * 5)

    for node_from, node_to, weight in base_graph:
        coord_from = list(coordinates[node_from - 1])
        coord_to = list(coordinates[node_to - 1])
        ax.plot([coord_from[0], coord_to[0]], [coord_from[1], coord_to[1]], [coord_from[2], coord_to[2]],
                linewidth=1,
                color='#4e8bae', zorder=1)

    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=55, repeat_delay=1000)
    anim.save(image_file_path, writer='imagemagick', fps=8, dpi=300)
    plt.close()


def generate_base_persistence_diagram(work_dir):
    chdir(path.join(settings.BASE_DIR, 'scripts'))
    command = 'Rscript diagram.r %s' % work_dir
    p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    p.communicate(timeout=15)
