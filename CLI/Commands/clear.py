from Scripts.Core.Language import get_message

class Command:
    name = "clear"
    description = get_message('clear_description')
    
    async def execute(self, console, args):
        console.clear_screen()
        return True
