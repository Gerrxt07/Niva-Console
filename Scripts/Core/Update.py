# Scripts/Core/Update.py
import aiohttp
import asyncio
import aiofiles
import toml
import os
import ssl
import certifi
from colorama import Fore, init
import zipfile
import io
import shutil
import time
from datetime import datetime
from pathlib import Path
import platform

# Initialize colorama for Windows compatibility
init()

# --------------- [ Async Update Module for Niva-Console ] --------------- #

class NivaUpdater:
    def __init__(self):
        self.config_path = 'config.toml'
        self.current_version = None
        self.backup_path = None
        self.staging_dir = 'update_staging'
        self.temp_dir = 'temp_update'
        self.os_type = platform.system()  # 'Windows', 'Linux', or 'Darwin' (macOS)
        
        # Adjust required files based on OS
        self.required_files = ['main.py', 'config.toml', 'scripts']
        
    async def load_config(self):
        async with aiofiles.open(self.config_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        config = toml.loads(content)
        self.current_version = config.get('Version')
        return config

    async def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Create backups directory if it doesn't exist
        if not os.path.exists('backups'):
            await asyncio.to_thread(os.makedirs, 'backups')
            
        self.backup_path = os.path.join('backups', f"niva_backup_{timestamp}")
        
        print(Fore.CYAN + f"Creating backup at: {self.backup_path}")
        await asyncio.to_thread(shutil.copytree, '.', self.backup_path, ignore=shutil.ignore_patterns('backups', self.staging_dir, self.temp_dir, '__pycache__'))
        print(Fore.GREEN + f"Backup created successfully")

    async def rollback(self):
        if self.backup_path and os.path.exists(self.backup_path):
            print(Fore.YELLOW + "Initiating rollback...")
            # Clear current directory (except backups and staging)
            for item in os.listdir('.'):
                if item not in ['backups', self.staging_dir, self.temp_dir]:
                    path = Path(item)
                    if path.is_dir():
                        await asyncio.to_thread(shutil.rmtree, path)
                    else:
                        await asyncio.to_thread(os.remove, path)
            
            # Restore from backup
            await asyncio.to_thread(shutil.copytree, self.backup_path, '.', dirs_exist_ok=True)
            print(Fore.GREEN + "Rollback completed successfully")
            return True
        print(Fore.RED + "Rollback failed: No backup available")
        return False

    async def validate_structure(self, extracted_dir):
        missing = []
        for item in self.required_files:
            path = os.path.join(extracted_dir, item)
            if item == 'scripts':
                if not os.path.isdir(path):
                    missing.append(item)
            else:
                if not os.path.isfile(path):
                    missing.append(item)
        
        if missing:
            print(Fore.RED + f"Invalid update package. Missing: {', '.join(missing)}")
            return False
        return True

    async def get_latest_version(self):
        print(Fore.CYAN + "Checking for latest Niva-Console release")
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        try:
            async with aiohttp.ClientSession(
                headers={'User-Agent': 'Niva-Console-Updater'},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                url = 'https://api.github.com/repos/Gerrxt07/Niva-Console/releases/latest'
                
                async with session.get(url, ssl=ssl_context) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            print(Fore.RED + f"Update check failed: {str(e)}")
            return None

    async def atomic_update(self, extracted_dir):
        try:
            # Prepare staging area
            if os.path.exists(self.staging_dir):
                await asyncio.to_thread(shutil.rmtree, self.staging_dir)
            
            await asyncio.to_thread(shutil.copytree, extracted_dir, self.staging_dir)
            
            # Validate staged files
            if not await self.validate_structure(self.staging_dir):
                return False

            # Replace current installation
            for item in os.listdir(self.staging_dir):
                src = os.path.join(self.staging_dir, item)
                dest = os.path.join('.', item)
                
                if os.path.exists(dest):
                    if os.path.isdir(dest):
                        await asyncio.to_thread(shutil.rmtree, dest)
                    else:
                        await asyncio.to_thread(os.remove, dest)
                
                if os.path.isdir(src):
                    await asyncio.to_thread(shutil.copytree, src, dest)
                else:
                    await asyncio.to_thread(shutil.copy2, src, dest)
            
            return True
        except Exception as e:
            print(Fore.RED + f"Atomic update failed: {str(e)}")
            return False

    async def perform_update(self, latest_release, auto_confirm=False):
        try:
            # If not auto-confirmed, prompt for confirmation
            if not auto_confirm:
                # Prompt for confirmation
                response = input(Fore.YELLOW + "Do you want to proceed with the update? (y/n): ").lower()
                if response != 'y':
                    print(Fore.YELLOW + "Update canceled by user")
                    return False
                    
            # Create backup
            await self.create_backup()
            
            # Download release
            print(Fore.CYAN + f"Downloading version {latest_release['tag_name']}...")
            async with aiohttp.ClientSession(
                headers={'Accept': 'application/octet-stream'},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                async with session.get(latest_release['zipball_url']) as response:
                    response.raise_for_status()
                    zip_data = await response.read()
            
            print(Fore.CYAN + "Extracting update package...")
            # Ensure temp dir doesn't exist
            if os.path.exists(self.temp_dir):
                await asyncio.to_thread(shutil.rmtree, self.temp_dir)
            
            os.makedirs(self.temp_dir, exist_ok=True)
            
            # Process update
            with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_ref:
                zip_ref.extractall(self.temp_dir)

            # The GitHub zipball usually contains a folder with the repository name and commit hash
            extracted_dir = os.path.join(self.temp_dir, os.listdir(self.temp_dir)[0])
            
            print(Fore.CYAN + "Applying update...")
            # Perform atomic update
            success = await self.atomic_update(extracted_dir)
            
            if success:
                # Update config version
                config = await self.load_config()
                config['Version'] = latest_release['tag_name']
                async with aiofiles.open(self.config_path, 'w') as f:
                    await f.write(toml.dumps(config))
                
                print(Fore.GREEN + "Update completed successfully")
                print(Fore.YELLOW + 'Please restart the application.')
                return True
            
            print(Fore.RED + "Update failed, initiating rollback")
            await self.rollback()
            return False

        except Exception as e:
            print(Fore.RED + f"Update failed: {str(e)}")
            await self.rollback()
            return False
        finally:
            # Cleanup
            for path in [self.temp_dir, self.staging_dir]:
                if os.path.exists(path):
                    await asyncio.to_thread(shutil.rmtree, path)

    async def check_for_updates(self):
        """Check for updates and return info about the latest version if available"""
        try:
            config = await self.load_config()
            latest_release = await self.get_latest_version()
            
            if not latest_release:
                return None, "Failed to fetch latest version information"
                
            current_version = self.current_version
            latest_version = latest_release['tag_name']
            
            if latest_version == current_version:
                return None, "Already up to date"
                
            # There's an update available
            return latest_release, f"Update available: {current_version} → {latest_version}"
            
        except Exception as e:
            return None, f"Error checking for updates: {str(e)}"

    async def update(self, auto_confirm=False):
        """Main update method that can be called from other parts of the application"""
        print(Fore.CYAN + f"Niva-Console Updater started on {self.os_type}")
        try:
            latest_release, message = await self.check_for_updates()
            print(Fore.CYAN + message)
            
            if not latest_release:
                return False, message
                
            # Perform the update
            result = await self.perform_update(latest_release, auto_confirm)
            
            if result:
                return True, "Update completed successfully"
            else:
                return False, "Update failed. System rolled back."

        except Exception as e:
            error_message = f'Critical Error: {str(e)}'
            print(Fore.RED + error_message)
            await self.rollback()
            return False, error_message


# Convenience function to run the updater with proper setup for all platforms
def run_updater(auto_confirm=False):
    """Run the updater with proper platform-specific setup"""
    # Check for asyncio policy to handle Windows differences
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    updater = NivaUpdater()
    return asyncio.run(updater.update(auto_confirm))


# Direct execution handler
if __name__ == "__main__":
    try:
        # Check for asyncio policy to handle Windows differences
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        updater = NivaUpdater()
        asyncio.run(updater.update())
        
        print(Fore.CYAN + "Press any key to exit...")
        # Cross-platform wait for input
        if platform.system() == "Windows":
            os.system("pause > nul")
        else:
            input()
            
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nUpdate process interrupted by user")