# 0.0.4 (2026-06-28)

## New Features

 - Support for sending Notifications to TTY-based login sessions, both local and remote(ssh)
 - Selectable TTY Notifications via CLI parameters
   - `-L`: Send notification to all local login sessions
   - `-R`: Send notification to all remote(ssh) sessions
 
## Bug Fixes

None

## Code changes

 - Restructure of internal class names to support multiple session types
 - Extraction of single-session code into separate classes

# 0.0.3 (2026-06-28)

## Original Release

### Features
 
 - Send DBUS notification to all DBUS Sessions as root
 - CLI parameters similar to `send-notify`
 - Logging included