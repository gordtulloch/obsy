from django.core.management.base import BaseCommand
from targets.models import NasaExplanetArchive
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Refresh cumulative exoplanet data from NASA Exoplanet Archive'

    def handle(self, *args, **kwargs):
        # Delete all records
        for targetObj in NasaExplanetArchive.objects.all():
            targetObj.delete()
        
        # Import all records
        try:
            NasaExplanetArchive.refresh_exoplanet_db()
        except Exception as e:
            logger.error('Failed to import NasaExoplanetArchive records')
            logger.error(e)
            return
        
        logger.info('Successfully imported all NasaExoplanetArchive records')