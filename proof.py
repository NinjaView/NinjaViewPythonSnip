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
base64_string = """R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs="""
image_data = base64.b64decode(base64_string)
background_image = Image.open(BytesIO(image_data))
