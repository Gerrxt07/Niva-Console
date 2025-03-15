class Command:
    name = "command_name"
    description = "Command description"
    usage = "command [options]"
    hidden = False
    
    async def execute(self, console, args):
        """
        Execute command logic
        Args:
            console: NivaConsole instance
            args: List of command arguments
        """
        # Your command logic here
        return True # Return True to continue, False to exit the console