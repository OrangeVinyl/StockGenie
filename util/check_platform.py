import platform

def get_os():
    os_name = platform.system()
    if os_name == 'Darwin':
        return 'macOS'
    elif os_name == 'Windows':
        return 'Windows'
    elif os_name == 'Linux':
        return 'Linux'
    else:
        return 'Unknown'