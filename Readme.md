GameTracker

Rastreador universal de tempo de gameplay para Windows.

Registra automaticamente sessões de jogo independente da plataforma — Steam, Epic, GOG, emuladores, jogos diretos por .exe — com detecção de AFK e foco de janela para medir tempo real de jogo, não apenas tempo de execução.

Stack
1. Python 3.12+
2. PySide6 (interface)
3. SQLite (banco local)
4. psutil (monitoramento de processos)
5. pywin32 (integração Windows)


Funcionalidades:
1. Detecção automática de jogos por processo (.exe)
2. Cálculo de tempo real com desconto de AFK
3. Histórico de sessões por jogo
4. Dashboard com sessões ativas em tempo real
5. Suporte a múltiplos jogos simultâneos
6. Início automático com o Windows (opcional)


Instalação

1. Clone o repositório

git clone https://github.com/seu-usuario/gametracker.git
cd gametracker

2. Crie e ative o ambiente virtual

python -m venv venv
venv\Scripts\activate

3. Instale as dependências

pip install -r requirements.txt

4. Rode o projeto

python main/Main.py

Estrutura

gametracker/
├── database/       # Banco de dados e queries
├── monitor/        # Lógica de rastreamento em segundo plano
├── ui/             # Interface gráfica (PySide6)
└── main/           # Ponto de entrada do app

Status

🚧 Em desenvolvimento — v0.1