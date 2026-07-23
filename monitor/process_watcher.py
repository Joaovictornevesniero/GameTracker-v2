import psutil

def get_running_executables():
    executables = []
    for proc in psutil.process_iter(['name']):
        try:
            executables.append(proc.info['name'].lower())
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return executables

def is_running(exe_name):
    return exe_name.lower() in get_running_executables()