import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = '33stanlake#'

DEBUG = True

APP_TITLE = 'Data Driven Simulation Management API'

VERSION = '0.1-dev'

MONGODB_SETTINGS = {
    'db': 'ddsm-production',
    'host': 'localhost',
    'port': 27017
}


