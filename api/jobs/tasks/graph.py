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
    np.save(path.join(work_dir, 'base_points'), points)

    # make_base_preview_image(points, work_dir, 'base')

    directions = sphere_random_directions()
    for index, (altitude, azimuth) in enumerate(directions):
        compute_projected_graph(job, index, points, base_graph, base_diagram, work_dir, altitude, azimuth)


def compute_projected_graph(job, index, base_points, base_graph, base_diagram, work_dir, altitude, azimuth):
    logging.info('processing direction %i' % index)
    job.output('direction_%i' % index, (altitude, azimuth))

    points = project_point_cloud(base_points, altitude, azimuth)
    np.save(path.join(work_dir, 'projected_%i_points' % index), points)

    make_projection_preview_image(points, work_dir, index)
    make_projection_preview_image_linked(points, base_graph, work_dir, index)

    distance_matrix = compute_points_distance_matrix(points)

    dipha_in_file = path.join(work_dir, 'projected_%i_dipha' % index)
    dipha_save_distance_matrix(distance_matrix, dipha_in_file)

    dipha_out_file = dipha_exec(dipha_in_file)
    diagram_file = dipha_extract_diagram(dipha_out_file, 'projected_%i_dipha' % index)

    bn_distance = calculate_bottleneck_distance(base_diagram, diagram_file)

    job.output('bn_distance_%i' % index, bn_distance)


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


def make_projection_preview_image_linked(coordinates, base_graph, work_dir, basename):
    image_file_path = path.join(work_dir, '%s-preview-linked.png' % basename)

    from matplotlib import pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for x, y in coordinates:
        ax.scatter(x, y, s=2, alpha=0.7, c="m")

    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    for node_from, node_to, weight in base_graph:
        coord_from = list(coordinates[node_from - 1])
        coord_to = list(coordinates[node_to - 1])
        ax.plot([coord_from[0], coord_to[0]], [coord_from[1], coord_to[1]])

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
