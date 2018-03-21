import math, random

# circle 1

points = []
for _ in range(300):
    theta = random.uniform(0, 359.9)
    z = random.uniform(0, 0.15)
    x = 1 - math.sin(theta) + random.uniform(-0.1, 0.1)
    y = 1 + math.cos(theta) + random.uniform(-0.1, 0.1)
    points.append([x, y, z])


# circle 2
for _ in range(300):
    theta = random.uniform(0, 359.9)
    y = random.uniform(0, 0.15)
    x = 1 - math.cos(theta) + random.uniform(-0.1, 0.1)
    z = 1 + math.sin(theta) + random.uniform(-0.1, 0.1)
    points.append([x, y, z])

for p in points:
    print('{0},{1},{2}'.format(*p))
