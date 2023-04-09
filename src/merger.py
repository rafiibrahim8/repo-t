import subprocess
import shutil
import os

from utils import logger, get_temp_dir
from update_checker import RepoUpdateChecker

class Merger:
    def __init__(self, new_db_path, old_db_path):
        assert new_db_path.endswith('.db')
        assert old_db_path.endswith('.db')
        self.__new_db_path = os.path.expanduser(new_db_path)
        self.__old_db_path = os.path.expanduser(old_db_path)
        self.__mkdirs()
    
    def __mkdirs(self):
        self.__temp_dir = get_temp_dir()
        self.__db_dir = os.path.join(self.__temp_dir, 'db')
        self.__files_dir = os.path.join(self.__temp_dir, 'files')
        self.__files_dir_old = os.path.join(self.__temp_dir, 'files_old')
        self.__files_dir_new = os.path.join(self.__temp_dir, 'files_new')
        self.__db_dir_old = os.path.join(self.__temp_dir, 'db_old')
        self.__db_dir_new = os.path.join(self.__temp_dir, 'db_new')

        os.makedirs(self.__db_dir)
        os.makedirs(self.__files_dir)
        os.makedirs(self.__files_dir_old)
        os.makedirs(self.__files_dir_new)
        os.makedirs(self.__db_dir_old)
        os.makedirs(self.__db_dir_new)
    
    def __move_from_old(self, dir_name):
        shutil.move(os.path.join(self.__db_dir_old, dir_name), os.path.join(self.__db_dir, dir_name))
        shutil.move(os.path.join(self.__files_dir_old, dir_name), os.path.join(self.__files_dir, dir_name))
    
    def __move_from_new(self, dir_name):
        shutil.move(os.path.join(self.__db_dir_new, dir_name), os.path.join(self.__db_dir, dir_name))
        shutil.move(os.path.join(self.__files_dir_new, dir_name), os.path.join(self.__files_dir, dir_name))

    @staticmethod
    def __extact_archive(arc_path, dest_dir):
        subprocess.check_call(['bsdtar', '-xf', arc_path, '-C', dest_dir])

    def merge(self):
        if not os.path.exists(self.__old_db_path):
            return logger.info('No old database found. Skipping merge')
        logger.info('Merging old and new database')
        new_db = RepoUpdateChecker(self.__new_db_path).get_full_dict()
        old_db = RepoUpdateChecker(self.__old_db_path).get_full_dict()

        self.__extact_archive(self.__new_db_path, self.__db_dir_new)
        self.__extact_archive(self.__old_db_path, self.__db_dir_old)
        self.__extact_archive(self.__new_db_path[:-3] + '.files', self.__files_dir_new)
        self.__extact_archive(self.__old_db_path[:-3] + '.files', self.__files_dir_old)

        for pkg_name, pkg in new_db.items():
            old_db[pkg_name] = pkg
        
        for pkg_name, pkg in old_db.items():
            dir_name = f'{pkg_name}-{pkg["version"]}'
            if os.path.exists(os.path.join(self.__db_dir_new, dir_name)):
                self.__move_from_new(dir_name)
            elif os.path.exists(os.path.join(self.__db_dir_old, dir_name)):
                self.__move_from_old(dir_name)
            else:
                raise Exception(f'Package {pkg_name} not found in old or new database')
        
        logger.info('Making new database')
        new_db_file_path = os.path.join(self.__temp_dir, os.path.basename(self.__new_db_path))
        new_files_file_path = os.path.join(self.__temp_dir, os.path.basename(self.__new_db_path)[: -3] + '.files')

        call_list = [
            'bsdtar',
            '--uid', '0',
            '--gid', '0',
            '-czf',
            new_db_file_path,
            '-C',
            self.__db_dir,
            '.'
        ]
        subprocess.check_call(call_list)
        logger.info('Making new files')
        call_list[-2] = self.__files_dir
        call_list[-4] = new_files_file_path
        subprocess.check_call(call_list)

        logger.info('Moving new database and files')
        shutil.move(new_db_file_path, self.__new_db_path)
        shutil.move(new_files_file_path, self.__new_db_path[: -3] + '.files')

def copy_dir_files(src, dest):
    for file in os.listdir(src):
        shutil.copy(os.path.join(src, file), os.path.join(dest, file))
