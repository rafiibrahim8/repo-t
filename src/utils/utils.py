import subprocess
import threading
import requests
import logging
import base64
import json
import time
import sys
import os

__all__ = ['get_temp_dir', 'notify', 'logger', 'get_sys_info', 'keep_alive_mount']

def get_temp_dir():
    random = base64.urlsafe_b64encode(os.urandom(9)).decode('utf-8')
    temp_dir = os.path.join('/tmp', 'private-arch-repo', random)
    os.makedirs(temp_dir)
    return temp_dir

def notify(message):
    if os.environ.get('DISCORD_WEBHOOK_URL'):
        requests.post(os.environ['DISCORD_WEBHOOK_URL'], json={'content': message})

def get_sys_info():
    info = {
        'os': os.uname(),
        'bsdtar': subprocess.check_output(['bsdtar', '--version']).decode('utf-8').split('\n')[0],
        'docker': subprocess.check_output(['docker', '--version']).decode('utf-8').split('\n')[0],
        'curl': subprocess.check_output(['curl', '--version']).decode('utf-8').split('\n')[0],
        'python': f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
    }
    return json.dumps(info, indent=4)

def keep_alive_mount(location):
    def keep_alive_mount_thread():
        while True:
            subprocess.check_output(['ls','-la', location])
            time.sleep(1)
    thread = threading.Thread(target=keep_alive_mount_thread)
    thread.daemon = True
    thread.start()

logger = logging.getLogger('private-arch-repo')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
