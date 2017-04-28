from sympy import *

SPHERE_FIBONACCI_INCREMENT = math.pi * (3.0 - math.sqrt(5.0))


def sphere_fibonacci_samples(samples=500):
    points = []
    rnd = 1.0
    offset = 1.0 / samples

    for i in range(samples):
        y = ((i * offset) - 1) + (offset / 2)
        r = math.sqrt(1 - pow(y, 2))

        phi = ((i + rnd) % samples) * SPHERE_FIBONACCI_INCREMENT

        x = math.cos(phi) * r
        z = math.sin(phi) * r

        points.append([x, y, z])

    return points
