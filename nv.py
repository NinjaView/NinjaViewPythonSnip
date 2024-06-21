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
