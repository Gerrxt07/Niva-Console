import Scripts.Core.Update as Update
from Scripts.Core.Logging import log
import aioconsole
import asyncio

async def main():
    log("INFO", "Starting the application")
    await Update.run_updater()
    log("INFO", "Press any key to exit...")
    await aioconsole.ainput()

if __name__ == "__main__":
    asyncio.run(main())
