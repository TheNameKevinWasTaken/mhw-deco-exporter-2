# mhw-deco-exporter-2

## What it does:
  It copies your monster hunter save to a temp folder > decrypts it > grabs the deco data > deletes the temp folder > exports yours decos.
  It never makes changes to your original save file, the only time it touches the file is to copy it.
  
  The ouput of this is a text file in a formatted list for https://honeyhunterworld.com/mhwbi deco input.

## Requirements:

    - This tool was written in python 3.7 so I can’t confirm it works with any other version.
    - I'll put together an exe with pyinstaller for people who don’t want to get all the python packages needed.
        - If you see this, I haven’t done it yet

## How to use it:
  Before using: go to your item box > set decorations > current equipment > press any deco > press "x" on keyboard or "start" on controller to remove all > save game (The program reads the deco data from your box, it can’t grab ones on your equipment)
  
  To use the program simply run deco-exporter.py with the decos.txt, floats.pickle, and ints.pickle files in the same directory. (or the exe when I make it)
  
  Press the "Open Web Pages to get ID" button to open the webpages to find your steamID3, if you already know it press the "Select the userdata\<your ID> folder"

  This should open up select folder prompt, highlight your steamID3 folder and "Select Folder"
  The program will now do all <What it does:> part of this readme and create an export.txt in the same location.
  The contents of this txt file can be pasted into https://honeyhunterworld.com/mhwbi > settings > decoration data (press re-write after you paste in)
  You can close the program.

## Problems:
  I don’t know of any so far, if you find any, add an issue on this GitHub or message me on discord: pocget#9572
  
## Thanks to:
  The script uses the decryption logic found https://github.com/LEGENDFF/mhw-Savecrypt which I have rewritten in python to remove the need for java.
  Thank you to https://github.com/clicksilver/mhw_decos_csv for the memory addresses of the decos
