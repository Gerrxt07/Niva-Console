from colorama import init, Fore, Style
init(autoreset=True)

class Command:
    name = "sudo"
    description = "Execute commands with elevated privileges"
    hidden = True  # Mark as hidden

    async def execute(self, console, args):
        if console.sudo_mode:
            print(f"{Fore.RED}Already in sudo mode{Style.RESET_ALL}")
            return True

        password = input(f"{Fore.YELLOW}Enter password: {Style.RESET_ALL}")
        if console.db.validate_user(console.user, password) and console.db.get_user(console.user)[3] == 1:
            console.sudo_mode = True
            print(f"{Fore.GREEN}Entered sudo mode{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Incorrect password or insufficient privileges{Style.RESETALL}")
        return True
