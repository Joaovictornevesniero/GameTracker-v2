import time
from process_watcher import is_running
from afk_detector import is_afk, get_idle_seconds
from window_focus import is_focused, get_active_exe

TEST_EXE = 'notepad.exe'

print(f'Monitorando {TEST_EXE}... (Ctrl+C para parar)')
print('-' * 50)

while True:
    rodando = is_running(TEST_EXE)
    afk = is_afk(threshold_seconds=10)
    foco = is_focused(TEST_EXE)
    idle = get_idle_seconds()

    print(f'[{TEST_EXE}] rodando={rodando} | idle={idle:.1f}s | afk={afk} | foco={foco}')
    time.sleep(2)