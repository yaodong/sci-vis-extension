import math


def project_point_cloud(points, altitude, azimuth):
    return [project_point(coord, altitude, azimuth) for coord in points]


def project_point(coordinate, altitude, azimuth):
    # rotate coordinate in negative direction to make X-axis as desired projection direction

    # altitude: from x to z
    # rotate: from z to x
    coordinate = rotate_coordinates(coordinate, altitude, 2, 0)

    # azimuth: from x to y
    # rotate: from y to x
    coordinate = rotate_coordinates(coordinate, azimuth, 1, 0)

    # look from X-axis
    return coordinate[1], coordinate[2]


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

    x, y = row[dim_from], row[dim_to]
    row[dim_from] = cos_alpha * x - sin_alpha * y
    row[dim_to] = sin_alpha * x + cos_alpha * y
    return row
