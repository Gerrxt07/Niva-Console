from colorama import init, Fore, Style
init(autoreset=True)

class Command:
    name = "sudo"
    description = "Execute commands with elevated privileges"
    hidden = True  # Mark as hidden

    async def execute(self, console, args):
        print(f"{Fore.YELLOW}sudo: Working, but not implemented yet.{Style.RESET_ALL}")
        return True