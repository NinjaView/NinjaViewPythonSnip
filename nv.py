import os
import winreg
import sys
import uuid
import time
import logging
import hashlib
import signal
import threading
import psutil
import PIL.Image
import tkinter as tk
import base64
import atexit
import subprocess
import requests
import pyperclip
import base64
from tkinter import simpledialog, messagebox, filedialog
from io import BytesIO
from datetime import datetime
from pystray import Icon as icon, Menu as menu, MenuItem as item
from threading import Thread as FlaskThread
import flask
from flask import request, jsonify, current_app
ngrok_process = None
is_verified = False
ngrok_started = False
public_url = None
details = {
    "ngrokAUTHTOKEN": "Default",
    "ngrokDOMAIN": "Default",
    "ngrokLOCATION": "Default"
}

def send_ati_command(command):
    try:
        # Connect to NinjaTrader ATI port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 36973))  # Adjust IP and port as necessary
            s.sendall(command.encode())
            data = s.recv(1024)
            print('Received', repr(data))
    except Exception as e:
        print("An error occurred:", e)

# Example command (replace with actual ATI command)
command = "PLACE;Account=Sim1;Instrument=ES 12-23;Action=BUY;Qty=1;OrderType=LIMIT;LimitPrice=4139;TIF=DAY"
send_ati_command(command)

