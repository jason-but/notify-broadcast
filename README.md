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
- colorlog: https://github.com/borntyping/python-colorlog/
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

Some examples of how to use `notify-broadcast` are listed below. These are by no means exhaustive:

`notify-broadcast -a Daily-backup -t 0 -i dialog-information.png "Backup completed without error" ""`

Display a notification that the backup has completed without error:
 - Display an information icon
 - A timeout of 0 signifies that the notification will display until the user clears it
 - Message contains a summary, but no body

`notify-broadcast -a Remote-rsync -t 6000 -i dialog-warning.png "Remote host not currently on the network" ""`

Display a notification that the remote host is not available:
 - Display a warning icon
 - A timeout of 6000 signifies that the notification will display for six seconds before clearing
 - Message contains a summary, but no body

`notify-broadcast -a Daily-backup -t 0 -i dialog-error.png "Error running backup, please consult logs" ""`

Display a notification that the backup has completed without error:
 - Display an error icon
 - A timeout of 0 signifies that the notification will display until the user clears it
 - Message contains a summary, but no body

`notify-broadcast -a "Disk Monitor" -h string:desktop-entry:org.kde.kinfocenter-i drive-harddisk "Disk" "SMART warning"`

Display a notification that a disk has encountered a SMART error:
 - Display an disk icon
 - No timeout signifies that the notification will display for the system default duration

## Comments

I am aware of a number of potential shortcomings that may impact broader distribution, as well as
some points about why things were coded this way, details listed below

### Finding DBUS Path via environment variables instead of `/run/user/{uid}/bus`

The code searches for the `DBUS_SESSION_BUS_ADDRESS` environment variable in a running program,
while many online examples suggest searching `/run/user/{uid}/bus`

My system (Gentoo) does not place the DBUS sockets in that location, so searching the environment
variables allows this to work regardless of the location of the socket.

### Program is hard-coded to KDE

As per the previous point, to search the environment variables, it means finding a running 
application that has the environment variables set. This means that we need to know the application
name to search for.

Hence, the program currently looks for running instances of `kwin_wayland` or `kwin_x11` depending
on the current session type.

This works for me as I use KDE, I don't like Gnome or other environments.

However, I realise this means that this will not work everywhere. Some chat online suggests looking
for `dbus-launch`, however the environment for this process does not appear to contain the
`DBUS_SESSION_BUS_ADDRESS` environment variable.

I would like to support alternate desktops, but I do not have the will to test and develop a
solution. I am happy to take comments/suggestions on how to detect across multiple platforms.

### Some of the Options are Useless for Broadcast application

As a broadcast application, this really makes sense as a 1) send a message; and 2) do not wait for
replies scenario

1. `--print-id` makes no sense if sending multiple notifications
2. `--replace-id` make no sense if we are just blasting information to everyone
3. `--action` display buttons to the user and return values to the program. This is generally useless for this application

### Running as non-root

A non-root user will not be able to post notifications to other users in either case. The 
application currently just prints warnings about being unable to access the environment and 
does nothing else.

It might be better to abort early if the user does not have permissions, but a system could
allow multiple users the requisite permissions, so it is hard to manage this properly.
