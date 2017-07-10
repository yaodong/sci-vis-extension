from analyses.models import Analysis


def echo(analysis, **args):
    return {
        'analysis': analysis.id,
        'arguments': args
    }


def best_linear_projection_iteration_chart(analysis):
    iterations = analysis.contexts\
                         .query().filter(name__startswith='iteration.').all()

    iterations = list(map(lambda i: i.value, iterations))

    best = min(iterations, key=lambda i: i['distance'])

    return {
        'best': best,
        'iterations': iterations,
        'last': iterations[-1]
    }
