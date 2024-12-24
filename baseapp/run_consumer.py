import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'mainapp')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baseapp.settings')

import django
django.setup()

from mainapp.consumer import message_handler
from mainapp.rabbitmq import consume_messages

if __name__ == '__main__':
    consume_messages(message_handler)
