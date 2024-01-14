import subprocess
import socket
import urllib.parse

def run_applescript(script):
    osa_command = ['osascript', '-e', script]
    return subprocess.run(osa_command, capture_output=True, text=True).stdout

def send_message(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 65500))
        s.sendall(message.encode('utf-8'))

# AppleScript for selecting Edit window and adjusting track height
script1 = '''
tell application "Pro Tools"
    activate
end tell
delay 1
tell application "System Events"
    tell process "Pro Tools"
        -- Select Edit window from Window menu
        click menu item "Edit" of menu "Window" of menu bar 1
        delay 0.5
        keystroke "a" using {command down} -- Select all tracks in Edit window
        delay 0.5
        -- Repeat "Control + Option + Down Arrow" six times, with a delay after each
        repeat 6 times
            keystroke (ASCII character 31) using {control down, option down}
            delay 0.5
        end repeat
        -- Repeat "Control + Option + Up Arrow" twice, with a delay after each
        repeat 2 times
            keystroke (ASCII character 30) using {control down, option down}
            delay 0.5
        end repeat
    end tell
end tell
'''
print(run_applescript(script1))

# AppleScript for turning off 'No Scrolling' option
script2 = '''
tell application "Pro Tools"
    activate
end tell
delay 1
tell application "System Events"
    tell process "Pro Tools"
        -- Open the "Options" menu
        tell menu bar item "Options" of menu bar 1
            click
            delay 0.5
            -- Open the "Edit Window Scrolling" submenu
            tell menu item "Edit Window Scrolling" of menu 1
                click
                delay 0.5
                -- Select "No Scrolling"
                tell menu item "No Scrolling" of menu 1
                    click
                end tell
            end tell
        end tell
    end tell
end tell
'''
print(run_applescript(script2))

# AppleScript for turning off 'Clip Gain Line'
script3 = '''
tell application "Pro Tools"
    activate
end tell
delay 1
tell application "System Events"
    tell process "Pro Tools"
        -- Open the "View" menu
        tell menu bar item "View" of menu bar 1
            click
            delay 0.5
            -- Open the "Clip" submenu
            tell menu item "Clip" of menu 1
                click
                delay 0.5
                -- Open the "Clip Gain Line" submenu and ensure it's unchecked
                tell menu item "Clip Gain Line" of menu 1
                    if (value of attribute "AXMenuItemMarkChar" is "✓") then
                        click
                    end if
                end tell
            end tell
        end tell
    end tell
end tell
'''
print(run_applescript(script3))

# AppleScript for turning on 'Clip Name'
script4 = '''
tell application "Pro Tools"
    activate
end tell
delay 1
tell application "System Events"
    tell process "Pro Tools"
        -- Open the "View" menu
        tell menu bar item "View" of menu bar 1
            click
            delay 1
            -- Open the "Clip" submenu
            tell menu item "Clip" of menu 1
                click
                delay 1
                -- Open the "Name" submenu and ensure it's checked
                tell menu item "Name" of menu 1
                    if (value of attribute "AXMenuItemMarkChar" is not "✓") then
                        click
                    end if
                end tell
            end tell
        end tell
    end tell
end tell
'''
print(run_applescript(script4))

# AppleScript for turning off 'Clip Effects'
script5 = '''
tell application "Pro Tools"
    activate
end tell
delay 1
tell application "System Events"
    tell process "Pro Tools"
        -- Open the "View" menu
        tell menu bar item "View" of menu bar 1
            click
            delay 0.5
            -- Open the "Other Displays" submenu
            tell menu item "Other Displays" of menu 1
                click
                delay 0.5
                -- Open the "Clip Effects" submenu and ensure it's unchecked
                tell menu item "Clip Effects" of menu 1
                    if (value of attribute "AXMenuItemMarkChar" is "✓") then
                        click
                    end if
                end tell
            end tell
        end tell
    end tell
end tell
'''
print(run_applescript(script5))

# AppleScript for turning off 'Insertion Follows Playback' option
script6 = '''
tell application "Pro Tools"
    activate
end tell
delay 1
tell application "System Events"
    tell process "Pro Tools"
        -- Open the "Options" menu
        tell menu bar item "Options" of menu bar 1
            click
            delay 0.5
            -- Open the "Insertion Follows Playback" submenu and ensure it's unchecked
            tell menu item "Insertion Follows Playback" of menu 1
                if (value of attribute "AXMenuItemMarkChar" is "✓") then
                    click
                end if
            end tell
        end tell
    end tell
end tell
'''
print(run_applescript(script6))

# AppleScript for opening the Workspace window and selecting all items
script7 = '''
tell application "Pro Tools"
    activate
end tell
delay 1
tell application "System Events"
    tell process "Pro Tools"
        -- Press option + O to open the Workspace window
        keystroke "o" using option down
        delay 1
        -- Press right on the arrow pad
        key code 124
        delay 3
        -- Select all (cmd A)
        keystroke "a" using command down
        -- Your additional steps here, e.g.:
        -- keystroke "someKey" using {modifier1 down, modifier2 down, ...}
    end tell
end tell
'''
print(run_applescript(script7))

# Notify the user
message = 'Now, with Workspace open, please right click the highlighted files and click "Copy and Relink"'
message_encoded = urllib.parse.quote(message)
send_message(f'sweejhelper://notify/0/{message_encoded}')
