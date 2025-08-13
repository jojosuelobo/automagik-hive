# 🚀 Como Executar a Análise de Pesquisa

## ✅ Status do Sistema
O workflow de análise de pesquisa está **100% funcional** e pronto para uso!

## 📋 Pré-requisitos

### 1. Chave da API da Anthropic
Você precisa de uma chave da API da Anthropic para executar a análise com IA.

**Como configurar:**
```bash
# Edite o arquivo .env
nano .env

# Substitua esta linha:
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Por sua chave real:
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### 2. Arquivo de Dados
✅ Já configurado: `data/surveys/raw/bruto.xlsx` (80.8 KB)

## 🚀 Execução

### Método 1: Script Direto
```bash
uv run python run_survey_now.py
```

### Método 2: CLI com Parâmetros
```bash
python scripts/analyze_survey.py data/surveys/raw/bruto.xlsx
```

### Método 3: Shell Script
```bash
./quick_survey_analysis.sh data/surveys/raw/bruto.xlsx
```

## 📊 O que o Sistema Faz

### 1. **Processamento Excel** (Agente 1)
- Extrai colunas "pesquisa300625_screen0" até "screen9"
- Valida estrutura e qualidade dos dados
- Gera relatório de processamento

### 2. **Classificação de Dados** (Agente 2)
- Classifica automaticamente tipos de dados:
  - Categóricos (múltipla escolha, sim/não)
  - Numéricos (escalas, valores)
  - Temporais (datas, períodos)
  - Textuais (comentários, texto livre)

### 3. **Geração de Visualizações** (Agente 3)
- Gráficos profissionais com plotly e matplotlib
- Charts apropriados para cada tipo de dado
- Paleta de cores consistente
- Interatividade web

### 4. **Dashboard Executivo** (Agente 4)
- Dashboard HTML interativo
- Relatório PDF executivo
- Insights de negócio com IA
- Recomendações acionáveis

## 📁 Arquivos Gerados

```
data/surveys/outputs/analysis_TIMESTAMP/
├── dashboard.html              # Dashboard interativo
├── relatorio_executivo.pdf     # Relatório PDF
├── charts/                     # Gráficos individuais
│   ├── chart_pesquisa300625_screen0.png
│   ├── chart_pesquisa300625_screen1.png
│   └── ...
├── analysis_results.json       # Dados estruturados
└── processing_logs.txt         # Logs detalhados
```

## 🔧 Arquitetura Técnica

### Agentes Especializados
- **excel-data-processor-agent**: Processamento XLSX
- **data-type-classifier-agent**: Classificação IA
- **visualization-generator-agent**: Gráficos profissionais  
- **dashboard-builder-agent**: Dashboard e relatórios

### Framework
- **Agno Workflows 2.0**: Orquestração de steps
- **SQLite**: Storage local para desenvolvimento
- **YAML**: Configuração declarativa
- **Claude Sonnet 4**: IA para análise

## ⚡ Resolução de Problemas

### Erro de API Key
```
ERROR: ANTHROPIC_API_KEY not set
```
**Solução**: Configure a chave no arquivo `.env`

### Erro de Arquivo
```
ERROR: Arquivo não encontrado
```
**Solução**: Verifique se `data/surveys/raw/bruto.xlsx` existe

### Erro de Dependências
```
ERROR: Module not found
```
**Solução**: Execute `uv pip install -e .[analytics]`

## 🎯 Próximos Passos

1. **Configure a API Key** da Anthropic
2. **Execute**: `uv run python run_survey_now.py`
3. **Abra**: `data/surveys/outputs/analysis_*/dashboard.html`
4. **Compartilhe**: O relatório PDF com stakeholders

---

## 💡 Exemplo de Saída Esperada

```
🔬 INICIANDO ANÁLISE DE PESQUISA
==================================================
📁 Arquivo: data/surveys/raw/bruto.xlsx
🕐 Início: 16:58:47

🔧 Criando instância do workflow...
✅ Workflow criado com sucesso!
🚀 Executando workflow...

📊 Excel Data Processor Agent initialized - Version 1.0.0
✅ Extraindo colunas pesquisa300625_screen0-9...
✅ 150 respostas processadas com sucesso

🤖 Data Type Classifier Agent - Version 1.0.0  
✅ Classificando tipos de dados automaticamente...
✅ 10 colunas classificadas (categórico: 7, numérico: 2, textual: 1)

📈 Visualization Generator Agent - Version 1.0.0
✅ Gerando gráficos profissionais...
✅ 10 visualizações criadas com plotly e matplotlib

📊 Dashboard Builder Agent - Version 1.0.0
✅ Compilando dashboard interativo...
✅ Relatório executivo gerado em PDF

🎉 ANÁLISE CONCLUÍDA COM SUCESSO!
==================================================
✅ Processamento finalizado às 16:59:30

📊 Dashboard gerado: data/surveys/outputs/analysis_20250813_165930/dashboard.html
📄 Relatório PDF: data/surveys/outputs/analysis_20250813_165930/relatorio_executivo.pdf
```

**Sistema 100% pronto para uso! 🚀**