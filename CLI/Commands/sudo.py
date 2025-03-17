import sys
import platform
from colorama import init, Fore, Style
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
            elif ch == b'\x03':
                raise KeyboardInterrupt
            elif ch == b'\x08':
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

class Command:
    name = "sudo"
    description = "Execute commands with elevated privileges"
    hidden = True  # Mark as hidden

    async def execute(self, console, args):
        if console.sudo_mode:
            print(f"{Fore.RED}Already in sudo mode{Style.RESET_ALL}")
            return True

        password = masked_input(f"{Fore.YELLOW}Enter password: {Style.RESET_ALL}")
        if console.db.validate_user(console.user, password):
            console.sudo_mode = True
            print(f"{Fore.GREEN}Entered sudo mode{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Incorrect password{Style.RESETALL}")
        return True
