import os
import asyncio
import platform
import importlib
import pathlib
import sys
from colorama import init, Fore, Style
from Scripts.Core.Logging import log
import Scripts.Core.Device as Device
from Database.Database import Database  # P8cbc

# Initialize colorama
init(autoreset=True)

def masked_input(prompt):
    print(prompt, end='', flush=True)
    if platform.system() == "Windows":
        import msvcrt
        pwd = []
        while True:
            ch = msvcrt.getch()
            if ch in [b'\r', b'\n']:
                print()
                break
            elif ch == b'\x03':  # Ctrl+C
                raise KeyboardInterrupt
            elif ch == b'\x08':  # Backspace
                if pwd:
                    pwd.pop()
                    print('\b \b', end='', flush=True)
            else:
                pwd.append(ch.decode('utf-8', errors='ignore'))
                print('*', end='', flush=True)
        return ''.join(pwd)
    else:
        import termios, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        pwd = ""
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ['\n', '\r']:
                    print()
                    break
                elif ch == '\x03':
                    raise KeyboardInterrupt
                elif ch == '\x7f':
                    if pwd:
                        pwd = pwd[:-1]
                        print('\b \b', end='', flush=True)
                else:
                    pwd += ch
                    print('*', end='', flush=True)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return pwd

class NivaConsole:
    def __init__(self):
        self.user = None
        self.device = None
        self.os = None
        self.path = "~"
        self.commands = {}
        self.running = False
        self.sudo_mode = False
        self.db = Database("Database/database.db")  # P8cbc
        self.db.initialize()  # P8cbc
        
    async def initialize(self):
        """Initialize the console with system information and commands"""
        self.device = await Device.get_device_name()
        self.user = await Device.get_user_name()
        self.os = await Device.get_os_name()
        await self._load_commands()
        log("INFO", f"Console initialized for {self.user}@{self.device}")

    async def _load_commands(self):
        """Dynamically load commands from CLI/Commands directory"""
        commands_dir = pathlib.Path("CLI/Commands")
        
        try:
            for file in commands_dir.glob("*.py"):
                if file.name.startswith("__") or file.name == "template.py":
                    continue

                module_name = f"CLI.Commands.{file.stem}"
                try:
                    module = importlib.import_module(module_name)
                    cmd_class = getattr(module, "Command", None)
                    
                    if cmd_class:
                        command = cmd_class()
                        if hasattr(command, "name") and hasattr(command, "execute"):
                            self.commands[command.name] = command
                            log("DEBUG", f"Loaded command: {command.name}")
                        else:
                            log("ERROR", f"Invalid command structure in {file.name}")
                except Exception as e:
                    log("ERROR", f"Failed to load {file.stem}: {str(e)}")
            
            log("INFO", f"Successfully loaded {len(self.commands)} commands")
        except Exception as e:
            log("ERROR", f"Command loading failed: {str(e)}")
            raise

    async def get_prompt(self):
        """Generate the command prompt with styling"""
        user_color = Fore.YELLOW
        device_color = Fore.CYAN
        path_color = Fore.BLUE
        symbol_color = Fore.WHITE
        
        if self.sudo_mode:  # Pfdf6
            prompt = f"{user_color}{self.device}{Style.RESET_ALL}@" \
                     f"{device_color}{self.os} {path_color}{self.path}{symbol_color}#: {Style.RESET_ALL}"
        else:
            prompt = f"{user_color}{self.user}{Style.RESET_ALL}@" \
                     f"{device_color}{self.device} " \
                     f"{path_color}{self.path}{symbol_color}$: {Style.RESET_ALL}"
        return prompt
    
    async def get_input(self, prompt):
        """Get user input with prompt"""
        print(prompt, end='', flush=True)
        
        try:
            return await asyncio.to_thread(input)
        except (EOFError, KeyboardInterrupt):
            return "exit"

    async def execute_command(self, command):
        """Execute a command from loaded commands"""
        if not command:
            return True
            
        parts = command.strip().split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in self.commands:
            try:
                if self.sudo_mode and cmd == "exit_sudo":  # Pc95e
                    self.sudo_mode = False
                    print(f"{Fore.GREEN}Exited sudo mode{Style.RESET_ALL}")
                    return True
                return await self.commands[cmd].execute(self, args)
            except Exception as e:
                log("ERROR", f"Command execution error: {e}")
                print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
                return True
        else:
            print(f"{Fore.RED}Command not found: {cmd}{Style.RESET_ALL}")
            return True

    async def show_help(self):
        """Show help information for loaded commands"""
        help_text = [
            f"\n{Fore.YELLOW}┌─ Niva Console Help ───────────────────────┐{Style.RESET_ALL}",
            f"{Fore.YELLOW}│{Style.RESET_ALL} Available Commands:                       {Style.RESET_ALL}"
        ]
        
        # Add command help (excluding hidden commands)
        for cmd in sorted(self.commands.values(), key=lambda x: x.name):
            if getattr(cmd, 'hidden', False):
                continue
            help_line = f" • {Fore.GREEN}{cmd.name.ljust(10)}{Style.RESET_ALL} {cmd.description}"
            help_text.append(f"{Fore.CYAN}│{Style.RESET_ALL}{help_line.ljust(46)}{Style.RESET_ALL}")

        help_text.append(f"{Fore.YELLOW}└───────────────────────────────────────────┘{Style.RESET_ALL}\n")
        print("\n".join(help_text))

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
        
    async def print_banner(self):
        """Print the console banner"""
        banner = f"""
{Fore.YELLOW}╔═══════════════════════════════════════════════════════════╗
║                   N I V A   C O N S O L E                 ║
╚═══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(banner)
        
    def masked_input(self, prompt):
        return masked_input(prompt)

    async def check_initial_users(self):
        users = self.db.get_all_users()
        if not users:
            print(f"{Fore.RED}No users found in the database.{Style.RESET_ALL}")
            while True:
                username = input(f"{Fore.YELLOW}Create a new user (username): {Style.RESET_ALL}")
                password = self.masked_input(f"{Fore.YELLOW}Create a new user (password): {Style.RESET_ALL}")
                self.db.add_user(username, password)
                print(f"{Fore.GREEN}User created successfully!{Style.RESET_ALL}")
                self.user = username
                break
        else:
            first_user = users[0]
            self.user = first_user[1]
            print(f"{Fore.GREEN}Auto-logged in as {self.user}.{Style.RESET_ALL}")

    async def start(self):
        """Start the console"""
        await self.initialize()
        self.running = True
        
        self.clear_screen()
        await self.print_banner()
        
        print(f"{Fore.YELLOW}Welcome to Niva Console!{Style.RESET_ALL}")
        print(f"Type '{Fore.GREEN}help{Style.RESET_ALL}' to see available commands.\n")
        
        await self.check_initial_users()
        
        while self.running:
            try:
                prompt = await self.get_prompt()
                command = await self.get_input(prompt)
                
                if command.lower() == "help":
                    await self.show_help()
                else:
                    if not await self.execute_command(command):
                        break
                        
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                log("ERROR", f"Console error: {e}")
                print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}Goodbye!{Style.RESET_ALL}")

# Global console instance
console = NivaConsole()

async def run():
    """Run the console"""
    await console.start()

if __name__ == "__main__":
    asyncio.run(run())
