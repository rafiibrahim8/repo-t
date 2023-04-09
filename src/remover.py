import os

from update_checker.repo import RepoUpdateChecker
from utils import logger

class Remover:
    def __init__(self, db_path):
        self.__repo_dir = os.path.dirname(db_path)
        self.__repo = RepoUpdateChecker(db_path)
    
    def __remove(self, path):
        logger.info('Removing file: ' + path)
        sig_file = path + '.sig'
        if os.path.exists(path):
            os.remove(path)
        if os.path.exists(sig_file):
            os.remove(sig_file)

    def remove(self):
        filenames = []
        for pkg in self.__repo.get_full_dict().values():
            filenames.append(pkg['filename'])

        for filename in os.listdir(self.__repo_dir):
            if filename not in filenames:
                if filename.endswith('.db') or filename.endswith('.sig') or filename.endswith('.files'):
                    continue
                self.__remove(os.path.join(self.__repo_dir, filename))
