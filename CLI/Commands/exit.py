class Command:
    name = "exit"
    description = "Exit the console"
    
    async def execute(self, console, args):
        console.running = False
        return False