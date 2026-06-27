"""
This module implements the NotifyBroadcastArgumentParser class which provides the command-line argument parser for the notify-broadcast command
"""
# Import System Libraries
import argparse
import logging
from gi.repository import GLib


class NotifyBroadcastArgumentParser(argparse.ArgumentParser):
    """
    Extends ArgumentParser to provide parameter parsing for the notify-broadcast command.

    Installs arguments similar to notify-send
    """
    class NotifyHints(argparse.Action):
        """
        Process one or more command line options in form TYPE:NAME:VALUE and appends a dictionary value mapping NAME -> VALUE cast to the
        specified TYPE

        NOTE: This class is designed to be used for validating a formatted parameter in the context of command-line argument parsing.
        When an instance of this class is called with a string, it checks if the string conforms to the appropriate format specification.
        If the provided string is in error, it raises an error suitable for argument parsing utilities.
        """
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            """Initialise argument to empty dictionary"""
            kwargs.setdefault('default', {})
            super().__init__(option_strings, dest, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            """
            Parse command line option as TYPE:NAME:VALUE and append to dictionary mapping name-->value(cast to type)

            :param parser: ArgParse instance, used to send errors back to the parser.
            :param namespace: Current parsed parameters.
            :param values: Current option being parsed.
            :param option_string: Actual option (e.g. --hint)
            """
            # Get the pre-existing parameter dictionary
            current_values = getattr(namespace, self.dest)

            # Split parameter to TYPE:NAME:VALUE tuple and add to dictionary
            try:
                parts = values.split(':', 2)
                if len(parts) != 3: raise ValueError(f'Parameter should contain three values in format TYPE:NAME:VALUE, only {len(parts)} values provided')

                raw_type, name, raw_value = parts

                match raw_type.lower():
                    case'int':
                        variant_val = GLib.Variant('i', int(raw_value))
                    case 'double':
                        variant_val = GLib.Variant('d', float(raw_value))
                    case 'boolean' | 'bool':
                        variant_val = GLib.Variant('b', raw_value.lower() in ('true', '1', 'yes'))
                    case 'byte':
                        variant_val = GLib.Variant('y', int(raw_value))
                    case _:  # Default to string
                        variant_val = GLib.Variant('s', str(raw_value))

                current_values[name] = variant_val

            except ValueError as e:
                parser.error(f'Invalid parameter "{option_string} {values}" is invalid: {e}')

            # Save dictionary back to namespace
            setattr(namespace, self.dest, current_values)

    class NotifyUrgency(argparse.Action):
        """
        Process command line options as human-readable "urgency" values and map directly into hints directory as corresponding byte values
        under the name "urgency"

        NOTE: String values should be checked by argparse, so no errors should be raised here, merely convert string->byte and append to
        dictionary
        """
        def __init__(self, option_strings, dest, **kwargs):
            """Initialise argument to empty dictionary"""
            kwargs.setdefault('default', {})
            super().__init__(option_strings, dest, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            """
            Parse command line option as low, normal, or critical, and append to dictionary with corresponding byte value under key name 'urgency'

            :param parser: ArgParse instance, used to send errors back to the parser.
            :param namespace: Current parsed parameters.
            :param values: Current option being parsed.
            :param option_string: Actual option (e.g. --urgency)
            """
            # Get the pre-existing parameter dictionary
            current_values = getattr(namespace, self.dest)

            urgency_mapping = {'low': 0, 'normal': 1, 'critical': 2}

            # Inject the key directly into the dictionary as a D-Bus byte variant
            current_values['urgency'] = GLib.Variant('y', urgency_mapping[values])

            # Save dictionary back to namespace
            setattr(namespace, self.dest, current_values)

    class NotifyCategory(argparse.Action):
        """
        Process command line options as string "category" value and map directly into hints directory as corresponding string under the
        name "category"

        NOTE: String value provided already, so no errors should be raised here, merely append string to dictionary
        """
        def __init__(self, option_strings, dest, **kwargs):
            """Initialise argument to empty dictionary"""
            kwargs.setdefault('default', {})
            super().__init__(option_strings, dest, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            """
            Parse command line option as string, and append to dictionary with corresponding string value under key name 'category'

            :param parser: ArgParse instance, used to send errors back to the parser.
            :param namespace: Current parsed parameters.
            :param values: Current option being parsed.
            :param option_string: Actual option (e.g. --option)
            """
            # Get the pre-existing parameter dictionary
            current_values = getattr(namespace, self.dest)

            # Inject the key directly into the dictionary as a D-Bus string variant
            current_values['category'] = GLib.Variant('s', str(values))

            # Save dictionary back to namespace
            setattr(namespace, self.dest, current_values)

    class NotifyTransient(argparse.Action):
        """
        Process command line flag to activate transient feature. Map directory into hints dictionary as "transient"->True

        NOTE: Simple parameter flag, so no errors should be raised here, merely append True to dictionary
        """
        def __init__(self, option_strings, dest, **kwargs):
            """Initialise argument to empty dictionary"""
            kwargs.setdefault('default', {})
            super().__init__(option_strings, dest, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            """
            Transient should be a flag on the command line, so this action is called to set flag to True. Append True value to dictionary
            under key name 'transient'

            :param parser: ArgParse instance, used to send errors back to the parser.
            :param namespace: Current parsed parameters.
            :param values: Current option being parsed.
            :param option_string: Actual option (e.g. --option)
            """
            # Get the pre-existing parameter dictionary
            current_values = getattr(namespace, self.dest)

            # Inject the key directly into the dictionary as a D-Bus byte variant
            current_values['transient'] = GLib.Variant('b', True)

            # Save dictionary back to namespace
            setattr(namespace, self.dest, current_values)

    class NotifyAction(argparse.Action):
        """
        Process one or more command line options in form KEY=LABEL or KEY:LABEL and append them to a flat "actions" list

        NOTE: This class is designed to be used for validating a formatted parameter in the context of command-line argument parsing.
        When an instance of this class is called with a string, it checks if the string conforms to the appropriate format specification.
        If the provided string is in error, it raises an error suitable for argument parsing utilities.
        """
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            """Initialise argument to empty list"""
            kwargs.setdefault('default', [])
            super().__init__(option_strings, dest, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            """
            Parse command line option as KEY=LABEL or KEY:LABEL and extend the existing list with two new entries [KEY, LABEL]

            :param parser: ArgParse instance, used to send errors back to the parser.
            :param namespace: Current parsed parameters.
            :param values: Current option being parsed.
            :param option_string: Actual option (e.g. --hint)
            """
            # Get the pre-existing parameter list
            actions_list = getattr(namespace, self.dest)

            # Allow splitting by either ':' or ',' to match common notify-send clones
            delimiter = '=' if '=' in values else ':'

            try:
                parts = values.split(delimiter, 1)
                if len(parts) != 2: raise ValueError(f'Must be in "KEY=LABEL" or "KEY:LABEL" format')

                key, label = parts[0].strip(), parts[1].strip()
                if not key: raise ValueError('Key cannot be an empty string')
                if not label: raise ValueError('Label cannot be an empty string')

                # D-Bus expects a flat list: [key1, label1, key2, label2]
                actions_list.extend([key, label])

            except Exception as e:
                parser.error(f'Invalid parameter "{option_string} {values}" is invalid: {e}')

            # Save dictionary back to namespace
            setattr(namespace, self.dest, actions_list)

    class SetGlobalLogLevel(argparse.Action):
        """
        Process the global-log-level parameter and set the default system log level as an action

        NOTE: This class is designed to be used for validating a formatted parameter in the context of command-line argument parsing.
        When an instance of this class is called with a string, it checks if the string conforms to the appropriate format specification.
        If the provided string is in error, it raises an error suitable for argument parsing utilities.
        """
        def __call__(self, parser, namespace, values, option_string=None):
            """
            Parse command line option as DEBUG, INFO, WARNING, ERROR, or CRITICAL, then set the logging log-level to match

            :param parser: ArgParse instance, used to send errors back to the parser.
            :param namespace: Current parsed parameters.
            :param values: Current option being parsed.
            :param option_string: Actual option (e.g. --urgency)
            """
            logging.basicConfig(level=values)

            # Save the value to the namespace for standard argparse behavior
            setattr(namespace, self.dest, values)

    # NotifyBroadcastArgumentParser member methods begin here
    def __init__(self, *args, **kwargs):
        """
        Overloaded Constructor

        Set default description and argparse parameters before calling superclass constructor

        Then call add_arguments() to add the required command-line parameters
        """
        # Default options
        kwargs.setdefault('description', 'Notify Broadcast\n\nSend a Broadcast DBUS notification to all users')
        kwargs.setdefault('formatter_class', argparse.ArgumentDefaultsHelpFormatter)
        kwargs.setdefault('allow_abbrev', False)
        kwargs.setdefault('conflict_handler', 'resolve')

        # Initialise the parent class
        super().__init__(*args, **kwargs)

        # Add parameter options
        self.__add_arguments()

        # Create variable to store generated notification from parsed arguments
        self.__notification = None
        self.__print_id = None
        self.__log_level = None

    def __add_arguments(self):
        """ Add command line arguments to the argument parser """
        self.add_argument('-a', '--app-name', type=str, default='', help='Specifies the app name for the notification')
        self.add_argument('-i', '--icon', type=str, default='dialog-information', help='Specifies an icon filename or stock icon to display.')
        self.add_argument('-t', '--expire-time', type=int, default=-1, help='The duration, in milliseconds, for the notification to appear on screen. Value of 0 means no expiry, while -1 uses the server default expiry.')
        self.add_argument('-h', '--hint', action=NotifyBroadcastArgumentParser.NotifyHints, metavar='TYPE:NAME:VALUE', help='Notification hints to pass to server (e.g., int:urgency:2)')
        self.add_argument('-c', '--category', action=NotifyBroadcastArgumentParser.NotifyCategory, metavar='TYPE', dest='hint', help='Specifies the notification category.')
        self.add_argument('-u', '--urgency', action=NotifyBroadcastArgumentParser.NotifyUrgency, choices=['low', 'normal', 'critical'], dest='hint', help='Specifies the urgency level (low, normal, critical).')

        self.add_argument('-A', '--action', action=NotifyBroadcastArgumentParser.NotifyAction, metavar='NAME=VALUE', help='Specifies the actions to display to the user. Implies --wait to wait for user input. May be set multiple times. The NAME of the action is output to stdout. If NAME is not specified, the numerical index of the option is used (starting with 1).')

        self.add_argument('-r', '--replace-id', type=int, default=0, help='The ID of the notification to replace.')
        self.add_argument('-p', '--print-id', action='store_true', help='Print the notification ID.')

        self.add_argument('-e', '--transient', action=NotifyBroadcastArgumentParser.NotifyTransient, dest='hint', help='Show a transient notification. Transient notifications by-pass the server\'s persistence capability, if any. And so it won\'t be preserved until the user acknowledges it.')

        self.add_argument('summary', type=str, help='exam configuration file to be used for student collection - toml format')
        self.add_argument('body', type=str, help='exam solution file to be placed in collection directory')

        self.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level for the core application.")

        self.add_argument("--global-log-level", action=NotifyBroadcastArgumentParser.SetGlobalLogLevel, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the global logging level (includes third-party libraries).")

    def parse_args(self, args=None, namespace=None):
        """
        Overload parse_args method. Constructs the notification details (stored in __notification) from the parsed command line arguments.
          - Call the base class method to parse the arguments and store in temporary variable
          - Extract parameters into a tuple (ready to pass to Notify()) and store in __notification
          - Extract other variables to make directly accessible via properties

        :return: Return the parsed arguments Namespace as required by parse_args()
        """
        # Call base class method to parse arguments and store in internal variable
        parsed = super().parse_args(args=args, namespace=namespace)

        self.__notification = (parsed.app_name, parsed.replace_id, parsed.icon, parsed.summary, parsed.body, parsed.action, parsed.hint, parsed.expire_time)
        self.__print_id = parsed.print_id
        self.__log_level = parsed.log_level

        return parsed

    @property
    def notification(self) -> tuple:
        """
        Retrieves the notification constructed from the command line arguments as a class property.

        :return: The value stored in internal variable __notification
        """
        return self.__notification

    @property
    def print_id(self) -> bool:
        """
        Retrieves the print_id from the command line arguments as a class property.

        :return: The value stored in internal variable __print_id
        """
        return self.__print_id

    @property
    def log_level(self) -> str:
        """
        Retrieves the log_level from the command line arguments as a class property.

        :return: The value stored in internal variable __log_level
        """
        return self.__log_level

