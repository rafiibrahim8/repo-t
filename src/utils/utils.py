import requests
import logging
import base64
import os

__all__ = ['get_temp_dir', 'notify', 'logger']

def get_temp_dir():
    random = base64.urlsafe_b64encode(os.urandom(9)).decode('utf-8')
    temp_dir = os.path.join('/tmp', 'private-arch-repo', random)
    os.makedirs(temp_dir)
    return temp_dir

def notify(message):
    if os.environ.get('DISCORD_WEBHOOK_URL'):
        requests.post(os.environ['DISCORD_WEBHOOK_URL'], json={'content': message})

logger = logging.getLogger('private-arch-repo')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
