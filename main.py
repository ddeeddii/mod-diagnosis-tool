import tkinter as tk
import tkinter.filedialog as fd
from xml.dom import minidom
import os
from math import floor
from datetime import datetime

# https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def colorPrint(text, color):
    text = f"{color}{text}{bcolors.ENDC}"

    print(text)


def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def checkItempools(path):
    _, mTail = os.path.split(path)

    content = f"{path}/content"

    if not os.path.isdir(content):
        return

    itemsPath = f"{content}/items.xml"
    itempoolsPath = f"{content}/itempools.xml"

    if not os.path.isfile(itemsPath) or not os.path.isfile(itempoolsPath):
        return

    # Parse items.xml and get all item names
    try:
        parsedItems = minidom.parse(itemsPath)
    except Exception as e:
        print(f"Unable to parse items.xml from mod {mTail}.\nManual checking of itempools.xml and items.xml parity required!\n")
        return

    itemslist = []
    tagsToFind = ["active", "passive", "familiar"]
    for tag in tagsToFind:    
        itemslist += parsedItems.getElementsByTagName(tag)

    itemsxmlNames = []
    for s in itemslist:
        name = str(s.attributes["name"].value)
        itemsxmlNames.append(name)
    
    # Parse itempools.xml and get all item names
    try:
        parsedItempools = minidom.parse(itempoolsPath)
    except Exception as e:
        print(f"Unable to parse itempools.xml from mod {mTail}.\nManual checking of itempools.xml and items.xml parity required!")
        return

    itempoolsList = parsedItempools.getElementsByTagName("Item")

    # Get all item names from itempools.xml and compare them to items.xml
    erroredItems = []

    for s in itempoolsList:
        name = str(s.attributes["Name"].value)

        if not (name in itemsxmlNames):
            if not (name in erroredItems):
                erroredItems.append(name)

    return erroredItems

def checkDates(path):
    patchDayTime = 1621093333 # may 15th, 2021 - patch where mods were enabled for rep
    timeModified = floor(os.path.getmtime(path))

    if timeModified < patchDayTime:
        return timeModified

def checkResources(path):
    resources = f"{path}/resources"

    if not os.path.isdir(resources):
        return

    erroredFiles = []
    with os.scandir(resources) as resourcesFolder:
        for file in resourcesFolder:
            _, extension = os.path.splitext(file.path)
            if extension == ".xml":
                erroredFiles.append(file.name)

    return erroredFiles



def main():
    # Ask user to select the mods folder
    print("Select the 'mods' directory where Isaac is installed:\n")

    root = tk.Tk()
    root.withdraw()
    modsPath = fd.askdirectory(title="Select the 'mods' directory where Isaac is installed")

    _, modsTail = os.path.split(modsPath)
    if modsTail != "mods":
        input("Path is incorrect! Make sure you selected the 'mods' folder in the place where Isaac is installed (where 'isaac-ng.exe' is)")
        os._exit(0)

    problems = []
    with os.scandir(modsPath) as modsMain:
        for rootEntry in modsMain:

            _, modTail = os.path.split(rootEntry.path)

            # Itempools checking
            erroredItems = checkItempools(rootEntry.path)
            if erroredItems:
                for item in erroredItems:
                    
                    problems.append(["ERROR", modTail, f"Item named '{item}' is present in mod's itempools.xml but not in items.xml!"])

            # XMLs in /resources/
            erroredFiles = checkResources(rootEntry.path)
            if erroredFiles:
                for file in erroredFiles:
    
                    if file == "items.xml":
                        problems.append(["ERROR", modTail, f"File named '{file}' is present in mod's /resources/ folder!"])
                    else:
                        problems.append(["WARN ", modTail, f"File named '{file}' is present in mod's /resources/ folder!"])
            
            # Edit times
            oldFile = checkDates(rootEntry.path)
            if oldFile:
                date = datetime.utcfromtimestamp(oldFile).strftime("%Y-%m-%d")
                problems.append(["WARN ", modTail, f"File was modified {date} which was before mods were enabled for Repentance!"])


    print("\nFinished diagnosing!\n")
    os.system('color') # Prepare for color printing

    for entry in problems:
        problemLevel = entry[0]
        modName = entry[1]
        problemText = entry[2]
        
        text = f"{problemLevel}: {modName} | {problemText}"

        if problemLevel == "WARN ":
            color = bcolors.WARNING
        elif problemLevel == "ERROR":
            color = bcolors.FAIL

        colorPrint(text, color)

    print("\nPress enter to exit.")
    input()


if __name__ == "__main__":
    # Start the sequence
    main()