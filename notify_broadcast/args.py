# Import System Libraries
import argparse
from gi.repository import GLib


# PRIVATE ARGPARSE ACTION CLASSES INTERNAL TO MODULE
class NotifyBroadcastArgumentParser(argparse.ArgumentParser):
    """
    Extends ArgumentParser to provide parameter parsing for the notify-broadcast command.

    Allowed arguments:
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

    def __init__(selfself, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        # Initialise the parent class
        super().__init__(*args, **kwargs)

        # Add parameter options

    def add_arguments(self):
        """

        :return:
        """
        # Create the main parser with global CLI parameters
 #       parser = argparse.ArgumentParser(description='Notify Broadcast\n\nSend a Broadcast DBUS notification to all users',
  #                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter,
   #                                      allow_abbrev=False,
    #                                     )
        self.add_argument('-a', '--app-name', type=str, default='', help='Specifies the app name for the notification')
        self.add_argument('-i', '--icon', type=str, default='dialog-information', help='Specifies an icon filename or stock icon to display.')
        self.add_argument('-t', '--expire-time', type=int, default=-1, help='The duration, in milliseconds, for the notification to appear on screen. Value of 0 means no expiry, while -1 uses the server default expiry.')
        self.add_argument('--hint', action=NotifyBroadcastArgumentParser.NotifyHints, metavar='TYPE:NAME:VALUE', help='Notification hints to pass to server (e.g., int:urgency:2)')
        self.add_argument('-c', '--category', action=NotifyBroadcastArgumentParser.NotifyCategory, metavar='TYPE', dest='hint', help='Specifies the notification category.')
        self.add_argument('-u', '--urgency', action=NotifyBroadcastArgumentParser.NotifyUrgency, choices=['low', 'normal', 'critical'], dest='hint', help='Specifies the urgency level (low, normal, critical).')

        self.add_argument('-A', '--action', action=NotifyBroadcastArgumentParser.NotifyAction, metavar='NAME=VALUE', help='Specifies the actions to display to the user. Implies --wait to wait for user input. May be set multiple times. The NAME of the action is output to stdout. If NAME is not specified, the numerical index of the option is used (starting with 1).')

        self.add_argument('-r', '--replace-id', type=int, default=0, help='The ID of the notification to replace.')
        self.add_argument('-p', '--print-id', action='store_true', help='Print the notification ID.')

        self.add_argument('-e', '--transient', action=NotifyBroadcastArgumentParser.NotifyTransient, dest='hint', help='Show a transient notification. Transient notifications by-pass the server\'s persistence capability, if any. And so it won\'t be preserved until the user acknowledges it.')

        self.add_argument('summary', type=str, help='exam configuration file to be used for student collection - toml format')
        self.add_argument('body', type=str, help='exam solution file to be placed in collection directory')

        self.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="WARNING", help="Set the logging level for the core application.")

        self.add_argument("--global-log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="WARNING", help="Set the global logging level (includes third-party libraries).")

#        return parser.parse_args()
