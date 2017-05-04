from os import environ
from webapp.settings.base import *

SECRET_KEY = environ.get("SECRET_KEY")

if SECRET_KEY is None or len(SECRET_KEY) < 50:
    raise Exception("The SECRET_KEY is empty or too short. The min length is 50.")

DEBUG = False

ALLOWED_HOSTS = ["demo-sci-tda-api.yaodong.org"]

DATA_DIR = "/srv/sci/tda/api/static"

