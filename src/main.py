import logging

from argparse import ArgumentParser
from update_checker import UpdateChecker
from builder import Builder
from signer import Signer
from dbmaker import DBMaker

from utils import logger
logger.setLevel(logging.DEBUG)

def _main_impl(args):
    checker = UpdateChecker(args.database)
    available =  checker.check()
    if not available:
        logger.info('No updates available. Bye bye!')
        return
    logger.debug('Updates available: %s', available)
    
    builder = Builder(available, '.gnupg', 'arepo', 'Ibrahim', 'rafiibrahim8@hotmail.com')
    #success, failed, to_remove = builder.build()
    #logger.info('Successfully built: %s', success)
    #logger.info('Failed to build: %s', failed)
    #logger.info('Files to remove: %s', to_remove)

    Signer('arepo', '.gnupg').sign_all()
    DBMaker('arepo', 'arepo').make_db()


    
def main():
    parser = ArgumentParser()
    parser.add_argument('-d', '--database', help='Path to the database file', required=True)

    _main_impl(parser.parse_args())

if __name__ == '__main__':
    main()
