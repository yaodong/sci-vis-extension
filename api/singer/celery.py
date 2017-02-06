import os
from celery import Celery

# More details at:
# http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'singer.settings')

app = Celery('singer')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
