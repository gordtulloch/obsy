from django.core.management.base import BaseCommand
from targets.models import SimbadType
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Refresh SIMBAD types to object class table'

    def handle(self, *args, **kwargs):
        # Delete all records
        for targetObj in SimbadType.objects.all():
            targetObj.delete()
        
        # Import all records
        try:
            SimbadType.populate_db()
        except Exception as e:
            logger.error('Failed to import Simbad Type records')
            logger.error(e)
            return
        
        logger.info('Successfully imported Simbad Type records')