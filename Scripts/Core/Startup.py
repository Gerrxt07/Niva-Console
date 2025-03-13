import Scripts.Core.Update as Update
from Scripts.Core.Logging import log
import asyncio

async def main():
    log("INFO", "Starting the application")
    await Update.run_updater()

def run():
    asyncio.run(main())