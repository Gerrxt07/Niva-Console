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
from Scripts.Core.Logging import log
import hashlib
from tqdm import tqdm
import aioconsole

# Initialize colorama for Windows compatibility
init(autoreset=True)

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
        self.required_files = ['Niva.py', 'config.toml', 'scripts']
        
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
        
        log("INFO", f"Creating backup at: {self.backup_path}")
        await asyncio.to_thread(shutil.copytree, '.', self.backup_path, ignore=shutil.ignore_patterns('backups', self.staging_dir, self.temp_dir, '__pycache__', '.git'))
        log("INFO", "Backup created successfully")

    async def cleanup_old_backups(self, max_backups=5):
        backups = sorted(Path('backups').iterdir(), key=os.path.getmtime)
        while len(backups) > max_backups:
            old_backup = backups.pop(0)
            await asyncio.to_thread(shutil.rmtree, old_backup)
            log("INFO", f"Deleted old backup: {old_backup}")

    async def rollback(self):
        if self.backup_path and os.path.exists(self.backup_path):
            log("WARNING", "Initiating rollback...")
            # Clear current directory (except backups and staging)
            for item in os.listdir('.'):
                if item not in ['backups', self.staging_dir, self.temp_dir, '.git']:
                    path = Path(item)
                    if path.is_dir():
                        await asyncio.to_thread(shutil.rmtree, path)
                    else:
                        await asyncio.to_thread(os.remove, path)
            
            # Restore from backup
            await asyncio.to_thread(shutil.copytree, self.backup_path, '.', dirs_exist_ok=True)
            log("INFO", "Rollback completed successfully")
            return True
        log("ERROR", "Rollback failed: No backup available")
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
            log("ERROR", f"Invalid update package. Missing: {', '.join(missing)}")
            return False
        return True

    async def get_latest_version(self):
        log("INFO", "Checking for latest Niva-Console release")
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        retry_attempts = 3
        for attempt in range(retry_attempts):
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
                log("ERROR", f"Update check failed (Attempt {attempt + 1}/{retry_attempts}): {str(e)}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(2)
                else:
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
            log("ERROR", f"Atomic update failed: {str(e)}")
            return False

    async def calculate_checksum(self, file_path):
        hash_sha256 = hashlib.sha256()
        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                data = await f.read(4096)
                if not data:
                    break
                hash_sha256.update(data)
        return hash_sha256.hexdigest()

    async def verify_checksum(self, file_path, expected_checksum):
        calculated_checksum = await self.calculate_checksum(file_path)
        return calculated_checksum == expected_checksum

    async def get_checksum_from_release(self, latest_release):
        assets = latest_release.get('assets', [])
        for asset in assets:
            if asset['name'].endswith('.sha256'):
                async with aiohttp.ClientSession() as session:
                    async with session.get(asset['browser_download_url']) as response:
                        response.raise_for_status()
                        checksum_data = await response.text()
                        return checksum_data.split()[0]
        return None

    async def download_with_progress(self, url, session):
        """Download a file with a progress bar"""
        async with session.get(url) as response:
            response.raise_for_status()
            
            # Get content length for progress bar
            total_size = int(response.headers.get('content-length', 0))
            
            # Create a buffer to store the downloaded data
            buffer = bytearray()
            
            # Create and configure progress bar
            progress_bar = tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                desc=f"Downloading update",
                ascii=True,  # Use ASCII characters for better cross-platform compatibility
                ncols=80     # Set width of progress bar
            )
            
            # Download the file in chunks
            chunk_size = 4096
            async for chunk in response.content.iter_chunked(chunk_size):
                buffer.extend(chunk)
                progress_bar.update(len(chunk))
            
            # Close the progress bar
            progress_bar.close()
            
            return bytes(buffer)

    async def perform_update(self, latest_release, auto_confirm=False):
        try:
            # If not auto-confirmed, prompt for confirmation
            if not auto_confirm:
                # Prompt for confirmation
                response = await aioconsole.ainput(Fore.YELLOW + "Do you want to proceed with the update? (y/n): ").lower()
                if response != 'y':
                    log("INFO", "Update canceled by user")
                    return False
                    
            # Create backup
            await self.create_backup()
            
            # Download release with progress bar
            log("INFO", f"Downloading version {latest_release['tag_name']}...")
            async with aiohttp.ClientSession(
                headers={'Accept': 'application/vnd.github.v3.raw'},
                timeout=aiohttp.ClientTimeout(total=60)  # Extended timeout for large downloads
            ) as session:
                # Use the download_with_progress method
                zip_data = await self.download_with_progress(latest_release['zipball_url'], session)
            
            log("INFO", "Extracting update package...")
            # Ensure temp dir doesn't exist
            if os.path.exists(self.temp_dir):
                await asyncio.to_thread(shutil.rmtree, self.temp_dir)
            
            os.makedirs(self.temp_dir, exist_ok=True)
            
            # Process extraction with progress
            log("INFO", "Extracting files...")
            with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_ref:
                total_files = len(zip_ref.namelist())
                extract_progress = tqdm(total=total_files, desc="Extracting files", unit="files", ascii=True, ncols=80)
                
                # Extract files one by one to show progress
                for file in zip_ref.namelist():
                    zip_ref.extract(file, self.temp_dir)
                    extract_progress.update(1)
                
                extract_progress.close()

            # The GitHub zipball usually contains a folder with the repository name and commit hash
            extracted_dir = os.path.join(self.temp_dir, os.listdir(self.temp_dir)[0])

            # Fetch and verify checksum
            expected_checksum = await self.get_checksum_from_release(latest_release)
            if expected_checksum:
                log("INFO", "Verifying download integrity...")
                zip_file_path = os.path.join(self.temp_dir, 'update.zip')
                async with aiofiles.open(zip_file_path, 'wb') as f:
                    await f.write(zip_data)
                if not await self.verify_checksum(zip_file_path, expected_checksum):
                    log("ERROR", "Checksum verification failed")
                    await self.rollback()
                    return False
                log("INFO", "Checksum verification successful")
            
            log("INFO", "Applying update...")
            # Show progress for the update application
            update_progress = tqdm(total=100, desc="Applying update", unit="%", ascii=True, ncols=80)
            
            # Simulate progress for the update process
            update_progress.update(25)  # Start at 25%
            # Perform atomic update
            success = await self.atomic_update(extracted_dir)
            update_progress.update(75)  # Complete to 100%
            update_progress.close()
            
            if success:
                # Update config version
                config = await self.load_config()
                config['Version'] = latest_release['tag_name']
                async with aiofiles.open(self.config_path, 'w') as f:
                    await f.write(toml.dumps(config))
                
                log("INFO", "Update completed successfully")
                log("WARNING", 'Please restart the application.')
                return True
            
            log("ERROR", "Update failed, initiating rollback")
            await self.rollback()
            return False

        except Exception as e:
            log("ERROR", f"Update failed: {str(e)}")
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
            return latest_release, f"Update available: {current_version} -> {latest_version}"
            
        except Exception as e:
            return None, f"Error checking for updates: {str(e)}"

    async def update(self, auto_confirm=False):
        """Main update method that can be called from other parts of the application"""
        log("INFO", f"Niva-Console Updater started on {self.os_type}")
        try:
            latest_release, message = await self.check_for_updates()
            log("INFO", message)
            
            if not latest_release:
                return False, message
                
            # Perform the update
            result = await self.perform_update(latest_release, auto_confirm)
            
            if result:
                await self.cleanup_old_backups()
                return True, "Update completed successfully"
            else:
                return False, "Update failed. System rolled back."

        except Exception as e:
            error_message = f'Critical Error: {str(e)}'
            log("ERROR", error_message)
            await self.rollback()
            return False, error_message


# Convenience function to run the updater with proper setup for all platforms
async def run_updater(auto_confirm=False):
    """Run the updater with proper platform-specific setup"""
    # Check for asyncio policy to handle Windows differences
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    updater = NivaUpdater()
    return await updater.update(auto_confirm)


# Direct execution handler
if __name__ == "__main__":
    try:
        # Check for asyncio policy to handle Windows differences
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        updater = NivaUpdater()
        asyncio.run(updater.update())
        log("INFO", "Press any key to exit...")
        # Cross-platform wait for input
        if platform.system() == "Windows":
            os.system("pause > nul")
        else:
            input()
            
    except KeyboardInterrupt:
        log("WARNING", "Update process interrupted by user")