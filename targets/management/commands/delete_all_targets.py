from django.core.management.base import BaseCommand
from targets.models import Target

class Command(BaseCommand):
    help = 'Delete all Target records'

    def handle(self, *args, **kwargs):
        # Delete all Target records
        for targetObj in Target.objects.all():
            targetObj.delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all Target records'))