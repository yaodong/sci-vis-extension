from analyses.models import Analysis, Context


def echo(analysis, **args):
    return {
        'analysis': analysis.id,
        'arguments': args
    }


def best_linear_projection_iteration_chart(analysis):
    iterations = analysis.contexts \
        .query().filter(name__startswith='iteration.').all()

    iterations = list(map(lambda i: i.value, iterations))

    best = min(iterations, key=lambda i: i['distance'])

    return {
        'best': best,
        'iterations': iterations,
        'last': iterations[-1]
    }


def sphere_is_ready(analysis):
    query = analysis.contexts.query()
    try:
        preview_status = query.filter(name="preview.is_ready").get()
        return {'is_ready': bool(preview_status.value)}
    except Context.DoesNotExist:
        return {'is_ready': False}


def sphere_projection_data(analysis):
    query = analysis.contexts.query()
    try:
        sample_size_ct = query.filter(name='samples.size').get()
    except Context.DoesNotExist:
        return None

    sample_size = int(sample_size_ct.value)

    query = analysis.contexts.query()
    directions = {}
    for i in range(0, sample_size):

        try:
            result_ct = query.filter(name='projected.result.%i' % i).get()
            directions[result_ct.value['index']] = result_ct.value
        except Context.DoesNotExist:
            pass

    if directions:
        return directions
    else:
        return None
