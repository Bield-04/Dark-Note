#!/bin/bash

# Acessa o diretório onde o script está salvo
cd "$(dirname "$0")"

# (Opcional) Se você usa venv, descomente a linha abaixo ajustando o nome da pasta:
# source venv/bin/activate

echo "🚀 Iniciando o Bloco de Notas..."
python3 main.py
