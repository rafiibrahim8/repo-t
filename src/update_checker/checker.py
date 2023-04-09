import json
import os

from .repo import RepoUpdateChecker
from .aur import AURUpdateChecker
from .git import GitUpdateChecker

from utils import logger

class UpdateChecker:
    def __init__(self, db_path):
        self.__repo_files = os.listdir(os.path.dirname(db_path))
        self.__local_repo = RepoUpdateChecker(os.path.expanduser(db_path))
    
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
        
        update_available = []
        for package_name in packages:
            aur_checker = AURUpdateChecker(package_name)
            if self.__local_repo.get_version(package_name) != aur_checker.get_version(package_name):
                update_available.append({'name': package_name})
                continue
            # Check if the file name has changed or the file has been removed
            if self.__local_repo.get(package_name, 'filename') not in self.__repo_files:
                update_available.append({'name': package_name})
        return update_available

    def __check_repo_packages(self):
        logger.info('Checking repo packages...')
        packages = self.__read_package_json('repo')
        
        update_available = []
        for package in packages:
            repo_checker = RepoUpdateChecker(f"{package['repo-url']}/{package['repo-name']}.db")
            package['file-url'] = f"{package['repo-url']}/{repo_checker.get(package['name'], 'filename')}"
            if self.__local_repo.get_version(package['name']) != repo_checker.get_version(package['name']):
                update_available.append(package)
                continue
            # Check if the file name has changed or the file has been removed
            if self.__local_repo.get(package['name'], 'filename') not in self.__repo_files:
                update_available.append(package)
        return update_available
    
    def __check_git_packages(self):
        logger.info('Checking git packages...')
        packages = self.__read_package_json('git')

        update_available = []
        for package in packages:
            git_checker = GitUpdateChecker(package.get('git_url'), package.get('pkgbuild-url'))
            if self.__local_repo.get_version(package['name']) != git_checker.get_version(package['name']):
                update_available.append(package)
                continue
            # Check if the file name has changed or the file has been removed
            if self.__local_repo.get(package['name'], 'filename') not in self.__repo_files:
                update_available.append(package)
        return update_available
