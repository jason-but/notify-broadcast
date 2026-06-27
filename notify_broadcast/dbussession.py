import os
import re
import logging
import psutil
from dasbus.client.proxy import InterfaceProxy
from dasbus.connection import AddressedMessageBus


class DBUSSession:
    """
    Locates the DBUS session for the nominated user and manages sending notifications to the user via the attached session
    """

    class SessionNotFound(Exception):
        """ This exception is raised when we cannot find the DBUS session for the nominated user and session type """
        pass

    def __init__(self, uid: int, username: str, session_type: str, log_level: str):
        """
        Class constructor to manage the DBUS session

        :param uid: User ID for a given session
        :param username: Username mapping to the session
        :param session_type: Process name that is running the graphical session
        :param log_level: Logging Level to use for class logger
        """
        self.__log = logging.getLogger('DBUSSession')
        self.__log.setLevel(log_level)
        self.__username = username
        self.__uid = uid

        # Store the current user UID, if root we need to change user then revert back again
        self.__app_uid = os.geteuid()

        self.__log.info(f'Constructing DBUSSession Class for user({username}), session_type({session_type})')

        self.__notify_bus = self.__get_notify_bus(f'kwin_{session_type}')

    def __get_notify_bus(self, name: str) -> InterfaceProxy:
        """
        Return a DBUS Notification Proxy using the DBUS_SESSION_BUS_ADDRESS from the environment of process with process ID pid

        :param name: Name of the program to search for
        """
        try:
            # 1) Find the process ID for program "name" owned by self.__uid
            self.__log.debug(f'Searching for process "{name}"')
            manager_pid = [p.pid for p in psutil.process_iter(['name', 'pid', 'username']) if p.info['name'] == name and p.info['uids'] == self.__uid][0]
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
                raise DBUSSession.SessionNotFound(f'No DBUS Session Address found in environment for process ID ({manager_pid})')

            dbus_path = dbus_match.group(1).decode('utf-8')
            self.__log.debug(f'DBUS Session Path: {dbus_path}')

            # 3) Create and return Notifications Proxy for the nominated path
            self.__log.debug(f'Creating Notification Proxy')
            return AddressedMessageBus(dbus_path).get_proxy("org.freedesktop.Notifications", "/org/freedesktop/Notifications")

        except IndexError:
            raise DBUSSession.SessionNotFound(f'Unable to locate process "{name}"')

        except (IOError, PermissionError):
            raise DBUSSession.SessionNotFound(f'Unable to access environment variables for process ID ({manager_pid})')

    def Notify(self, app_name: str, replaces_id: int, app_icon: str, summary: str, body: str, actions: list, hints: dict, expire_timeout: int, print_id: bool):
        """Broadcasts a notification to all discovered active desktop sessions."""
        self.__log.info(f'Sending notification from App({app_name}) with Title({summary}) to all {self.__username}')

        match self.__app_uid:
            case 0:
                self.__log.debug(f'Root user: Changing UID to {self.__uid} to send notification')
                os.seteuid(self.__uid)
            case self.__uid:
                self.__log.debug(f'Running as UID, sending notification OK')
            case _:
                self.__log.error(f'Current UID ({os.getuid()}) is NOT root and does not match BDUS session user ({self.__uid}), aborting notification')
                return

        self.__log.info(f'Sending Notification to {self.__username}({self.__uid})')
        notify_id = self.__notify_bus.Notify(app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout)
        if print_id: print(notify_id)

        if self.__app_uid == self.__uid: return

        self.__log.debug(f'Reverting UID to {self.__app_uid}')
        os.seteuid(self.__app_uid)
