import os

from celery.schedules import crontab

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notify.settings")

app = Celery('notify')
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'create_messages': {
        'task': 'api.tasks.create_messages',
        'schedule': crontab(minute='*/5'),
    },
    'handle_messages': {
        'task': 'api.tasks.handle_messages',
        'schedule': crontab(minute='*/1'),
    },
}
