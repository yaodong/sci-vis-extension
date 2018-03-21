from celery import shared_task
from analyses.models import Analysis
from analyses.processes.sphere_evenly_sampling import SphereEvenlySampling
from analyses.processes.best_linear_projection import BestLinearProjection
import logging

PROCESS_CLASSES = {
    'sphere_evenly_sampling': SphereEvenlySampling,
    'search_best_linear_projection': BestLinearProjection
}


@shared_task()
def analysis_process(instance_id):
    logging.info('analysis opened: %i' % instance_id)
    analysis = Analysis.objects.get(pk=instance_id)

    # TODO params from user
    params = analysis.params
    process_class = PROCESS_CLASSES[params['process']]

    process = process_class(analysis)
    process.run()
