from .docker_builders import AURBuilder, GitBuilder
from .pkg_downloader import PkgDownloader

from utils import logger
from errors import BuildFailedError

class Builder:
    def __init__(self, updates, gpghome, repo_dir, packager_name, packager_email):
        self.__packager_name = packager_name
        self.__packager_email = packager_email
        self.__gpg_home = gpghome
        self.__repo_dir = repo_dir
        self.__updates = updates
        self.__builder_dict = {
            'repo': self.__build_repo,
            'aur': self.__build_aur,
            'git': self.__build_git
        }
    
    def build(self):
        success, failed, to_remove = [], [], []
        for pkg_type, packages in self.__updates.items():
            logger.info('Building %s packages', pkg_type)
            for package in packages:
                try:
                    self.__builder_dict[pkg_type](package)
                    logger.info('Successfully built %s', package['name'])
                    success.append(package['name'])
                    to_remove.append(package['old-filename'])
                except BuildFailedError as e:
                    logger.error(e)
                    failed.append(package['name'])
        to_remove = list(filter(lambda x: not not x, to_remove))
        return success, failed, to_remove
    
    def __build_repo(self, package):
        downloader = PkgDownloader(self.__repo_dir, package['file-url'], package.get('keyid'), self.__gpg_home)
        downloader.download()
    
    def __build_aur(self, package):
        builder = AURBuilder(self.__packager_name, self.__packager_email, self.__repo_dir, package['name'])
        builder.build()
    
    def __build_git(self, package):
        builder = GitBuilder(self.__packager_name, self.__packager_email, self.__repo_dir, package['git_url'])
        builder.build()
