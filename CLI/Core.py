import os
import asyncio
import platform
import importlib
import pathlib
from colorama import init, Fore, Style
from Scripts.Core.Logging import log
import Scripts.Core.Device as Device

# Initialize colorama
init(autoreset=True)

class NivaConsole:
    def __init__(self):
        self.user = None
        self.device = None
        self.path = "~"
        self.commands = {}
        self.running = False
        
    async def initialize(self):
        """Initialize the console with system information and commands"""
        self.device = await Device.get_device_name()
        self.user = await Device.get_user_name()
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
        
    async def start(self):
        """Start the console"""
        await self.initialize()
        self.running = True
        
        self.clear_screen()
        await self.print_banner()
        
        print(f"{Fore.YELLOW}Welcome to Niva Console!{Style.RESET_ALL}")
        print(f"Type '{Fore.GREEN}help{Style.RESET_ALL}' to see available commands.\n")
        
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