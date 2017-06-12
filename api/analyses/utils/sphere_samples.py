import random
from numpy import *

__all__ = ['sphere_random_directions']


# Cartesian to Horizontal
def sphere_random_directions(amount=150):
    """
    :param amount:
    :return: radians
    """
    directions = []
    points = _fibonacci_sphere(amount * 2)  # whole sphere
    for x, y, z in points:
        if z < 0:
            continue

        if x == 0:
            if y > 0:
                longitude = .5
            else:
                longitude = -.5
        else:
            longitude = arctan2(y, x) * 180 / pi

        if z == 0:
            latitude = 0
        else:
            latitude = arcsin(z / sqrt(x * x + y * y + z * z)) * 180 / pi

        directions.append((longitude, latitude))

    return directions[0:amount]


def _fibonacci_sphere(samples=300, randomize=True):
    rnd = 1.
    if randomize:
        rnd = random.random() * samples

    points = []
    offset = 2. / samples
    increment = pi * (3. - sqrt(5.))

    for i in range(samples):
        y = ((i * offset) - 1) + (offset / 2)
        r = sqrt(1 - pow(y, 2))

        phi = ((i + rnd) % samples) * increment

        x = cos(phi) * r
        z = sin(phi) * r

        points.append([x, y, z])

    return points
