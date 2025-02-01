from django.core.management.base import BaseCommand
from config.models import GeneralConfig, CommunicationsConfig, RepositoryConfig

class Command(BaseCommand):
    help = 'Reset all Config records'

    def handle(self, *args, **kwargs):
        # Delete all Config records
        GeneralConfig.objects.all().delete()
        CommunicationsConfig.objects.all().delete()
        RepositoryConfig.objects.all().delete()
        '''
        # Fetch or create the first record for each configuration model with default values
        general_config, created = GeneralConfig.objects.get_or_create(
            id=1,
            defaults={'latitude': 0.0, 'longitude': 0.0, 'elevation': 0}
        )
        general_config.save()
        communications_config, created = CommunicationsConfig.objects.get_or_create(
            id=1,
            defaults={
                'email_host': 'smtp.gmail.com',
                'email_port': 587,
                'email_use_tls': True,
                'email_host_user': 'email@gmail.com',
                'email_host_password': 'secret',
                'sender_email': 'email@gmail.com',
                'recipient_email': 'email@gmail.com',
            }
        )
        communications_config.save()
        repository_config, created = RepositoryConfig.objects.get_or_create(
            id=1,
            defaults={
                'ppsourcepath': '/home/user/REPOSITORY.Incoming',
                'pprepopath': '/home/user/REPOSITORY'
            }
        )
        repository_config.save()'''

        self.stdout.write(self.style.SUCCESS('Successfully reset all config records'))