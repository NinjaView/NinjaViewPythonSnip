# Understanding NinjaView: Understanding How NinaView Works and Addressing Potential Antivirus Flags



## Introduction

This document serves as an informative guide, detailing the functionality and setup process of a Python script integral to the NinjaView application. It is worth mentioning that, although the application is secure, certain antivirus programs might mistakenly identify it as a potential threat. This document aims to address these concerns and guide users through the installation and execution process.

`nv.py` uses NinjaTrader's Advanced Trade Interface (ATI) to place trades and manage orders. It establishes a connection to NinjaTrader's ATI port and sends trading commands directly, ensuring a seamless and swift execution of trades. Below is a simplified example of how it sends a trade command to NinjaTrader:

```
from flask import Flask, request, jsonify
from werkzeug.serving import make_server
import threading
import time
import logging
import uuid
import psutil
import pystray
from PIL import Image
import os
import winreg

app = Flask(__name__)
app.debug = False

# Set up logging
logging.basicConfig(level=logging.DEBUG)

allowed_ips = ["52.89.214.238", "34.212.75.30", "54.218.53.128", "52.32.178.7", "127.0.0.1"]

server = None
server_thread = None
tray_icon = None

# Check if a process is running
def check_if_process_running(process_name):
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if process_name.lower() in proc.info['name'].lower():
                return True, proc.info['pid']
        return False, None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return False, None

@app.before_request
def restrict_ip():
    client_ip = request.remote_addr
    if client_ip not in allowed_ips:
        logging.warning(f"HoneyPot/7.0 Unauthorized: {client_ip} logged.")
        return f"HoneyPot/7.0 Unauthorized: {client_ip} logged.", 401

@app.route('/', methods=['OPTIONS', 'POST', 'GET'])
def webhook():
    client_ip = request.remote_addr
    if client_ip not in allowed_ips:
        logging.warning(f"HoneyPot/7.0 Unauthorized: {client_ip} logged.")
        return f"HoneyPot/7.0 Unauthorized: {client_ip} logged.", 401

    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return '', 204, headers

    if request.method == 'GET':
        return jsonify({"message": "GET request received"}), 200

    is_running, pid = check_if_process_running('NinjaTrader.exe')
    if not is_running:
        logging.error("NinjaTrader.exe is not running.")
        return jsonify({"error": "NinjaTrader.exe is not running."}), 400

    content = request.get_json()
    if content is None:
        logging.error("No JSON content in request")
        return jsonify({"error": "No JSON content in request"}), 400

    alert = content.get('alert', '')
    account = content.get('account', 'Sim101')
    ticker = content.get('ticker', 'NQ 09-24')
    data = ''

    if alert == 'Market Long':
        data = f"PLACE;{account};{ticker};BUY;1;MARKET;;;DAY;;;;"
    elif alert == 'Market Short':
        data = f"PLACE;{account};{ticker};SELL;1;MARKET;;;DAY;;;;"
    elif alert == 'Close All':
        data = f"CLOSEPOSITION;{account};{ticker};;;;;;;;;;"
    elif alert == 'Close Then Long':
        data = f"CLOSEPOSITION;{account};{ticker};;;;;;;;;;"
        execute_command(data)
        time.sleep(1)
        data = f"PLACE;{account};{ticker};BUY;1;MARKET;;;DAY;;;;"
    elif alert == 'Close Then Short':
        data = f"CLOSEPOSITION;{account};{ticker};;;;;;;;;;"
        execute_command(data)
        time.sleep(1)
        data = f"PLACE;{account};{ticker};SELL;1;MARKET;;;DAY;;;;"

    if data:
        execute_command(data)

    logging.debug(f"Received alert: {alert}, wrote data: {data}")
    change_icon_color("green")  # Change icon color to green on successful connection

    return {'success': True}

def execute_command(command):
    personal_root = get_personal_root_from_registry()
    
    if not personal_root:
        logging.error("Personal root not found in registry")
        return
    
    file_name = os.path.join(personal_root, 'incoming', f'oif{uuid.uuid4()}.txt')
    logging.info(f"Attempting to execute command by placing order in {file_name}")

    try:
        with open(file_name, 'w') as f:
            f.write(command)
    except Exception as e:
        logging.error(f"Error writing to file: {e}")

def get_personal_root_from_registry():
    base_reg_path = r'SOFTWARE\NinjaTrader, LLC'
    versions = ['NinjaTrader 8', 'NinjaTrader 7']

    for version in versions:
        reg_path = os.path.join(base_reg_path, version)

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if 'cmp' in subkey_name:
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                personal_root, reg_type = winreg.QueryValueEx(subkey, 'PERSONAL_ROOT')
                                return personal_root
                    except OSError:
                        break
                    i += 1
        except OSError:
            continue
    
    return None

def create_menu():
    return pystray.Menu(
        pystray.MenuItem('Start Listening', start_server),
        pystray.MenuItem('Stop Listening', stop_server),
        pystray.MenuItem('Exit', exit_program)
    )

def create_tray_icon():
    global tray_icon
    icon_image = Image.new('RGB', (64, 64), color='red')
    tray_icon = pystray.Icon("NinjaView", icon_image, "NinjaView System Tray", create_menu())
    tray_icon.run()

def change_icon_color(color):
    global tray_icon
    if tray_icon:
        icon_image = Image.new('RGB', (64, 64), color=color)
        tray_icon.icon = icon_image
        tray_icon.update_menu()

def start_server(icon, item):
    global server, server_thread
    if server is None:
        server = make_server('0.0.0.0', 4002, app)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.start()
        logging.info("Server started")
        change_icon_color("green")  # Change icon color to green when server starts

def stop_server(icon, item):
    global server, server_thread
    if server:
        server.shutdown()
        server_thread.join()
        server = None
        server_thread = None
        logging.info("Server stopped")
        change_icon_color("red")  # Change icon color back to red when server stops

def exit_program(icon, item):
    if server:
        server.shutdown()
    icon.stop()

if __name__ == '__main__':
    create_tray_icon()
```

## Why is NinjaView a Paid Application?
NinjaView is a paid application because it represents the culmination of extensive research, development, and overcoming numerous challenges to provide a reliable and effective trading solution. The integration with NinjaTrader through its ATI port, as demonstrated in nv.py, required significant time and effort to perfect. Your purchase and support ensure continued development, improvements, and customer support for NinjaView, enabling traders to enhance their trading experience seamlessly.

## Building Trust in a New Frontier

NinjaView is a relatively new entrant in the trading software domain. We understand that building trust within the trading community takes time, especially when introducing innovative solutions that have never been seen before. Our commitment to transparency, security, and relentless improvement is unwavering. We are here to revolutionize trading automation and provide traders with unparalleled tools for success.

We encourage users to reach out with any questions, concerns, or feedback. Your insights and experience with NinjaView are invaluable to us and the wider trading community. Together, we are shaping the future of trading automation.


## Prerequisites

Before proceeding, ensure that you have the following prerequisites installed on your system:

- **Python**: Version 3.6 or later
- **pip**: A package installer for Python

You can install the required Python packages using the following command:

```sh
pip install flask pystray Pillow requests psutil pyperclip

```
## Setting Up the Script
Download the Script: Clone the repository or download the script from the provided source.
Navigate to the Script's Directory: Use your command line tool to go to the script's folder.
```cd path/to/script/directory```

Install Virtual Environment (Optional): It is a good practice to create a virtual environment to isolate the project dependencies.

```
cd path/to/script/directory

python -m venv venv
.\venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Unix or MacOS
```
Install Requirements: Install the required packages using pip:

```
pip install -r requirements.txt
or
pip install flask pystray Pillow requests psutil pyperclip
```
Note: Some of the packages that might be required include os, winreg, sys, uuid, time, logging, hashlib, signal, threading, psutil, PIL, tkinter, base64, atexit, subprocess, requests, pyperclip, pystray, flask, and ngrok.

Running the Script
Execute the Script: Run the script using Python.
```
python nv.py
```
Compiling with PyInstaller
Install PyInstaller: If you don’t have PyInstaller installed, you can install it using pip:

```
pip install pyinstaller
```
Compile the Script: Use PyInstaller to compile the script.


```
pyinstaller --onefile --noconsole nv.py
```
If you want to add an icon to the executable, you can use the --icon option (This will cause more false anti-virus flags:

```
pyinstaller --onefile --noconsole --icon=icon.ico nv.py
```
Replace icon.ico with the path to your icon file.

# Scan your compiled .exe
http://virustotal.com/

support@ninja-view.com


## Note on False Positive Antivirus Flags
When compiling Python scripts to executable files using PyInstaller, the resulting executable might be flagged by some antivirus programs as suspicious or malicious. This is a known issue with PyInstaller and other similar tools, and it happens because:

Heuristic Analysis: Antivirus programs use heuristic analysis to detect unusual patterns that might indicate malicious behavior. Compiled Python scripts often exhibit such patterns because the Python interpreter, script, and all dependencies are bundled into a single executable file.

Code Obfuscation: Some parts of the Python script may be obfuscated to protect intellectual property, which can trigger false positives.

Lack of Reputation: Newly created or rarely downloaded files might not have an established reputation, making them more likely to be flagged as potential threats.

Use in Malware: Unfortunately, attackers sometimes use tools like PyInstaller to package malicious scripts, which has led to a negative reputation for executables created with these tools.
