from celery import shared_task


@shared_task()
def analysis_process(instance_id):
    print("=" * 10)
    print('process')
    print("=" * 10)
    analysis_open.delay(instance_id)


@shared_task()
def analysis_open(instance_id):
    print("=" * 10)
    print('open')
    print("=" * 10)
    analysis_optimize.delay(instance_id, 0)


@shared_task()
def analysis_optimize(instance_id, iteration_index):
    print(iteration_index)
    print("=" * 10)
    print('iteration index %i' % iteration_index)
    print("=" * 10)
    if iteration_index > 10:
        analysis_close.delay(instance_id)
    else:
        analysis_optimize.delay(instance_id, iteration_index + 1)

@shared_task()
def analysis_close(instance_id):
    print("=" * 10)
    print('close')
    print("=" * 10)
