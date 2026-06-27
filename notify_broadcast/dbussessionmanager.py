"""
This module implements the DBUSSessionManager class which finds all user DBUS sessions and maps their NotificationProxy to allow broadcast of
notifications to all users with a DBUS session
"""
# Import System Libraries
import os
import psutil
import re
import logging

# Import dasbus library modules
from dasbus.connection import SystemMessageBus, AddressedMessageBus
from dasbus.client.proxy import InterfaceProxy


class DBUSSessionManager:
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
        self.__log = logging.getLogger('DBUSSessionManager')
        if log_level is not None:
            self.__log.setLevel(log_level)
        else:
            self.__log.debug('using default log level')
        self.__log.info(f'Constructing Class')

        self.__app_uid = os.geteuid()
        self.__log.debug(f'Storing UID of user running application: {self.__app_uid}')

        self.__users: dict[int, InterfaceProxy] = {}
        self.__find_users()
        self.__log.debug(f'User DBUS sessions: {self.__users}')

    def __get_notify_proxy(self, uid: int, name: str) -> InterfaceProxy:
        """
        Return a DBUS Notification Proxy for the given user, running the graphical session from the provided process name

        :param uid: User ID for a given session
        :param name: Name of the program to search for

        :return: The DBUS Notification Proxy to send notifications to the user via the attached session
        """
        try:
            # 1) Find the process ID for program "name" owned by self.__uid
            self.__log.debug(f'Searching for process "{name}"')
            manager_pid = [p.pid for p in psutil.process_iter(['name', 'pid', 'uids']) if p.info['name'] == name and p.info['uids'].real == uid][0]
            self.__log.debug(f'Found Process ID: {manager_pid}')

            # 2) Search the environment for manager_pid, and extract the DBUS session address
            self.__log.debug('Reading Process environment')
            with open(f'/proc/{manager_pid}/environ', 'rb') as f:
                env_bytes = f.read()

            # Regex pattern to locate DBUS addresses inside environment blocks
            self.__log.debug('Searching for DBUS Session Bus Address')
            dbus_pattern = re.compile(b"DBUS_SESSION_BUS_ADDRESS=(unix:path=[^\\x00]+)")
            dbus_match = dbus_pattern.search(env_bytes)

            if not dbus_match:
                raise DBUSSessionManager.DBUSSessionNotFound(f'No DBUS Session Address found in environment for process ID ({manager_pid})')

            dbus_path = dbus_match.group(1).decode('utf-8')
            self.__log.debug(f'DBUS Session Path: {dbus_path}')

            # 3) Create and return Notifications Proxy for the nominated path
            self.__log.debug(f'Creating Notification Proxy')
            return AddressedMessageBus(dbus_path).get_proxy("org.freedesktop.Notifications", "/org/freedesktop/Notifications")

        except IndexError:
            raise DBUSSessionManager.DBUSSessionNotFound(f'Unable to locate process "{name}"')

        except (IOError, PermissionError):
            raise DBUSSessionManager.DBUSSessionNotFound(f'Unable to access environment variables for process ID ({manager_pid}) - Need to run as root or user with appropriate permissions')

    def __find_users(self):
        """
        Find all users with a login session, locate if they have a DBUS session attached to it, then populate __users with that information
        """
        self.__log.info('Finding DBUS sessions for all users')
        bus = SystemMessageBus()
        login_bus = bus.get_proxy("org.freedesktop.login1", "/org/freedesktop/login1")

        for session_id, uid, username, seat, path in login_bus.ListSessions():
            # Get session details for this login
            session_proxy = bus.get_proxy("org.freedesktop.login1", path)
            if session_proxy.Type in ['wayland', 'x11']:
                try:
                    self.__log.info(f'Login session {session_id}: User [{username}({uid})] on seat[{seat}] is a {session_proxy.Type} session')
                    self.__users[uid] = self.__get_notify_proxy(uid, f'kwin_{session_proxy.Type}')
                except DBUSSessionManager.DBUSSessionNotFound as e:
                    self.__log.warning(e)
            else:
                self.__log.info(f'Non-graphical login session {session_id}: User [{username}({uid})]')

    def broadcast_notification(self, notification: tuple, print_id: bool):
        """
        Broadcast a notification to all users using the DBUS Notification Proxies as listed in __users

        :param notification: Tuple containing parameters to pass to the Notify() method of the Notification Proxy
        :param print_id: Boolean indicating whether the message ID should be printed to screen
        """
        self.__log.info(f'Sending notification ({notification}) to all users')
        for uid, notify_proxy in self.__users.items():
            self.__log.debug(f'Changing UID to {uid} to send notification')
            os.seteuid(uid)

            self.__log.info(f'User({uid}): Sending Notification')
            notify_id = notify_proxy.Notify(*notification)
            if print_id: print(notify_id)

            self.__log.debug(f'Reverting UID to {self.__app_uid}')
            os.seteuid(self.__app_uid)
