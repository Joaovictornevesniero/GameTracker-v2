import win32gui
import win32process
import psutil

def get_active_exe():
    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        proc = psutil.Process(pid)
        return proc.name().lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

def is_focused(exe_name):
    return get_active_exe() == exe_name.lower()

if __name__ == '__main__':
    import time
    print('Monitorando janela ativa... (Ctrl+C para parar)')
    while True:
        exe = get_active_exe()
        print(f'Janela ativa: {exe}')
        time.sleep(2)
        