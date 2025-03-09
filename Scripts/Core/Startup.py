import Scripts.Core.Update as Update
from Scripts.Core.Logging import log

def main():
    log("INFO", "Starting the application")
    Update.run_updater()
