from celery import shared_task
from analyses.models import Analysis
from analyses.processes import sphere_evenly_sampling
import logging

PROCESS_CLASSES = {
    'sphere_evenly_samping': sphere_evenly_sampling.SphereEvenlySampling
}


@shared_task()
def analysis_process(instance_id):
    logging.info('analysis opened: %i' % instance_id)
    analysis = Analysis.objects.get(pk=instance_id)

    # TODO params from user
    params = analysis.params
    process_class = PROCESS_CLASSES[params['process']]

    process = process_class(analysis)
    try:
        while True:
            process.tick()
    except process.HasFinished:
        logging.info('analysis finished')
