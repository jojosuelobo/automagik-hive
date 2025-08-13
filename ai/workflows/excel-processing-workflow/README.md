# Excel Processing Workflow

Este workflow foi desenvolvido para processar arquivos Excel (.xlsx) através de múltiplos passos organizados, começando com o agente separador que lê e estrutura os dados para análise posterior.

## Visão Geral

O **Excel Processing Workflow** é composto por três passos principais:

1. **Excel Separation Step** - Agente separador que lê e processa o arquivo Excel
2. **Data Analysis Step** - (Preparado para implementação do próximo agente)
3. **Report Generation Step** - (Preparado para expansões futuras)

## Componentes

### 1. Excel Separator Agent (`excel-separator-agent`)

O agente separador é responsável por:
- Ler arquivos Excel (.xlsx/.xls)
- Identificar tipos de dados em cada coluna (numérico, texto, data)
- Separar e estruturar os dados em formato JSON
- Validar a integridade dos dados extraídos
- Fornecer metadados detalhados sobre cada coluna

### 2. Workflow de Processamento

O workflow coordena a execução sequencial dos passos:
- **Passo 1**: Separação e estruturação dos dados Excel
- **Passo 2**: Análise dos dados (placeholder para próximo agente)
- **Passo 3**: Geração de relatórios finais

## Como Usar

### Requisitos

- Arquivo Excel válido (.xlsx ou .xls)
- Pandas instalado (já incluído nas dependências do projeto)

### Exemplo de Uso

```python
import asyncio
from ai.workflows.excel_processing_workflow.workflow import get_excel_processing_workflow_workflow

async def processar_excel():
    # Criar instância do workflow
    workflow = get_excel_processing_workflow_workflow()
    
    # Caminho para o arquivo Excel
    arquivo_excel = "/caminho/para/seu/arquivo.xlsx"
    
    # Executar o workflow
    resultado = await workflow.arun(message=f"file_path: {arquivo_excel}")
    
    print("Processamento concluído:")
    print(resultado.content)

# Executar o exemplo
asyncio.run(processar_excel())
```

### Formato de Entrada

O workflow aceita duas formas de entrada:

1. **Com prefixo**: `file_path: /caminho/para/arquivo.xlsx`
2. **Direto**: `/caminho/para/arquivo.xlsx`

### Formato de Saída

O workflow retorna dados estruturados em JSON contendo:

```json
{
  "step": "excel_separation",
  "file_info": {
    "file_path": "/caminho/arquivo.xlsx",
    "total_rows": 100,
    "total_columns": 5,
    "column_names": ["Nome", "Idade", "Email", "Salário", "Data"],
    "file_size_mb": 0.15,
    "processed_at": "2024-01-15T10:30:00"
  },
  "separated_data": {
    "columns": {
      "Nome": {
        "data": ["João", "Maria", "Pedro", ...],
        "type": "text",
        "non_null_count": 98,
        "null_count": 2,
        "unique_values": 95,
        "sample_values": ["João", "Maria", "Pedro", "Ana", "Carlos"],
        "avg_length": 8.5,
        "max_length": 15
      },
      "Idade": {
        "data": [25, 30, 35, ...],
        "type": "numeric",
        "non_null_count": 100,
        "null_count": 0,
        "unique_values": 45,
        "sample_values": [25, 30, 35, 28, 42],
        "min_value": 18,
        "max_value": 65,
        "mean_value": 35.2
      }
    },
    "metadata": {
      "total_rows": 100,
      "total_columns": 5,
      "processed_at": "2024-01-15T10:30:00",
      "file_path": "/caminho/arquivo.xlsx"
    }
  },
  "validation_report": {
    "is_valid": true,
    "issues": [],
    "warnings": [],
    "summary": {
      "total_columns": 5,
      "numeric_columns": 2,
      "text_columns": 3,
      "datetime_columns": 0,
      "empty_columns": 0,
      "total_issues": 0,
      "total_warnings": 0
    }
  },
  "status": "completed"
}
```

## Funcionalidades do Agente Separador

### Detecção de Tipos de Dados

O agente identifica automaticamente:
- **Numérico**: Inteiros e decimais
- **Texto**: Strings e dados categóricos
- **Data/Hora**: Timestamps e datas

### Validação de Dados

- Verifica colunas vazias
- Identifica alta porcentagem de valores nulos
- Valida consistência de dados numéricos
- Gera relatório de qualidade dos dados

### Metadados Gerados

Para cada coluna, o agente fornece:
- Contagem de valores válidos e nulos
- Valores únicos e amostras
- Estatísticas específicas por tipo (min/max para numéricos, comprimento para texto)

## Próximos Passos

O workflow está preparado para receber:

1. **Agente de Análise**: Para processamento e análise dos dados separados
2. **Funcionalidades Customizadas**: Baseadas nas necessidades específicas
3. **Relatórios Avançados**: Geração de insights e visualizações

## Estrutura de Arquivos

```
ai/workflows/excel-processing-workflow/
├── config.yaml          # Configuração do workflow
├── workflow.py          # Implementação do workflow
└── README.md           # Esta documentação

ai/agents/excel-separator-agent/
├── config.yaml          # Configuração do agente
├── agent.py            # Implementação do agente
└── __init__.py         # Package initialization
```

## Troubleshooting

### Erros Comuns

1. **Arquivo não encontrado**: Verifique se o caminho está correto
2. **Formato inválido**: Certifique-se de usar arquivos .xlsx ou .xls
3. **Pandas não encontrado**: Já incluído nas dependências do projeto

### Logs

O workflow gera logs detalhados sobre cada passo:
- Informações do arquivo lido
- Progresso da separação de colunas
- Resultados da validação
- Resumo final do processamento

---

**Versão**: 1.0  
**Autor**: Setup inicial para processamento Excel  
**Data**: Janeiro 2024 