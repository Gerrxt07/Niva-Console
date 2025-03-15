class Command:
    name = "clear"
    description = "Clear the screen"
    
    async def execute(self, console, args):
        console.clear_screen()
        return True