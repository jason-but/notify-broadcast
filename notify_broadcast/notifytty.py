"""
This module implements the NotifyTTY class which manages a list of TTY connections for one or more users and can be used to send notifications
to all TTYs in the list
"""
# Import System Libraries
import pathlib
import logging


class NotifyTTY:
    class TTYError(Exception):
        """ This exception is raised when we have an error accessing the provided TTY """
        pass

    def __init__(self, user_type: str, log_level: str):
        """
        Initialise class and internal variables

        Initialise empty list of user IDs and corresponding TTYs to send notifications to

        :param user_type: Text description of user type for logging purposes
        :param log_level: Level to set for the internal class logger
        """
        self.__log = logging.getLogger('NotifyTTY')
        if log_level is not None:
            self.__log.setLevel(log_level)
        else:
            self.__log.debug('using default log level')
        self.__log.info(f'Constructing Class')

        self.__user_type = user_type
        self.__tty_list: list[tuple[int, pathlib.Path]] = []

    def __len__(self):
        """ Return the number of TTYs in the list """
        return len(self.__tty_list)

    def __str__(self):
        """ Return string representation of class """
        return f'{self.__user_type.capitalize()} TTY sessions: {self.__tty_list}'

    def add_tty(self, uid: int, tty_path: pathlib.Path) -> None:
        """
        Add the provided user ID and TTY to the internal list

        :param uid: Integer representing the user ID
        :param tty_path: pathlib.Path representing the TTY to send a message to this user

        :raise TTYError: Raised if provided TTY Path is invalid or cannot be written to
        """
        try:
            self.__log.debug(f'Validating TTY Path: {tty_path}')
            with open(tty_path, 'w'):
                pass
            self.__log.debug(f'Storing TTY Path ({tty_path}) for user {uid}')
            self.__tty_list.append((uid, tty_path))

        except Exception as e:
            raise NotifyTTY.TTYError(f'Error confirming TTY Path({tty_path}) for user({uid}): {e}')

    def broadcast_notification(self, notification: str) -> None:
        """
        Send the provided notification string to all user TTYs stored in the internal list

        :param notification: String to display on each TTY
        """
        if len(self.__tty_list) == 0:
            self.__log.info(f'No {self.__user_type} users to send notification to')
            return

        self.__log.info(f'Sending notification to {self.__user_type} users')
        self.__log.debug(f'Notification text: {notification!r}')
        for uid, tty_path in self.__tty_list:
            self.__log.info(f'Sending Notification: {self.__user_type} User({uid}) on TTY({tty_path})')
            try:
                with open(tty_path, 'w') as f:
                    f.write(notification)
            except Exception as e:
                self.__log.error(f'Error sending notification to user({uid}) on TTY Path({tty_path}): {e}')
