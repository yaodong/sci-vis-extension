import random
import math


# Cartesian to Horizontal
def sphere_random_directions(samples=150):
    """
    :param samples:
    :return: radians
    """
    directions = []
    points = _fibonacci_sphere(samples * 2)
    for x, y, z in points:
        if z < 0:
            continue

        if x == 0:
            if y > 0:
                azimuth = .5
            else:
                azimuth = -.5
        else:
            azimuth = math.atan(y / x)

        if z == 0:
            altitude = 0
        else:
            altitude = math.atan(z / math.sqrt(math.pow(x, 2) + math.pow(y, 2)))

        altitude = round(altitude, 5)
        azimuth = round(azimuth, 5)

        directions.append((altitude, azimuth))

    return directions


def _fibonacci_sphere(samples=300, randomize=True):
    rnd = 1.
    if randomize:
        rnd = random.random() * samples

    points = []
    offset = 2. / samples
    increment = math.pi * (3. - math.sqrt(5.))

    for i in range(samples):
        y = ((i * offset) - 1) + (offset / 2)
        r = math.sqrt(1 - pow(y, 2))

        phi = ((i + rnd) % samples) * increment

        x = math.cos(phi) * r
        z = math.sin(phi) * r

        points.append([x, y, z])

    return points
