#!/usr/bin/env python3
"""Teste rápido do arquivo Excel"""

import pandas as pd
import os

# Caminho do arquivo
arquivo = "ai/workflows/excel-processing-workflow/file/bruta.xlsx"

print("🚀 Teste rápido do arquivo Excel")
print(f"📁 Arquivo: {arquivo}")

if not os.path.exists(arquivo):
    print("❌ Arquivo não encontrado")
    exit(1)

try:
    # Ler apenas as primeiras linhas
    print("📊 Lendo arquivo...")
    df = pd.read_excel(arquivo, nrows=5)
    
    print(f"✅ Arquivo lido com sucesso!")
    print(f"📋 Colunas: {list(df.columns)}")
    print(f"📊 Shape (primeiras 5 linhas): {df.shape}")
    print(f"\n🔍 Primeiras 3 linhas:")
    print(df.head(3))
    
    # Informações dos tipos
    print(f"\n📝 Tipos de dados:")
    print(df.dtypes)
    
except Exception as e:
    print(f"❌ Erro: {e}") 