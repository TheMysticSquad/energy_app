# utility_cis/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "utility_cis.settings")
app = Celery("utility_cis")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
