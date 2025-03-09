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

def log(level, message):
    # Get current time and date
    now = datetime.datetime.now()
    timestamp = now.strftime("%H:%M - %d-%m-%Y")
    
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
    
    # Determine log directory based on OS
    if platform.system() == "Windows":
        log_dir = os.path.join(os.getenv('APPDATA'), 'Niva', 'logs')
    else:
        log_dir = os.path.join(os.path.expanduser('~'), 'Niva', 'logs')
    
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S_logfile.log"))
    
    with open(log_file, 'a') as file:
        file.write(formatted_message + '\n')
