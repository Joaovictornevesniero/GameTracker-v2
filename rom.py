"""Descobre quais jogos estão rodando, olhando os processos do Windows.

Jogo normal  -> basta o .exe estar rodando.
Emulador     -> o .exe + a ROM/ISO, que é procurada na linha de comando do processo
                e no título das janelas dele.
"""
import ntpath
import os

import psutil

try:
    import win32gui
    import win32process
except ImportError:  # fora do Windows (só para testes)
    win32gui = win32process = None

ROM_EXT = {
    '.gba', '.gbc', '.gb', '.nds', '.3ds', '.cia', '.nes', '.sfc', '.smc', '.n64', '.z64', '.v64',
    '.gen', '.md', '.smd', '.gg', '.sms', '.pce', '.iso', '.cso', '.chd', '.cue', '.gcm', '.gcz',
    '.rvz', '.wbfs', '.wad', '.nsp', '.xci', '.pkg', '.zip', '.7z',
}


def rom_key(rom):
    """Nome da ROM normalizado para comparação (sem pasta, sem extensão de jogo, minúsculo)."""
    base = ntpath.basename(rom.strip().strip('"'))
    stem, ext = ntpath.splitext(base)
    return (stem if ext.lower() in ROM_EXT else base).casefold()


def rom_in_cmdline(args):
    for arg in args[1:]:
        arg = arg.strip('"')
        if ntpath.splitext(arg)[1].lower() in ROM_EXT:
            return ntpath.basename(arg)
    return None


def _cmdline(proc):
    try:
        return proc.cmdline()
    except (psutil.Error, OSError):
        return []


def window_titles():
    """{pid: [títulos das janelas visíveis]}"""
    out = {}
    if not win32gui:
        return out

    def collect(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                out.setdefault(win32process.GetWindowThreadProcessId(hwnd)[1], []).append(title)
        return True

    try:
        win32gui.EnumWindows(collect, None)
    except Exception:
        pass
    return out


def find_active(games):
    """IDs dos jogos que estão rodando agora. Uma única varredura de processos por chamada."""
    by_exe = {}
    for g in games:
        by_exe.setdefault(g['executable'].lower(), []).append(g)

    procs = []
    for p in psutil.process_iter(['name']):
        name = (p.info['name'] or '').lower()
        if name in by_exe:
            procs.append((p, name))
    if not procs:
        return set()

    titles = window_titles() if any(g['rom'] for _, n in procs for g in by_exe[n]) else {}
    active = set()
    for p, name in procs:
        cands = by_exe[name]
        with_rom = [g for g in cands if g['rom']]
        hay = ''
        if with_rom:
            hay = ' '.join(_cmdline(p) + titles.get(p.pid, [])).casefold()
        hits = [g for g in with_rom if rom_key(g['rom']) in hay]
        # Jogo com ROM tem prioridade; o cadastro só do .exe pega o que sobrar
        active.update(g['id'] for g in (hits or [g for g in cands if not g['rom']]))
    return active


def running_windows():
    """Programas com janela aberta, para o botão 'Detectar jogo aberto'."""
    titles = window_titles()
    out = []
    for p in psutil.process_iter(['pid', 'name']):
        if p.pid == os.getpid() or p.pid not in titles:
            continue
        out.append({'exe': p.info['name'] or '?',
                    'rom': rom_in_cmdline(_cmdline(p)),
                    'title': titles[p.pid][0]})
    return sorted(out, key=lambda x: x['exe'].lower())
