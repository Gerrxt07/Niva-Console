import Scripts.Core.Startup as Startup
import CLI.Core as Console
import asyncio

Startup.run()

asyncio.run(Console.run())