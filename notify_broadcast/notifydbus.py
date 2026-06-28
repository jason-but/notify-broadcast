"""
This module implements the NotifyDBUS class which manages a list of TTY connections for one or more users and can be used to send notifications
to all TTYs in the list
"""
# Import System Libraries
import os
import psutil
import re
import logging

# Import dasbus library modules
from dasbus.connection import AddressedMessageBus
from dasbus.client.proxy import InterfaceProxy


class NotifyDBUS:
    class DBUSSessionNotFound(Exception):
        """ This exception is raised when we have an error accessing the provided TTY """
        pass

    def __init__(self, user_type: str, log_level: str):
        """
        Initialise class and internal variables

        Initialise empty list of user IDs and corresponding TTYs to send notifications to

        :param user_type: Text description of user type for logging purposes
        :param log_level: Level to set for the internal class logger
        """
        self.__log = logging.getLogger(self.__class__.__name__)
        if log_level is not None:
            self.__log.setLevel(log_level)
        else:
            self.__log.debug('using default log level')

        self.__user_type = user_type
        self.__dbus_list: list[tuple[int, InterfaceProxy]] = []

    def __len__(self):
        """ Return the number of TTYs in the list """
        return len(self.__dbus_list)

    def __str__(self):
        """ Return string representation of class """
        return f'{self.__user_type.capitalize()} DBUS sessions: {self.__dbus_list}'

    def add_session(self, uid: int, process_name: str) -> None:
        """
        Add a DBUS Notification Proxy  for the given user ID running process_name to the internal list

        :param uid: User ID for a given session
        :param process_name: Name of the program to search for

        :return: The DBUS Notification Proxy to send notifications to the user via the attached session
        """
        try:
            # 1) Find the process ID for program "name" owned by self.__uid
            self.__log.debug(f'Searching for process "{process_name}"')
            manager_pid = [p.pid for p in psutil.process_iter(['name', 'pid', 'uids']) if p.info['name'] == process_name and p.info['uids'].real == uid][0]
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
                raise NotifyDBUS.DBUSSessionNotFound(f'No DBUS Session Address found in environment for process ID ({manager_pid})')

            dbus_path = dbus_match.group(1).decode('utf-8')
            self.__log.debug(f'DBUS Session Path: {dbus_path}')

            # 3) Create and return Notifications Proxy for the nominated path
            self.__log.debug(f'Creating Notification Proxy')
            self.__dbus_list.append((uid, AddressedMessageBus(dbus_path).get_proxy("org.freedesktop.Notifications", "/org/freedesktop/Notifications")))

        except IndexError:
            raise NotifyDBUS.DBUSSessionNotFound(f'Unable to locate process "{process_name}"')

        except (IOError, PermissionError):
            raise NotifyDBUS.DBUSSessionNotFound(f'Unable to access environment variables for process ID ({manager_pid}) - Need to run as root or user with appropriate permissions')

    def broadcast_notification(self, app_uid: int, notification: tuple, print_id: bool) -> None:
        """
        Send the provided notification string to all user TTYs stored in the internal list

        :param app_uid: Current effective User ID running application, need to revert to this EUID after sending notification
        :param notification: Tuple containing parameters to pass to the Notify() method of the Notification Proxy
        :param print_id: Boolean indicating whether the message ID should be printed to screen
        """
        if len(self.__dbus_list) == 0:
            self.__log.info(f'No {self.__user_type} users to send notification to')
            return

        self.__log.info(f'Sending notification to {self.__user_type} DBUS users')
        self.__log.debug(f'Notification: {notification}')
        for uid, notify_proxy in self.__dbus_list:
            self.__log.debug(f'Changing UID to {uid} to send notification')
            os.seteuid(uid)

            self.__log.info(f'User({uid}): Sending Notification')
            try:
                notify_id = notify_proxy.Notify(*notification)
                if print_id: print(notify_id)
            except Exception as e:
                self.__log.error(f'Error sending notification to user({uid}): {e}')

            self.__log.debug(f'Reverting UID to {app_uid}')
            os.seteuid(app_uid)
