from django.core.management.base import BaseCommand
from config.models import GeneralConfig, CommunicationsConfig, RepositoryConfig

class Command(BaseCommand):
    help = 'Delete all Config records'

    def handle(self, *args, **kwargs):
        # Delete all Config records
        GeneralConfig.objects.all().delete()
        CommunicationsConfig.objects.all().delete()
        RepositoryConfig.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Successfully deleted all config records'))