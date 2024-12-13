from django.core.management.base import BaseCommand
from targets.models import target

class Command(BaseCommand):
    help = 'Delete all target records'

    def handle(self, *args, **kwargs):
        # Delete all Target records
        for targetObj in target.objects.all():
            targetObj.delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all Target records'))