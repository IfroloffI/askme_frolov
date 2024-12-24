import pika
import json
from django.conf import settings

def publish_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE)

    channel.basic_publish(exchange='',
                          routing_key=settings.RABBITMQ_QUEUE,
                          body=json.dumps(message))
    connection.close()

def consume_messages(callback):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE)

    def on_message(ch, method, properties, body):
        message = json.loads(body)
        callback(message)

    channel.basic_consume(queue=settings.RABBITMQ_QUEUE, on_message_callback=on_message, auto_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
