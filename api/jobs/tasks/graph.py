from celery import shared_task
from jobs.utils.dipha import *
from jobs.utils.graph import *
from jobs.utils.job import job_get
from jobs.utils.sphere import sphere_random_directions
from jobs.utils.point_cloud import project_point_cloud
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import animation


@shared_task()
def compute_graph(job_id, data_file):
    job = job_get(job_id)

    work_dir = path.dirname(data_file)
    distance_matrix_file = path.join(work_dir, 'base_distance_matrix.bin')

    base_graph = graph_load(data_file)
    distance_matrix = graph_distance_matrix(base_graph)
    dipha_save_distance_matrix(distance_matrix, distance_matrix_file)

    dipha_out = dipha_exec(distance_matrix_file)
    base_diagram = dipha_extract_diagram(dipha_out, 'base')

    points = multidimensional_scaling(distance_matrix)

    generate_base_persistence_diagram(work_dir)

    make_base_preview_image(points, work_dir)

    directions = sphere_random_directions(30)

    direction_results = {}
    for index, (longitude, latitude) in enumerate(directions):
        print((index, longitude, latitude))
        direction_results[index] = compute_projected_graph(index, points, base_graph, base_diagram, work_dir, longitude,
                                                           latitude)

    job.results = {
        'best': min(direction_results.values(), key=lambda d: d['distance'])['index'],
        'worst': max(direction_results.values(), key=lambda d: d['distance'])['index'],
        'directions': direction_results
    }
    job.progress = 100
    job.status = job.STATUS_DONE
    job.save()


def compute_projected_graph(index, base_points, base_graph, base_diagram, work_dir, longitude, latitude):
    logging.info('processing direction %i' % index)

    points = project_point_cloud(base_points, longitude, latitude)
    np.save(path.join(work_dir, 'projected_%i_points' % index), points)

    make_projection_preview_image(points, base_graph, work_dir, index, index, longitude, latitude)
    distance_matrix = compute_points_distance_matrix(points)

    dipha_in_file = path.join(work_dir, 'projected_%i_dipha' % index)
    dipha_save_distance_matrix(distance_matrix, dipha_in_file)

    dipha_out_file = dipha_exec(dipha_in_file)
    diagram_file = dipha_extract_diagram(dipha_out_file, 'projected_%i_dipha' % index)

    distance = calculate_bottleneck_distance(diagram_file, base_diagram)
    return {
        'index': index,
        'longitude': longitude,
        'latitude': latitude,
        'distance': distance
    }


def make_projection_preview_image(coordinates, base_graph, work_dir, basename, index, longitude, latitude):
    image_path = path.join(work_dir, 'projected_%s_preview_dots.png' % basename)
    linked_image_path = path.join(work_dir, 'projected_%s_preview_graph.png' % basename)

    from matplotlib import pyplot as plt

    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111)

    for x, y in coordinates:
        ax.scatter(x, y, s=4, c="orange", zorder=2, edgecolors='#FFFFFF', linewidths=0.2)

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    plt.title('direction #%i' % index, loc='left')
    plt.title('ongitude %s  latitude %s' % (round(longitude, 3), round(latitude, 3)), loc='right')
    plt.axis('equal')
    plt.savefig(image_path, dpi=600)

    for node_from, node_to, weight in base_graph:
        coord_from = list(coordinates[node_from - 1])
        coord_to = list(coordinates[node_to - 1])
        ax.plot([coord_from[0], coord_to[0]], [coord_from[1], coord_to[1]], linewidth=0.5, color='0.8', zorder=1)

    plt.savefig(linked_image_path, dpi=600)

    plt.close()


def make_base_preview_image(coordinates, workdir):
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
            ax.scatter(x, y, z, s=4, c="orange", edgecolors='#FFFFFF', linewidths=0.2)

    def animate(i):
        logging.info('frame %i' % i)
        ax.view_init(elev=i * 5, azim=i * 5)

    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=55, repeat_delay=1000)
    anim.save(image_file_path, writer='imagemagick', fps=8, dpi=300)
    plt.close()


def generate_base_persistence_diagram(work_dir):
    chdir(path.join(settings.BASE_DIR, 'scripts'))
    command = 'Rscript diagram.r %s' % work_dir
    p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    p.communicate(timeout=15)
