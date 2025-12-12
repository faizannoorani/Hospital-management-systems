
import os
from celery import Celery

# Tell Celery to use your Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Hospital.settings')

app = Celery('Hospital')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Use local Redis on port 6379
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'

app.autodiscover_tasks()

# Optional: add a debug beat schedule for testing
app.conf.beat_schedule = {
    "test-task-every-minute": {
        "task": "myapp.tasks.check_pending_amounts",
        "schedule": 60.0,  # seconds
        "args": (),
    },
}
