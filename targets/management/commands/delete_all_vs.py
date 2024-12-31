from django.core.management.base import BaseCommand
from targets.models import GCVS
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Delete variable star data from GCVS table'

    def handle(self, *args, **kwargs):
        # Delete all records
        GCVS.objects.all().delete()
               
        logger.info('Successfully deleted all variable star records')