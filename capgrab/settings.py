import os

DIR = os.path.abspath(os.path.dirname(__file__))
TEMP_DIR = os.path.join(os.path.dirname(DIR), 'tmp')

S3_BUCKET_NAME = 'capwnd'
S3_ACCESS_KEY = '0EMND7QMCXGS6ANXQKG2'
S3_SECRET_KEY = '1A6+dA7H89agWY7vmp8J/w7Y76BxCPfHuLPWqqhM'

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

BROKER_HOST = REDIS_HOST
BROKER_PORT = REDIS_PORT
BROKER_VHOST = 0

CARROT_BACKEND = 'ghettoq.taproot.Redis'
CELERYBEAT_SCHEDULE_FILENAME = os.path.join(TEMP_DIR, 'celery-beat')
CELERY_ALWAYS_EAGER = False
CELERY_EAGER_PROPAGATES_EXCEPTIONS = False
CELERY_RESULT_BACKEND = 'redis'
CELERY_IMPORTS = ('capgrab.tasks',)

URL_TIMEOUT = 30
STALE_AFTER = 4320000  # 5 days
SCREENGRAB_FORMAT = 'jpg'

CUTYCAP = '/Users/seanbrant/Desktop/cutycapt/CutyCapt/CutyCapt.app/Contents/MacOS/CutyCapt'

DEFAULT_FOLDER = 'default'
DEFAULT_SIZE = 't'
FULL_SIZE = 'l'
IMAGE_SIZES = {
    's': (75, 75),
    't': (100, 63),
    'm': (640, 400),
    'l': (1024, 640),
}
