import math
from copy import deepcopy


def project_point_cloud(points, longitude, latitude):
    projected = []
    for p in points:
        projected.append([float(c) for c in project_point(p, longitude, latitude)])

    return projected


def project_point(coordinate, longitude, latitude):
    # rotate coordinate in negative direction to make X-axis as desired projection direction

    # longitude, from y to x
    projected = rotate_coordinates(coordinate, longitude * math.pi / 180, 1, 0)

    # latitude, from z to x
    projected = rotate_coordinates(projected, latitude * math.pi / 180, 2, 0)

    # look from X-axis
    return [projected[1], projected[2]]


def rotate_coordinates(row, radian, dim_from, dim_to):
    """
    dim:
      - 0: x
      - 1: y
      - 2: z
    angle:
        radian
    """
    cos_alpha, sin_alpha = math.cos(radian), math.sin(radian)

    new_row = deepcopy(row)
    x, y = new_row[dim_from], new_row[dim_to]
    new_row[dim_from] = cos_alpha * x - sin_alpha * y
    new_row[dim_to] = sin_alpha * x + cos_alpha * y
    return new_row
