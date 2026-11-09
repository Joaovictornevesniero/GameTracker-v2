"""Iniciar com o Windows (chave Run do registro do usuário)."""
import os
import sys
import winreg

KEY = r'Software\Microsoft\Windows\CurrentVersion\Run'
NAME = 'GameTracker'


def _command():
    if getattr(sys, 'frozen', False):
        return f'"{sys.executable}" --tray'
    python = sys.executable.replace('python.exe', 'pythonw.exe')
    return f'"{python}" "{os.path.abspath(sys.argv[0])}" --tray'


def enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY) as k:
            winreg.QueryValueEx(k, NAME)
        return True
    except FileNotFoundError:
        return False


def set_enabled(on):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY, 0, winreg.KEY_SET_VALUE) as k:
        if on:
            winreg.SetValueEx(k, NAME, 0, winreg.REG_SZ, _command())
        else:
            try:
                winreg.DeleteValue(k, NAME)
            except FileNotFoundError:
                pass
