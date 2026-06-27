"""
This module implements the DBUSSessionManager class which finds all user DBUS sessions and maps their NotificationProxy to allow broadcast of
notifications to all users with a DBUS session
"""
# Import System Libraries
import logging

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
    logging.basicConfig(format='%(asctime)s - %(levelname)-8s %(name)s.%(funcName)s() - %(message)s')

    # Create the DBUSSessionManager, then broadcast the notification to all users
    dbus_manager = DBUSSessionManager(parser.log_level)
    dbus_manager.broadcast_notification(parser.notification, parser.print_id)