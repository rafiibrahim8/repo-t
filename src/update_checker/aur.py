from .git import GitUpdateChecker

class AURUpdateChecker(GitUpdateChecker):
    def __init__(self, package):
        super().__init__(None, f'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h={package}')
