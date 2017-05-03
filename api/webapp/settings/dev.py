from os import path
from webapp.settings.base import *

DATA_DIR = path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
