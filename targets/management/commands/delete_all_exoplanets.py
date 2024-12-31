from django.core.management.base import BaseCommand
from targets.models import NasaExplanetArchive
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Delete cumulative exoplanet data from NASA Exoplanet Archive'

    def handle(self, *args, **kwargs):
        # Delete all records
        NasaExplanetArchive.objects.all().delete()
               
        logger.info('Successfully deleted all NasaExoplanetArchive records')