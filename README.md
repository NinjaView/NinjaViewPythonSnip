# NinjaView Proof of Concept Documentation

## Introduction

This document provides a guide on how to run a Python script that is part of the NinjaView application. This particular script serves as a proof of concept, demonstrating that Ninja Trader is not a virus. It is important to note that when compiled with PyInstaller, this script may trigger false positive antivirus flags.

## Prerequisites

Before proceeding, ensure that you have the following prerequisites installed on your system:

- **Python**: Version 3.6 or later
- **pip**: A package installer for Python

You can install the required Python packages using the following command:

```sh
pip install flask pystray Pillow requests psutil pyperclip
```
## Setup
Clone the Repository or Download the Script: Download the Python script from its repository or any provided source.

Navigate to the Script Directory: Use the command line to navigate to the directory containing the script.


Copy code
cd path/to/script/directory
Install Virtual Environment (Optional): It is a good practice to create a virtual environment to isolate the project dependencies.


```
python -m venv venv
.\venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Unix or MacOS
```
Install Requirements: Install the required packages using pip:


```
pip install -r requirements.txt
```
Note: If there is no requirements.txt file provided, you will need to manually install the required packages listed in the script. Some of the packages that might be required include os, winreg, sys, uuid, time, logging, hashlib, signal, threading, psutil, PIL, tkinter, base64, atexit, subprocess, requests, pyperclip, pystray, flask, and ngrok.

Running the Script
Execute the Script: Run the script using Python.
```
python proof.py
```
Compiling with PyInstaller
Install PyInstaller: If you don’t have PyInstaller installed, you can install it using pip:


```
pip install pyinstaller
```
Compile the Script: Use PyInstaller to compile the script.


```
pyinstaller --onefile --noconsole proof.py
```
If you want to add an icon to the executable, you can use the --icon option (This will cause more false anti-virus flags:

```
pyinstaller --onefile --noconsole --icon=icon.ico proof.py
```
Replace icon.ico with the path to your icon file.

# Scan your compiled .exe
http://virustotal.com/
```https://www.virustotal.com/gui/file/cfb5f7f7b6997bf247ba64d165ea135fde34c641b2d256fe03ef5c3562546047?nocache=1```

# This concludes the reason behind the false virus alerts

support@ninja-view.com

