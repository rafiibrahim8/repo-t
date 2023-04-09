import subprocess
import shutil
import os

from utils import get_temp_dir, logger
from gpg import GPG
from errors import BuildFailedError

class PkgDownloader:
    def __init__(self, dest, url, keyid=None, gpghome=None):
        self.__dest = dest
        self.__keyid = keyid
        self.__gpghome = gpghome
        self.__url = url
        self.__file_name = os.path.basename(url)
        self.__temp_dir = get_temp_dir()
    
    def download(self):
        self.__download(self.__url)
        self.__download(self.__url + '.sig')
        if not self.__verify():
            raise BuildFailedError('Verification failed')
        self.__move()
        self.__cleanup()
    
    def __download(self, url):
        logger.info('Downloading file from %s', url)
        try:
            subprocess.check_call(['curl', '-LO', '--fail-with-body', '--output-dir', self.__temp_dir, url])
        except subprocess.CalledProcessError:
            logger.error('Failed to download %s', url)
            raise BuildFailedError('Failed to download file')
    
    def __verify(self):
        if not self.__keyid:
            logger.warning('No keyid specified, skipping verification for %s', self.__file_name)
            return True
        file_path = os.path.join(self.__temp_dir, self.__file_name)
        sig_path = os.path.join(self.__temp_dir, self.__file_name + '.sig')

        verifier = GPG(self.__gpghome).verifier(self.__keyid)
        if not verifier.verify(file_path, sig_path):
            logger.error('Verification failed for %s', self.__file_name)
            return False
        return True
    
    def __move(self):
        shutil.move(os.path.join(self.__temp_dir, self.__file_name) , os.path.join(self.__dest, self.__file_name))
    
    def __cleanup(self):
        shutil.rmtree(self.__temp_dir)
