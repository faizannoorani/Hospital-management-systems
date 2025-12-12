

from celery.schedules import crontab

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hospital_db',
        'USER': 'root',
        'PASSWORD': 'faizan123@A1',
        'HOST': '127.0.0.1',  # Docker mapped host
        'PORT': '3307',       # Maps to container 3306
    }
}


CELERY_BROKER_URL = "redis://localhost:6380/0"
CELERY_RESULT_BACKEND = "redis://localhost:6380/0"

CELERY_BEAT_SCHEDULE = {
    "check-pending-amounts-every-minute": {
        "task": "myapp.tasks.check_pending_amounts",
        "schedule": crontab(minute="*/1"),
        "args": (),
    },
}
