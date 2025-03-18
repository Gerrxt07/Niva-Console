from Scripts.Core.Language import get_message

class Command:
    name = "exit"
    description = get_message('exit_description')
    
    async def execute(self, console, args):
        console.running = False
        return False
