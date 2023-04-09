import logging
import os

from argparse import ArgumentParser
from update_checker import UpdateChecker
from builder import Builder
from signer import Signer
from dbmaker import DBMaker

from utils import logger, get_sys_info
logger.setLevel(logging.DEBUG)

def _main_impl(args):
    repo_name = os.environ.get('REPO_NAME', 'private-arch-repo')
    repo_dir = os.path.expanduser('~/repo')
    if not os.path.exists(repo_dir):
        raise FileNotFoundError(f'Repo directory {repo_dir} does not exist')
    mantainer_name = os.environ['MANTAINER_NAME']
    mantainer_email = os.environ['MANTAINER_EMAIL']

    logger.info('Repo name: %s', repo_name)
    logger.info('Mantainer name: %s', mantainer_name)
    logger.info('Mantainer email: %s', mantainer_email)
    
    checker = UpdateChecker(os.path.join(repo_dir, f'{repo_name}.db'))

    available =  checker.check()
    if not available:
        logger.info('No updates available. Bye bye!')
        return
    logger.debug('Updates available: %s', available)
    
    builder = Builder(available, repo_dir, mantainer_name, mantainer_email)
    success, failed, to_remove = builder.build()
    logger.info('Successfully built: %s', success)
    logger.info('Failed to build: %s', failed)
    logger.info('Files to remove: %s', to_remove)
    
    Signer(repo_dir).sign_all()
    DBMaker(repo_dir, repo_name, to_remove).make_db()

    for file in to_remove:
        if os.path.exists(os.path.join(repo_dir, file)):
            os.remove(os.path.join(repo_dir, file))
    
def main():
    parser = ArgumentParser()
    # Will be implemented later

    logger.info('System info: %s', get_sys_info())
    _main_impl(parser.parse_args())

if __name__ == '__main__':
    main()
