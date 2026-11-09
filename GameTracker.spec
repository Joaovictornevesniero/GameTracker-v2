# -*- mode: python ; coding: utf-8 -*-
# Gerar o .exe:  pyinstaller GameTracker.spec
a = Analysis(['main.py'], excludes=['tkinter'])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='GameTracker', console=False)
