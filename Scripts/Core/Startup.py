import Scripts.Core.Update as Update
from Scripts.Core.Logging import log
import aioconsole
import asyncio

def main():
    log("INFO", "Starting the application")
    Update.run_updater()

def run():
    main()
