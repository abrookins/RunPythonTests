#!/bin/bash

# Copyright (c) 2011 Will Bond <will@wbond.net>

VERSION=$(sw_vers -productVersion)

if (( $(expr $VERSION '<' 10.7) )); then
    RUNNING=$(osascript<<END
    tell application "System Events"
        count(processes whose name is "iTerm")
    end tell
END
)
else
    RUNNING=1
fi

if (( $RUNNING )); then
    osascript<<END
    tell application "iTerm"
        activate
        set term to (make new terminal)
        tell term
            set sess to (launch session "Default Session")
            tell sess
                write text "$1"
            end tell
        end tell
    end tell
END
else
    osascript<<END
    tell application "iTerm"
        activate
        set sess to the first session of the first terminal
        tell sess
            write text "$1"
        end tell
    end tell
END
fi