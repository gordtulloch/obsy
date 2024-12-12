from django.core.management.base import BaseCommand
import pika
from observations.tasks import process_fits_file
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Consume FITS files from RabbitMQ and process them'

    def handle(self, *args, **options):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='fits_files', durable=True)

        def callback(ch, method, properties, body):
            file_path = body.decode()
            logger.info(f"Received FITS file: {file_path}")
            process_fits_file.delay(file_path)

        channel.basic_consume(queue='fits_files', on_message_callback=callback, auto_ack=True)
        logger.info('Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()