# GameTracker

Rastreador de tempo de jogo para Windows. Detecta o jogo pelo processo e conta o tempo enquanto ele está aberto.
Funciona com jogos normais (`.exe`) e com **emuladores**, separando cada ROM/ISO (GBA, DS, PS1/PS2, etc.).

## Rodar
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
Gerar o `.exe`: `pip install pyinstaller` e depois `pyinstaller GameTracker.spec` (sai em `dist\`).
O banco `gametracker.db` fica ao lado do `.exe` (ou do `main.py`).

## Como adicionar um jogo
- **Jogo normal:** informe o `.exe`.
- **Emulador:** informe o `.exe` do emulador **e** a ROM/ISO. Abra o jogo no emulador e use
  **Detectar jogo aberto** para preencher sozinho.

A ROM é procurada na linha de comando do processo e no título das janelas dele. Se o emulador mostra FPS ou
outras coisas variáveis no título, deixe no campo ROM/ISO só um trecho fixo (o nome do jogo).
Se houver um cadastro só com o `.exe` e outro com ROM para o mesmo emulador, a ROM tem prioridade.

## Estrutura
```
main.py          entrada, bandeja, instância única
monitor.py       thread que detecta jogos e grava sessões
rom.py           varredura de processos e identificação da ROM
db.py            SQLite, migração do banco antigo, consultas
startup.py       iniciar com o Windows
ui/              tema + Dashboard, Jogos, Histórico, diálogo de adicionar
```
