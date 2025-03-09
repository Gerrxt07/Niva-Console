import datetime
import os
from colorama import Fore, init
import platform

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
    
    with open(LOG_FILE, 'a') as file:
        file.write(formatted_message + '\n')