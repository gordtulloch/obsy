from django.core.management.base import BaseCommand
from targets.models import Target

class Command(BaseCommand):
    help = 'Set Rise / Transit / Set times for all Targets'

    def handle(self, *args, **kwargs):
        # Load all target records
        targets = Target.objects.all()
        for target in targets:
            target.set_rise_transit_set()
            target.save()

        self.stdout.write(self.style.SUCCESS('Successfully reset all config records'))
