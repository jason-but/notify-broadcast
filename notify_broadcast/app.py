from notify_broadcast import NotifyBroadcastArgumentParser
from notify_broadcast import DBUSSessionManager

import argparse
import logging

def notify_broadcast():
    """

    :return:
    """
    print('Notifying broadcast...')
    foo = NotifyBroadcastArgumentParser()

    x = foo.parse_args()
    logging.basicConfig(format='%(asctime)s - %(levelname)-8s %(name)s.%(funcName)s() - %(message)s')

    print(foo.notification)

    bar = DBUSSessionManager(x.log_level)

    bar.Notify(foo.notification, x.print_id)