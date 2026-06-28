"""
This module implements the DBUSSessionManager class which finds all user DBUS sessions and maps their NotificationProxy to allow broadcast of
notifications to all users with a DBUS session
"""
# Import System Libraries
import os
import pathlib
import psutil
import re
import logging

# Import dasbus library modules
from dasbus.connection import SystemMessageBus, AddressedMessageBus
from dasbus.client.proxy import InterfaceProxy

from notify_broadcast import NotifyTTY, NotifyDBUS


class SessionManager:
    class DBUSSessionNotFound(Exception):
        """ This exception is raised when we cannot find the DBUS session for the nominated user and session type """
        pass

    def __init__(self, log_level: str):
        """
        Initialise class and internal variables:
          - Store UID of current user so we can change EUID during running
          - Populate __users mapping uid to a DBUS InterfaceProxy that we can use to notify that user

        :param log_level: Level to set for the internal class logger
        """
        self.__log = logging.getLogger(self.__class__.__name__)
        if log_level is not None:
            self.__log.setLevel(log_level)
        else:
            self.__log.debug('using default log level')

        self.__app_uid = os.geteuid()
        self.__log.debug(f'Storing UID of user running application: {self.__app_uid}')

        self.__graphical_users: NotifyDBUS = NotifyDBUS('graphical', log_level)
        self.__local_users: NotifyTTY = NotifyTTY('local', log_level)
        self.__remote_users: NotifyTTY = NotifyTTY('remote', log_level)

    def find_sessions(self):
        """
        Find all users with a login session, locate if they have a DBUS session attached to it, then populate __users with that information
        """
        self.__log.info('Finding login sessions for all users')
        bus = SystemMessageBus()
        login_bus = bus.get_proxy("org.freedesktop.login1", "/org/freedesktop/login1")

        for session_id, uid, username, seat, path in login_bus.ListSessions():
            # Get session details for this login
            session_proxy = bus.get_proxy("org.freedesktop.login1", path)

            match session_proxy.Type:
                case 'wayland' | 'x11':
                    # Graphical session
                    try:
                        self.__log.info(f'Login session {session_id}: User [{username}({uid})] on seat[{seat}] is a {session_proxy.Type} session')
                        self.__graphical_users.add_session(uid, f'kwin_{session_proxy.Type}')
                    except SessionManager.DBUSSessionNotFound as e:
                        self.__log.warning(e)
                case 'tty':
                    # Console session
                    try:
                        tty_path = pathlib.Path('/dev', session_proxy.TTY)
                        self.__log.info(f'{'Remote' if session_proxy.Remote else 'Local'} TTY login session {session_id}: User [{username}({uid})] on TTY({session_proxy.TTY})')
                        if session_proxy.Remote:
                            self.__remote_users.add_session(uid, tty_path)
                        else:
                            self.__local_users.add_session(uid, tty_path)
                    except NotifyTTY.TTYError as e:
                        self.__log.warning(f'{username} - {e}')
                case _:
                    # Unknown session type
                    self.__log.info(f'Non-graphical login session {session_id}: User [{username}({uid})]')
                    self.__log.debug(f'Session Type: {session_proxy.Type}')

        if len(self.__graphical_users) > 0: self.__log.debug(self.__graphical_users)
        if len(self.__local_users) > 0: self.__log.debug(self.__local_users)
        if len(self.__remote_users) > 0: self.__log.debug(self.__remote_users)

    def broadcast_notification(self, notification: tuple, print_id: bool):
        """
        Broadcast a notification to all users using the DBUS Notification Proxies as listed in __users

        :param notification: Tuple containing parameters to pass to the Notify() method of the Notification Proxy
        :param print_id: Boolean indicating whether the message ID should be printed to screen
        """
        self.__log.info(f'Sending notification to all users')

        # Sending DBUS/Graphical Notifications
        self.__graphical_users.broadcast_notification(self.__app_uid, notification, print_id)

        # Sending TTY Notifications
        app_name, _, _, summary, body, _, _, _ = notification
        self.__local_users.broadcast_notification(f'\n\n----------------------------------------\n{summary}{f' (received from {app_name})' if len(app_name) > 0 else ''}\n\n{body}\n----------------------------------------\n\n')
        self.__remote_users.broadcast_notification(f'\n\n----------------------------------------\n{summary}{f' (received from {app_name})' if len(app_name) > 0 else ''}\n\n{body}\n----------------------------------------\n\n')
