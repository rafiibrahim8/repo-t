import os

from .docker_builders import AURBuilder, GitBuilder
from .pkg_downloader import PkgDownloader

from utils import logger
from errors import BuildFailedError

class Builder:
    def __init__(self, updates, repo_dir, packager_name, packager_email, gpghome=None):
        self.__packager_name = packager_name
        self.__packager_email = packager_email
        self.__repo_dir = repo_dir
        self.__updates = updates
        self.__builder_dict = {
            'repo': self.__build_repo,
            'aur': self.__build_aur,
            'git': self.__build_git
        }
        if gpghome is None:
            gpghome = os.path.expanduser('~/.gnupg')
        self.__gpg_home = gpghome
    
    def build(self):
        success, failed = [], []
        for pkg_type, packages in self.__updates.items():
            logger.info('Building %s packages', pkg_type)
            for package in packages:
                try:
                    self.__builder_dict[pkg_type](package)
                    logger.info('Successfully built %s', package['name'])
                    success.append(package['name'])
                except BuildFailedError as e:
                    logger.error(e)
                    failed.append(package['name'])
        return success, failed
    
    def __build_repo(self, package):
        downloader = PkgDownloader(self.__repo_dir, package['file-url'], package.get('keyid'), self.__gpg_home)
        downloader.download()
    
    def __build_aur(self, package):
        builder = AURBuilder(self.__packager_name, self.__packager_email, self.__repo_dir, package['name'])
        builder.build()
    
    def __build_git(self, package):
        builder = GitBuilder(self.__packager_name, self.__packager_email, self.__repo_dir, package['git_url'])
        builder.build()
