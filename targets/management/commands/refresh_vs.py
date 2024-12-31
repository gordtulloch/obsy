from django.core.management.base import BaseCommand
from targets.models import GCVS
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Refresh GCVS table from disk file standard_data/gvcs.csv'

    def handle(self, *args, **kwargs):
        logger.info(self.help)
        # Delete all records
        for targetObj in GCVS.objects.all():
            targetObj.delete()
        
        # Import all records
        try:
            GCVS.populate_db()
        except Exception as e:
            logger.error('Failed to import GCVS records')
            logger.error(e)
            return
        
        logger.info('Successfully imported GCVS records')