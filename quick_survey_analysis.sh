#!/bin/bash
# Script de execução rápida para análise de pesquisa
# Uso: ./quick_survey_analysis.sh caminho/para/planilha.xlsx

set -e  # Parar em caso de erro

# Verificar se arquivo foi fornecido
if [ $# -eq 0 ]; then
    echo "❌ Erro: Forneça o caminho para o arquivo XLSX"
    echo "Uso: $0 caminho/para/planilha.xlsx"
    echo "Exemplo: $0 /Users/joao/Downloads/pesquisa.xlsx"
    exit 1
fi

XLSX_FILE="$1"
PROJECT_DIR="/Users/josuelobo/Documents/random/automagik-hive-fork/automagik-hive"

echo "🚀 EXECUÇÃO RÁPIDA - ANÁLISE DE PESQUISA"
echo "======================================"

# 1. Ir para diretório do projeto
echo "📁 Mudando para diretório do projeto..."
cd "$PROJECT_DIR"

# 2. Verificar branch
echo "🔧 Verificando branch..."
git checkout 13aug2

# 3. Criar diretórios
echo "📂 Criando estrutura de diretórios..."
mkdir -p data/surveys/raw
mkdir -p data/surveys/outputs

# 4. Verificar se arquivo existe
if [ ! -f "$XLSX_FILE" ]; then
    echo "❌ Arquivo não encontrado: $XLSX_FILE"
    exit 1
fi

# 5. Copiar arquivo para local correto
FILENAME=$(basename "$XLSX_FILE")
TARGET_PATH="data/surveys/raw/$FILENAME"

echo "📋 Copiando arquivo para: $TARGET_PATH"
cp "$XLSX_FILE" "$TARGET_PATH"

# 6. Instalar dependências se necessário
echo "📦 Verificando dependências..."
uv pip install -e .[analytics] --quiet

# 7. Executar análise
echo "⚡ Executando análise..."
python scripts/analyze_survey.py "$TARGET_PATH"

# 8. Mostrar resultados
echo ""
echo "✅ EXECUÇÃO CONCLUÍDA!"
echo "📊 Resultados disponíveis em:"
LATEST_OUTPUT=$(ls -t data/surveys/outputs/ | head -1)
echo "   Dashboard: $PROJECT_DIR/data/surveys/outputs/$LATEST_OUTPUT/dashboard.html"
echo "   PDF: $PROJECT_DIR/data/surveys/outputs/$LATEST_OUTPUT/relatorio_executivo.pdf"
echo ""
echo "🌐 Para abrir o dashboard:"
echo "   open data/surveys/outputs/$LATEST_OUTPUT/dashboard.html"