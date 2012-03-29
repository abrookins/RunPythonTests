#!/bin/bash

# Copyright (c) 2011 Will Bond <will@wbond.net>


VERSION=$(sw_vers -productVersion)
if (( $(expr $VERSION '<' 10.7.0) )); then
	IN_WINDOW="in window 1"
fi
osascript<<END
try
	tell application "System Events"
		if (count(processes whose name is "Terminal")) is 0 then
			tell application "Terminal"
				activate
				do script "$1" $IN_WINDOW
			end tell
		else
			tell application "Terminal"
				activate
				do script "$1"
			end tell
		end if
	end tell
end try
END