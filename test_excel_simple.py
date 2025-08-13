#!/usr/bin/env python3
"""
Teste Simples do Agente Separador Excel
=====================================

Teste das funções básicas de separação de Excel sem dependências do framework
"""

import json
import os
import sys
from pathlib import Path

# Adicionar paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Importar as funções diretamente
import importlib.util

# Carregar o módulo do agente
agent_path = current_dir / "ai" / "agents" / "excel-separator-agent" / "agent.py"
spec = importlib.util.spec_from_file_location("excel_agent", agent_path)
excel_agent = importlib.util.module_from_spec(spec)

# Adicionar pandas e outras dependências ao path
import pandas as pd
from datetime import datetime

# Definir as funções localmente para evitar dependências
def read_excel_file_simple(file_path: str):
    """Versão simplificada da leitura de Excel"""
    try:
        df = pd.read_excel(file_path)
        
        file_info = {
            "file_path": file_path,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "file_size_mb": Path(file_path).stat().st_size / (1024 * 1024),
            "processed_at": datetime.now().isoformat()
        }
        
        print(f"✅ Excel file read successfully: {file_info['total_rows']} rows, {file_info['total_columns']} columns")
        return df, file_info
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {str(e)}")
        raise


def separate_columns_simple(df):
    """Versão simplificada da separação de colunas"""
    separated_data = {
        "columns": {},
        "metadata": {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "processed_at": datetime.now().isoformat()
        }
    }
    
    for column in df.columns:
        column_data = df[column]
        
        # Determinar tipo de coluna
        if pd.api.types.is_numeric_dtype(column_data):
            col_type = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(column_data):
            col_type = "datetime"
        else:
            col_type = "text"
        
        # Extrair informações da coluna
        separated_data["columns"][column] = {
            "data": column_data.fillna("").tolist(),  # Add full data array
            "type": col_type,
            "non_null_count": int(column_data.count()),
            "null_count": int(column_data.isnull().sum()),
            "unique_values": int(column_data.nunique()),
            "sample_values": column_data.dropna().head(3).tolist()
        }
        
        # Adicionar metadados específicos por tipo
        if col_type == "numeric":
            separated_data["columns"][column].update({
                "min_value": float(column_data.min()) if not column_data.empty else None,
                "max_value": float(column_data.max()) if not column_data.empty else None,
                "mean_value": float(column_data.mean()) if not column_data.empty else None
            })
        elif col_type == "text":
            separated_data["columns"][column].update({
                "avg_length": float(column_data.astype(str).str.len().mean()) if not column_data.empty else 0,
                "max_length": int(column_data.astype(str).str.len().max()) if not column_data.empty else 0
            })
    
    print(f"✅ Column separation completed: {len(separated_data['columns'])} columns processed")
    return separated_data


def validate_data_simple(separated_data):
    """Versão simplificada da validação"""
    validation_report = {
        "is_valid": True,
        "issues": [],
        "warnings": [],
        "summary": {},
        "validated_at": datetime.now().isoformat()
    }
    
    total_rows = separated_data["metadata"]["total_rows"]
    columns = separated_data["columns"]
    
    # Verificar colunas vazias
    empty_columns = [col for col, data in columns.items() if data["non_null_count"] == 0]
    if empty_columns:
        validation_report["warnings"].append(f"Colunas vazias encontradas: {empty_columns}")
    
    # Verificar alta porcentagem de nulos
    high_null_columns = []
    for col, data in columns.items():
        null_percentage = (data["null_count"] / total_rows) * 100
        if null_percentage > 50:
            high_null_columns.append(f"{col} ({null_percentage:.1f}% nulos)")
    
    if high_null_columns:
        validation_report["warnings"].append(f"Colunas com alta porcentagem de nulos: {high_null_columns}")
    
    # Gerar resumo
    validation_report["summary"] = {
        "total_columns": len(columns),
        "numeric_columns": len([c for c in columns.values() if c["type"] == "numeric"]),
        "text_columns": len([c for c in columns.values() if c["type"] == "text"]),
        "datetime_columns": len([c for c in columns.values() if c["type"] == "datetime"]),
        "empty_columns": len(empty_columns),
        "total_issues": len(validation_report["issues"]),
        "total_warnings": len(validation_report["warnings"])
    }
    
    print(f"✅ Data validation completed: {validation_report['summary']}")
    return validation_report


def test_excel_processing():
    """Teste principal do processamento Excel"""
    
    # Caminho do arquivo
    arquivo_excel = "ai/workflows/excel-processing-workflow/file/bruta.xlsx"
    arquivo_absoluto = os.path.abspath(arquivo_excel)
    
    print("🚀 Iniciando teste do processamento Excel")
    print(f"📁 Arquivo: {arquivo_absoluto}")
    
    # Verificar se arquivo existe
    if not os.path.exists(arquivo_absoluto):
        print(f"❌ Erro: Arquivo não encontrado: {arquivo_absoluto}")
        return
    
    # Informações básicas do arquivo
    file_size = os.path.getsize(arquivo_absoluto) / (1024 * 1024)
    print(f"💾 Tamanho: {file_size:.2f} MB")
    
    try:
        # Passo 1: Ler arquivo Excel
        print("\n📊 Passo 1: Lendo arquivo Excel...")
        df, file_info = read_excel_file_simple(arquivo_absoluto)
        
        print(f"   ✅ Linhas: {file_info['total_rows']}")
        print(f"   ✅ Colunas: {file_info['total_columns']}")
        print(f"   ✅ Nomes das colunas: {file_info['column_names'][:5]}{'...' if len(file_info['column_names']) > 5 else ''}")
        
        # Passo 2: Separar colunas
        print("\n🔧 Passo 2: Separando colunas...")
        separated_data = separate_columns_simple(df)
        
        # Passo 3: Validar dados
        print("\n🔍 Passo 3: Validando dados...")
        validation_report = validate_data_simple(separated_data)
        
        # Exibir resultados
        print("\n" + "="*50)
        print("📋 RESULTADOS DO PROCESSAMENTO")
        print("="*50)
        
        print(f"\n📊 Informações Gerais:")
        print(f"   Total de linhas: {file_info['total_rows']}")
        print(f"   Total de colunas: {file_info['total_columns']}")
        
        summary = validation_report["summary"]
        print(f"\n🔍 Resumo da Validação:")
        print(f"   Status: {'✅ VÁLIDO' if validation_report['is_valid'] else '❌ INVÁLIDO'}")
        print(f"   Colunas numéricas: {summary['numeric_columns']}")
        print(f"   Colunas de texto: {summary['text_columns']}")
        print(f"   Colunas de data: {summary['datetime_columns']}")
        print(f"   Problemas: {summary['total_issues']}")
        print(f"   Avisos: {summary['total_warnings']}")
        
        # Mostrar avisos se houver
        if validation_report["warnings"]:
            print(f"\n⚠️  Avisos encontrados:")
            for warning in validation_report["warnings"]:
                print(f"   - {warning}")
        
        # Mostrar exemplos de colunas
        print(f"\n📋 Exemplo de Colunas (primeiras 3):")
        columns = separated_data["columns"]
        for i, (nome_coluna, info_coluna) in enumerate(list(columns.items())[:3]):
            print(f"\n   🏷️  {i+1}. {nome_coluna}")
            print(f"      Tipo: {info_coluna['type']}")
            print(f"      Valores válidos: {info_coluna['non_null_count']}")
            print(f"      Valores únicos: {info_coluna['unique_values']}")
            print(f"      Amostras: {info_coluna['sample_values']}")
        
        # Salvar resultado completo
        resultado_completo = {
            "file_info": file_info,
            "separated_data": separated_data,
            "validation_report": validation_report
        }
        
        with open("resultado_teste_simples.json", "w", encoding="utf-8") as f:
            json.dump(resultado_completo, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Resultado completo salvo em: resultado_teste_simples.json")
        print(f"🎉 Teste concluído com sucesso!")
        
        return resultado_completo
        
    except Exception as e:
        print(f"\n❌ Erro durante o processamento:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("🎯 TESTE SIMPLES DO PROCESSAMENTO EXCEL")
    print("=" * 60)
    
    test_excel_processing() 