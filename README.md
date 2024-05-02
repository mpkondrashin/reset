# reset.py - reset overwritten settings for Trend Micro Deep Security and Workload Security

**reset.py resets general computer settings and anti-malware paremeter to settings from policy**

## Requirements
1. Python 3.x
2. Internet connectivity (to download required packages)

## Installation

**Note:** Below commands are for Linux and macOS. For Windows use corresponding commands.

1. Download [latest release](https://github.com/mpkondrashin/reset/archive/refs/heads/master.zip). 
2. Unpack zip archive.
3. Create Virtual Environment using following command: ```python3 -m venv venv```
4. Activate source: ```source venv/bin/activate```
5. Install all required packages: ```pip install -r requirements.txt```

## Usage

Using reset.py operates in two stages:
1. Save list of all computers in file. This file can be edited to leave computers that require further treatment.
2. Reset settings for computers listed in a given file.

reset.py supports following command line options:
1. ```--apikey``` - Deep Securty or Workload Security API Key (mandatory).
2. ```--hostname``` - Deep Security Manager hostname or Cloud One/Vision One Workload Security  (mandatory).
3. ```--filename``` - name of the file to store/read list of computers in CSV format.
4. ```--antimalware``` - reset only anti-malware settings.
5. ```--settings``` - reset only general computer settings.
6. ```--all``` - reset both - anti-malware and general settings.

To save all computers into CSV file use following command:
```commandline
python reset.py --hostname https://dsm.local:4119/api --apikey XYZ list --filename computers.csv
```

Command to reset antimalware settings:
```commandline
python reset.py --hostname https://dsm.local:4119/api --apikey XYZ reset --filename computers.csv --antimalware
```

replace ```--antimalware``` to ```--settings``` to reset general settings or to ```---all``` to reset both.
