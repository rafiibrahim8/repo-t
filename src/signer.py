import os

from gpg import GPG
from utils import logger

class Signer:
    def __init__(self, repo_dir, gpghome, signkeyid=None):
        if signkeyid is None:
            signkeyid = GPG(gpghome).get_default_keyid()
        logger.info(f'Using key {signkeyid} to sign packages')
        self.__signer = GPG(gpghome).signer(signkeyid)
        self.__repo_dir = repo_dir
    
    def sign(self, file_path):
        logger.info(f'Signing {file_path}')
        file_path = os.path.expanduser(file_path)
        sig_path = f'{file_path}.sig'
        self.__signer.sign(file_path, sig_path)
    
    def sign_all(self):
        for file in os.listdir(self.__repo_dir):
            if file.endswith('.sig') or file.endswith('.db'):
                continue
            if os.path.exists(os.path.join(self.__repo_dir, f'{file}.sig')):
                continue
            self.sign(os.path.join(self.__repo_dir, file))
