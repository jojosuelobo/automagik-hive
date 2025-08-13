"""
API routes para análise de dados de pesquisa
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from ai.workflows.survey_data_visualization_workflow.workflow import get_survey_data_visualization_workflow
from lib.logging import logger

router = APIRouter(prefix="/survey-analysis", tags=["Survey Analysis"])


class SurveyAnalysisRequest(BaseModel):
    """Modelo de request para análise de pesquisa"""
    file_path: str
    session_id: Optional[str] = None
    output_format: str = "all"  # all, dashboard, pdf, charts
    include_insights: bool = True
    include_recommendations: bool = True


class SurveyAnalysisResponse(BaseModel):
    """Modelo de response para análise de pesquisa"""
    analysis_id: str
    status: str
    message: str
    dashboard_url: Optional[str] = None
    pdf_url: Optional[str] = None
    results: Optional[dict] = None


# Storage para tracking de análises em andamento
analysis_jobs = {}


@router.post("/upload-and-analyze", response_model=SurveyAnalysisResponse)
async def upload_and_analyze_survey(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session_id: Optional[str] = None,
    output_format: str = "all"
):
    """
    Upload de arquivo XLSX e execução de análise de pesquisa
    """
    
    # Validar formato do arquivo
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Formato de arquivo não suportado. Use .xlsx ou .xls"
        )
    
    # Gerar ID único para a análise
    analysis_id = f"survey_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    if not session_id:
        session_id = f"api-{analysis_id}"
    
    # Salvar arquivo temporariamente
    upload_dir = Path("data/surveys/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"{analysis_id}_{file.filename}"
    
    try:
        # Salvar arquivo
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Registrar job
        analysis_jobs[analysis_id] = {
            "status": "queued",
            "file_path": str(file_path),
            "session_id": session_id,
            "output_format": output_format,
            "created_at": datetime.now().isoformat()
        }
        
        # Executar análise em background
        background_tasks.add_task(
            execute_survey_analysis_background,
            analysis_id,
            str(file_path),
            session_id,
            output_format
        )
        
        return SurveyAnalysisResponse(
            analysis_id=analysis_id,
            status="queued",
            message="Análise de pesquisa iniciada. Use GET /status/{analysis_id} para acompanhar o progresso."
        )
        
    except Exception as e:
        logger.error(f"Erro no upload e análise: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/analyze-file", response_model=SurveyAnalysisResponse)
async def analyze_existing_file(
    request: SurveyAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Análise de arquivo XLSX já existente no servidor
    """
    
    # Validar se arquivo existe
    file_path = Path(request.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Arquivo não encontrado: {request.file_path}"
        )
    
    # Gerar ID para análise
    analysis_id = f"survey_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    session_id = request.session_id or f"api-{analysis_id}"
    
    # Registrar job
    analysis_jobs[analysis_id] = {
        "status": "queued",
        "file_path": request.file_path,
        "session_id": session_id,
        "output_format": request.output_format,
        "created_at": datetime.now().isoformat()
    }
    
    # Executar em background
    background_tasks.add_task(
        execute_survey_analysis_background,
        analysis_id,
        request.file_path,
        session_id,
        request.output_format
    )
    
    return SurveyAnalysisResponse(
        analysis_id=analysis_id,
        status="queued",
        message="Análise iniciada. Use GET /status/{analysis_id} para acompanhar."
    )


@router.get("/status/{analysis_id}", response_model=SurveyAnalysisResponse)
async def get_analysis_status(analysis_id: str):
    """
    Obter status de uma análise de pesquisa
    """
    
    if analysis_id not in analysis_jobs:
        raise HTTPException(
            status_code=404,
            detail=f"Análise não encontrada: {analysis_id}"
        )
    
    job = analysis_jobs[analysis_id]
    
    response = SurveyAnalysisResponse(
        analysis_id=analysis_id,
        status=job["status"],
        message=job.get("message", ""),
        dashboard_url=job.get("dashboard_url"),
        pdf_url=job.get("pdf_url"),
        results=job.get("results")
    )
    
    return response


@router.get("/download/{analysis_id}/{file_type}")
async def download_analysis_file(analysis_id: str, file_type: str):
    """
    Download de arquivos gerados pela análise
    
    file_type: dashboard, pdf, charts, data
    """
    
    if analysis_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    
    job = analysis_jobs[analysis_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Análise ainda não concluída")
    
    # Determinar arquivo para download
    output_dir = Path(f"data/surveys/outputs/analysis_{analysis_id}")
    
    if file_type == "dashboard":
        file_path = output_dir / "dashboard.html"
        media_type = "text/html"
    elif file_type == "pdf":
        file_path = output_dir / "relatorio_executivo.pdf"
        media_type = "application/pdf"
    elif file_type == "data":
        file_path = output_dir / "analysis_results.json"
        media_type = "application/json"
    else:
        raise HTTPException(status_code=400, detail="Tipo de arquivo inválido")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=file_path.name
    )


@router.get("/list-analyses")
async def list_analyses():
    """
    Listar todas as análises de pesquisa
    """
    
    analyses = []
    for analysis_id, job in analysis_jobs.items():
        analyses.append({
            "analysis_id": analysis_id,
            "status": job["status"],
            "file_path": job["file_path"],
            "created_at": job["created_at"],
            "dashboard_available": job.get("dashboard_url") is not None,
            "pdf_available": job.get("pdf_url") is not None
        })
    
    return {"analyses": analyses, "count": len(analyses)}


async def execute_survey_analysis_background(
    analysis_id: str,
    file_path: str,
    session_id: str,
    output_format: str
):
    """
    Executar análise de pesquisa em background
    """
    
    try:
        # Atualizar status
        analysis_jobs[analysis_id]["status"] = "processing"
        analysis_jobs[analysis_id]["message"] = "Executando workflow de análise..."
        
        # Criar diretório de output
        output_dir = Path(f"data/surveys/outputs/analysis_{analysis_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Criar workflow
        workflow = get_survey_data_visualization_workflow(session_id=session_id)
        
        # Preparar mensagem de análise
        analysis_message = f"""
        Analise os dados de pesquisa do arquivo: {file_path}
        
        Requisitos:
        1. Extrair colunas com padrão 'pesquisa*'
        2. Classificar tipos de dados automaticamente
        3. Gerar visualizações profissionais
        4. Criar dashboard interativo
        5. Gerar relatório executivo
        
        Configurações:
        - Formato de saída: {output_format}
        - Diretório de saída: {output_dir}
        - Incluir insights de negócio: true
        - Incluir recomendações: true
        """
        
        # Executar workflow
        result = await workflow.arun(message=analysis_message)
        
        # Atualizar status de sucesso
        analysis_jobs[analysis_id].update({
            "status": "completed",
            "message": "Análise concluída com sucesso",
            "dashboard_url": f"/survey-analysis/download/{analysis_id}/dashboard",
            "pdf_url": f"/survey-analysis/download/{analysis_id}/pdf",
            "results": json.loads(result.content) if hasattr(result, 'content') else {},
            "completed_at": datetime.now().isoformat()
        })
        
        logger.info(f"Análise {analysis_id} concluída com sucesso")
        
    except Exception as e:
        # Atualizar status de erro
        analysis_jobs[analysis_id].update({
            "status": "failed",
            "message": f"Erro na análise: {str(e)}",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        })
        
        logger.error(f"Análise {analysis_id} falhou: {str(e)}")