import platform, socket, getpass

async def get_os_name():
    return platform.system()

async def get_device_name():
    return socket.gethostname()

async def get_user_name():
    return getpass.getuser()
