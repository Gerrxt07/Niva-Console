import datetime
import os
from colorama import Fore, init
import platform
from cryptography.fernet import Fernet

# Initialize colorama
init(autoreset=True)

# Define log levels
INFO = "INFO"
DEBUG = "DEBUG"
WARNING = "WARNING"
ERROR = "ERROR"

# Determine log directory based on OS
if platform.system() == "Windows":
    log_dir = os.path.join(os.getenv('APPDATA'), 'Niva', 'logs')
else:
    log_dir = os.path.join(os.path.expanduser('~'), 'Niva', 'logs')

os.makedirs(log_dir, exist_ok=True)

# Define a single log file for the entire script run
LOG_FILE = os.path.join(log_dir, datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S_logfile.log"))

# Generate or load encryption key
KEY_FILE = os.path.join(log_dir, 'key.key')
if os.path.exists(KEY_FILE):
    with open(KEY_FILE, 'rb') as key_file:
        key = key_file.read()
else:
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)

cipher_suite = Fernet(key)

def log(level, message):
    # Get current time and date
    now = datetime.datetime.now()
    timestamp = now.strftime("%H:%M:%S - %d-%m-%Y")
    
    # Format log message
    formatted_message = f"{timestamp} | [{level}]: {message}"
    
    # Print message to console with color
    if level == INFO:
        print(Fore.GREEN + formatted_message)
    elif level == DEBUG:
        print(Fore.BLUE + formatted_message)
    elif level == WARNING:
        print(Fore.YELLOW + formatted_message)
    elif level == ERROR:
        print(Fore.RED + formatted_message)
    else:
        print(formatted_message)
    
    # Encrypt the log message
    encrypted_message = cipher_suite.encrypt(formatted_message.encode())
    
    with open(LOG_FILE, 'ab') as file:
        file.write(encrypted_message + b'\n')

def decrypt_log_file(log_file_path):
    with open(log_file_path, 'rb') as file:
        encrypted_lines = file.readlines()
    
    decrypted_lines = [cipher_suite.decrypt(line.strip()).decode() for line in encrypted_lines]
    return decrypted_lines
