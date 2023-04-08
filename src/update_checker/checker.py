import logging
import json
import os

from .repo import RepoUpdateChecker
from .aur import AURUpdateChecker
from .git import GitUpdateChecker

from utils import logger

class UpdateChecker:
    def __init__(self, db_path):
        self.__local_repo = RepoUpdateChecker(db_path)
    
    def check(self):
        logger.info('Checking for updates...')
        return {
            'aur': self.__check_aur_packages(),
            'repo': self.__check_repo_packages(),
            'git': self.__check_git_packages()
        }
        
    
    def __read_package_json(self, package_name):
        with open(os.path.join('packages', f'{package_name}.json'), 'r') as f:
            return json.load(f)

    def __check_aur_packages(self):
        logger.info('Checking AUR packages...')
        packages = self.__read_package_json('aur')
        aur_checker = AURUpdateChecker(packages)
        
        update_available = []
        for package_name in packages:
            if self.__local_repo.get_version(package_name) != aur_checker.get_version(package_name):
                update_available.append({'name': package_name, 'old-filename': self.__local_repo.get(package_name, 'filename')})
        return update_available

    def __check_repo_packages(self):
        logger.info('Checking repo packages...')
        packages = self.__read_package_json('repo')
        
        update_available = []
        for package in packages:
            update_checker = RepoUpdateChecker(f"{package['repo-url']}/{package['repo-name']}.db")
            if self.__local_repo.get_version(package['name']) != update_checker.get_version(package['name']):
                package['file-url'] = f"{package['repo-url']}/{update_checker.get(package['name'], 'filename')}"
                package['old-filename'] = self.__local_repo.get(package['name'], 'filename')
                update_available.append(package)
        return update_available
    
    def __check_git_packages(self):
        logger.info('Checking git packages...')
        packages = self.__read_package_json('git')

        update_available = []
        for package in packages:
            git_checker = GitUpdateChecker(package.get('git_url'), package.get('pkgbuild-url'))
            if self.__local_repo.get_version(package['name']) != git_checker.get_version(package['name']):
                package['old-filename'] = self.__local_repo.get(package['name'], 'filename')
                update_available.append(package)
        return update_available
