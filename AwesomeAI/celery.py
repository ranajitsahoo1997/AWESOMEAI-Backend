import os
from celery import Celery

# set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AwesomeAI.settings')

app = Celery('AwesomeAI')

# Load settings from Django settings, using `CELERY_` namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks from installed apps
app.autodiscover_tasks()
