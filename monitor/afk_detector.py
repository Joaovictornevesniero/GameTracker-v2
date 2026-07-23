import ctypes
import time

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ('cbSize', ctypes.c_uint),
        ('dwTime', ctypes.c_uint)
    ]

def get_idle_seconds():
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    millis_now = ctypes.windll.kernel32.GetTickCount()
    idle_millis = millis_now - lii.dwTime
    return idle_millis / 1000.0

def is_afk(threshold_seconds=300):
    return get_idle_seconds() >= threshold_seconds

if __name__ == '__main__':
    print('Monitorando inatividade... (Ctrl+C para parar)')
    while True:
        idle = get_idle_seconds()
        afk = is_afk(threshold_seconds=10)
        print(f'Inativo há: {idle:.1f}s | AFK (10s): {afk}')
        time.sleep(2)