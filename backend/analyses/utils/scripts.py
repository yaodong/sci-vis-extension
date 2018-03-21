from os import path, chdir
from django.conf import settings
from subprocess import Popen, PIPE
from time import sleep
import logging


def r(file, *args):
    chdir(path.join(settings.BASE_DIR, 'scripts'))
    command = 'Rscript %s ' % file
    command += ' '.join([str(i) for i in args])

    logging.debug(command)

    proc = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    while proc.poll() is None:
        sleep(0.3)
