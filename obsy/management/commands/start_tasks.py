from django.core.management.base import BaseCommand
from celery.schedules import crontab
from observations.tasks import daily_observations_task
from celery import Celery
import logging

logger = logging.getLogger(__name__)

app = Celery('obsy')
app.config_from_object('django.conf:settings', namespace='CELERY')

class Command(BaseCommand):
    help = "Starts Celery Tasks for the Observations App"

    def handle(self, *args, **options):
        logger.info("Starting Celery Tasks for the Observations App")

        # Schedule the daily_observations_task to run every day at 10:00 AM
        app.conf.beat_schedule = {
            'daily-observations-task': {
                'task': 'observations.tasks.daily_observations_task',
                'schedule': crontab(hour=10, minute=0),
            },
        }

        logger.info("- Daily Observations Task scheduled to run every day at 10:00 AM")