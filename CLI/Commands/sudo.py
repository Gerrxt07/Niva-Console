from colorama import init, Fore, Style
init(autoreset=True)

class Command:
    name = "sudo"
    description = "Execute commands with elevated privileges"
    hidden = True  # Mark as hidden

    async def execute(self, console, args):
        password = input(f"{Fore.YELLOW}Enter password: {Style.RESET_ALL}")
        if password == "test":
            console.sudo_mode = True
            print(f"{Fore.GREEN}Entered sudo mode{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Incorrect password{Style.RESETALL}")
        return True
