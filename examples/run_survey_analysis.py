#!/usr/bin/env python3
"""
Exemplo prático de execução do workflow de análise de dados de pesquisa
"""

import asyncio
import os
from pathlib import Path
from datetime import datetime

# Importar o workflow
from ai.workflows.survey_data_visualization_workflow.workflow import get_survey_data_visualization_workflow


async def run_survey_analysis(xlsx_file_path: str, output_dir: str = None):
    """
    Executa análise completa de dados de pesquisa
    
    Args:
        xlsx_file_path: Caminho para o arquivo XLSX de pesquisa
        output_dir: Diretório para salvar os resultados (opcional)
    """
    
    # Verificar se o arquivo existe
    if not Path(xlsx_file_path).exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {xlsx_file_path}")
    
    # Criar diretório de output se necessário
    if output_dir is None:
        output_dir = f"data/surveys/outputs/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"🔄 Iniciando análise da pesquisa...")
    print(f"📁 Arquivo: {xlsx_file_path}")
    print(f"📊 Output: {output_dir}")
    
    # Criar instância do workflow
    workflow = get_survey_data_visualization_workflow(
        session_id=f"survey-analysis-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    
    # Preparar mensagem de entrada
    analysis_message = f"""
    Por favor, analise os dados de pesquisa do arquivo XLSX:
    
    Arquivo: {xlsx_file_path}
    
    Instruções:
    1. Extraia todas as colunas que contenham 'pesquisa' no nome
    2. Classifique automaticamente os tipos de dados de cada coluna
    3. Gere visualizações profissionais apropriadas para cada tipo de dado
    4. Compile um dashboard interativo com insights executivos
    5. Salve os resultados no diretório: {output_dir}
    
    Estrutura esperada das colunas:
    - pesquisa300625_screen0 até pesquisa300625_screen9
    - Tipos de dados: categóricos, numéricos, temporais, textuais
    
    Gere relatório executivo com recomendações de negócio.
    """
    
    try:
        # Executar workflow com streaming para acompanhar progresso
        print("\n📈 Executando workflow...")
        
        async for response in workflow.run(
            message=analysis_message,
            stream=True,
            stream_intermediate_steps=True
        ):
            # Mostrar progresso de cada etapa
            if hasattr(response, 'step_name') and response.step_name:
                print(f"   ⏳ {response.step_name}: {response.content[:100]}...")
        
        # Resultado final
        final_result = await workflow.arun(message=analysis_message)
        
        print("\n✅ Análise concluída com sucesso!")
        print(f"📊 Resultados salvos em: {output_dir}")
        print(f"📄 Logs completos disponíveis no sistema")
        
        return final_result
        
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {str(e)}")
        raise


async def main():
    """Exemplo de uso principal"""
    
    # Exemplo 1: Análise básica
    xlsx_file = "data/surveys/raw/pesquisa_satisfacao_2024.xlsx"
    
    if Path(xlsx_file).exists():
        result = await run_survey_analysis(xlsx_file)
        print(f"\n🎯 Resultado: {result}")
    else:
        print(f"⚠️  Arquivo de exemplo não encontrado: {xlsx_file}")
        print("   Coloque sua planilha em data/surveys/raw/ e ajuste o caminho acima")


if __name__ == "__main__":
    # Executar análise
    asyncio.run(main())