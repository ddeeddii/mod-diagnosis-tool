# Mod Diagnosis Tool
 Python script that attempts to find problems with currently installed Repentance mods.

# Usage
## Releases
1. Download the latest release
2. Run main.exe 

## From source
### Prerequisites
- Python

### Steps
1. Clone the repo
2. Run main.py

# How it works
The scripts checks all folders inside the `/mods/` folder.
It matches them against a couple of known problems:
- `items.xml` not matching `itempools.xml`
- `xml` file inside `/resources`
- mod not being updated since Repentance's mod patch

