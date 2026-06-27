from notify_broadcast import NotifyBroadcastArgumentParser

import argparse
import logging

def notify_broadcast():
    """

    :return:
    """
    print('Notifying broadcast...')
    foo = NotifyBroadcastArgumentParser()

    a = foo.parse_args()

    logging.info('info')
    logging.warn('warn')
    logging.error('err')
    logging.critical('critical')
    logging.debug('debug')
    print(a)