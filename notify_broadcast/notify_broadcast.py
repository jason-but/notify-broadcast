"""
This module implements the notify-broadcast application. The application is installed as a script which runs the notify_broadcast()
function contained within this file
"""
# Import System Libraries
import colorlog

# Import Package Modules
from notify_broadcast import NotifyBroadcastArgumentParser
from notify_broadcast import DBUSSessionManager


def notify_broadcast():
    """
    This is the main application
    """
    # Create the command line argument parser and parse all arguments
    parser = NotifyBroadcastArgumentParser()
    parser.parse_args()

    # Set the default logging format
    colorlog.basicConfig(format='%(log_color)s[%(levelname)-8s] %(reset)s%(name)s.%(funcName)s() - %(log_color)s%(message)s%(reset)s',
                         log_colors={'DEBUG': 'cyan', 'INFO': 'green', 'WARNING': 'yellow', 'ERROR': 'red', 'CRITICAL': 'red,bg_white'}
                         )

    # Create the DBUSSessionManager, then broadcast the notification to all users
    dbus_manager = DBUSSessionManager(parser.log_level)
    dbus_manager.broadcast_notification(parser.notification, parser.print_id)