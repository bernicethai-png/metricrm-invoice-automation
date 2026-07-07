#!/usr/bin/env osascript

set scriptPath to (path to home folder as text) & "Claude:Projects:MetriCRM Auto Invoice:install_auto_invoice.sh"
set shellScript to "bash " & quoted form of POSIX path of scriptPath

tell application "Terminal"
    activate
    do script shellScript
end tell
