# notify-broadcast

This program was developed because I run a number of **cron** jobs as root that I would like to be
able to send notifications to the GUI User

`notify-send` only functions if run by the same user running the graphical session.

I created `notify-broadcast` to effectively tack the same parameters as `notify-send` but that
could be executed by the `root` user.

The application searches for all active DBUS Notification sessions, and sends the notification to
all currently attached users.

## Installation

When complete, should be:

```console
pip install notify-broadcast
```

Seek information elsewhere about installing in a virtual environment

The install should pull in all dependencies. At present these are:
- dasbus: https://github.com/dasbus-project/dasbus
- psutil: https://github.com/giampaolo/psutil
- PyGObject: https://pygobject.gnome.org

## Usage

```console
# notify-broadcast --help
usage: notify-broadcast [--help] [-a APP_NAME] [-i ICON] [-t EXPIRE_TIME] [-h TYPE:NAME:VALUE] [-c TYPE] [-u {low,normal,critical}] [-A NAME=VALUE] [-r REPLACE_ID] [-p] [-e HINT] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        [--global-log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        summary body

Notify Broadcast Send a Broadcast DBUS notification to all users

positional arguments:
  summary               exam configuration file to be used for student collection - toml format
  body                  exam solution file to be placed in collection directory

options:
  --help                show this help message and exit
  -a APP_NAME, --app-name APP_NAME
                        Specifies the app name for the notification (default: )
  -i ICON, --icon ICON  Specifies an icon filename or stock icon to display. (default: dialog-information)
  -t EXPIRE_TIME, --expire-time EXPIRE_TIME
                        The duration, in milliseconds, for the notification to appear on screen. Value of 0 means no expiry, while -1 uses the server default expiry. (default: -1)
  -h TYPE:NAME:VALUE, --hint TYPE:NAME:VALUE
                        Notification hints to pass to server (e.g., int:urgency:2) (default: {})
  -c TYPE, --category TYPE
                        Specifies the notification category. (default: {})
  -u {low,normal,critical}, --urgency {low,normal,critical}
                        Specifies the urgency level (low, normal, critical). (default: {})
  -A NAME=VALUE, --action NAME=VALUE
                        Specifies the actions to display to the user. Implies --wait to wait for user input. May be set multiple times. The NAME of the action is output to stdout. If NAME is not specified, the numerical index of the
                        option is used (starting with 1). (default: [])
  -r REPLACE_ID, --replace-id REPLACE_ID
                        The ID of the notification to replace. (default: 0)
  -p, --print-id        Print the notification ID. (default: False)
  -e HINT, --transient HINT
                        Show a transient notification. Transient notifications by-pass the server's persistence capability, if any. And so it won't be preserved until the user acknowledges it. (default: {})
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level for the core application. (default: None)
  --global-log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the global logging level (includes third-party libraries). (default: None)
```

**NOTE:** For more support on these parameters, see `notify-send` man pages

## Examples

## Comments

