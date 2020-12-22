# pyssrs
Python String Search and Replace Script

This script was created to clean up the names of the TV recordings created by the DVB software. The backend I'm usint (TVHeadend) has very good options to customize the name, but the actual OTA EPG data can not be edited on the fly. While the shows are most of the time named reasonably, there are some frequently occurring conventions. One, for example, is the "Movie:" tag in front of a movie. This ends up in files named as Movie_ Deadpool-TVChannel-YYYY-MM-DD-HH-MM.mkv .

While this is not particularly annoying, it causes the files to get sorted randomly and the ever-growing movie collection ends up a mess.

This script makes it possible to create rules to remove these unwanted tags from desired files in a specified location. It can also be applied to the contents of text files so that the tag is also removed inside the file. I use this to clean up the .nfo (xml) files created from the EPG data.

This script is a Python rewrite of my older SSRS script. The problem with SSRS was that it was written with AutoHotkey, which is a Windows-only scripting language. I'm planning on moving the whole DVB recording setup to a single Linux-based computer, so this rewrite was needed.

The rule-tagging and setup borrows from the other subsystem of my setup, pycos (that handles the conversion of the files and creating .nfo (XML) files). On top of being platform agnostic, it is also more flexible, as you can use different settings and rule files with CLI parameters, as SSRS was written as one big script file.

## Requirements:
* Windows or GNU/Linux compatible. Should probably work with OSX (untested)
* Python 3.7 or higher

## Usage/setup:
* Download the repository either manually as .zip (and unpack) or with git (>git clone https://github.com/TurboK234/pyssrs).
* Copy the pyssrs.py file if needed (e.g. to a "scripts" folder), this is optional.
* Copy the settings.txt and rules.txt (either from the root folder or from the defaults folder (identical files)) to a desired place (e.g. ~/pyssrs_settings/settingsprofile1/ ) and rename the settings file to something else if you want. NOTE: You can also run the script in the original folder and use the settings.txt and rules.txt in the same folder by default, but this is the least flexible way, and it's difficult to have several conversion "profiles" this way.
* Edit the settings file. Do this carefully. And read the comments that should give enough information to get you started.
* Edit the rules.txt (NOTE: rules.txt can not be renamed, but it can reside in a different folder than settings, if specified in the settings file). Rules file is very important for the script functionality, since without any rules, there will be nothing to search for and edit.

## Execution:
* Run the program with Python. The syntax is `python path/to/pyssrs.py path/to/settingsfile` . You can also just run `python /path/to/pyssrs.py` , but then you need to have properly set settings.txt (with the original name) in the same folder as pyssrs.py .
