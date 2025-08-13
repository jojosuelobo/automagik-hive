"""
Excel Processing Workflow - Comprehensive Excel File Processing Pipeline
=======================================================================

This workflow handles Excel file processing through multiple steps:
1. Excel Separation Step - Reading and structuring Excel data
2. Data Analysis Step - (Ready for future implementation)
3. Report Generation Step - (Ready for future implementation)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from lib.logging import logger
from agno.workflow.v2 import Workflow, Step
from agno.workflow.v2.types import StepInput, StepOutput
from ai.agents.excel_separator_agent.agent import (
    read_excel_file,
    separate_columns_data,
    validate_excel_data,
    get_excel_separator_agent
)


def execute_excel_separation_step(step_input: StepInput) -> StepOutput:
    """
    Execute Excel file separation step
    
    Args:
        step_input: Input containing Excel file path or data
        
    Returns:
        StepOutput with separated Excel data and metadata
    """
    input_message = step_input.message
    if not input_message:
        raise ValueError("Input message with Excel file path is required")
    
    logger.info("Executing Excel separation step...")
    
    try:
        # Extract file path from input message
        # Expect format: "file_path: /path/to/excel/file.xlsx" or just the path
        if "file_path:" in input_message:
            file_path = input_message.split("file_path:")[-1].strip()
        else:
            file_path = input_message.strip()
        
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        # Validate file extension
        if not file_path.lower().endswith(('.xlsx', '.xls')):
            raise ValueError(f"Invalid file format. Expected .xlsx or .xls, got: {file_path}")
        
        logger.info(f"Processing Excel file: {file_path}")
        
        # Step 1: Read basic file information
        file_info = read_excel_file(file_path)
        logger.info(f"📊 File info: {file_info['total_rows']} rows, {file_info['total_columns']} columns")
        
        # Step 2: Separate and structure column data
        separated_data = separate_columns_data(file_path)
        logger.info(f"📋 Columns separated: {len(separated_data['columns'])} columns processed")
        
        # Step 3: Validate the separated data
        validation_report = validate_excel_data(separated_data)
        logger.info(f"✅ Validation completed: {validation_report['summary']}")
        
        # Combine all results
        separation_results = {
            "step": "excel_separation",
            "file_info": file_info,
            "separated_data": separated_data,
            "validation_report": validation_report,
            "processing_timestamp": datetime.now().isoformat(),
            "status": "completed" if validation_report["is_valid"] else "completed_with_warnings"
        }
        
        # Log summary
        summary = (
            f"Excel separation completed:\n"
            f"- File: {file_info['file_path']}\n"
            f"- Rows: {file_info['total_rows']}\n"
            f"- Columns: {file_info['total_columns']}\n"
            f"- Validation: {'✅ Valid' if validation_report['is_valid'] else '⚠️ Has issues'}\n"
            f"- Issues: {len(validation_report['issues'])}\n"
            f"- Warnings: {len(validation_report['warnings'])}"
        )
        logger.info(summary)
        
        return StepOutput(content=json.dumps(separation_results, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "step": "excel_separation",
            "status": "error",
            "error": str(e),
            "processing_timestamp": datetime.now().isoformat()
        }
        logger.error(f"Excel separation failed: {str(e)}")
        return StepOutput(content=json.dumps(error_result, ensure_ascii=False, indent=2))


def execute_data_analysis_step(step_input: StepInput) -> StepOutput:
    """
    Execute survey data analysis step using the Survey Data Analyzer Agent
    
    Args:
        step_input: Input containing separated Excel data from previous step
        
    Returns:
        StepOutput with survey analysis results
    """
    # Get separation results from previous step
    previous_output = step_input.get_step_output("excel_separation_step")
    if not previous_output:
        raise ValueError("Previous Excel separation step output not found")
    
    separation_data = json.loads(previous_output.content)
    
    logger.info("Executing survey data analysis step...")
    
    try:
        # Import survey analysis functions
        from ai.agents.survey_data_analyzer_agent.agent import (
            identify_survey_columns,
            extract_survey_responses,
            generate_survey_summary
        )
        
        # Step 1: Identify survey columns
        logger.info("🔍 Identifying survey columns...")
        separated_excel_data = separation_data.get("separated_data", {})
        survey_columns = identify_survey_columns(separated_excel_data)
        
        if not survey_columns:
            logger.warning("No survey columns found in the data")
            analysis_results = {
                "step": "survey_data_analysis",
                "status": "no_survey_data",
                "message": "No survey columns identified in the Excel data",
                "survey_columns_found": 0,
                "processing_timestamp": datetime.now().isoformat()
            }
        else:
            logger.info(f"📊 Found {len(survey_columns)} survey columns: {survey_columns}")
            
            # Step 2: Extract and analyze survey responses
            logger.info("📋 Extracting survey responses...")
            survey_data = extract_survey_responses(separated_excel_data, survey_columns)
            
            # Step 3: Generate summary
            logger.info("📈 Generating survey summary...")
            survey_summary = generate_survey_summary(survey_data)
            
            # Prepare analysis results
            analysis_results = {
                "step": "survey_data_analysis",
                "status": "completed",
                "survey_columns_found": len(survey_columns),
                "survey_columns": survey_columns,
                "survey_data": survey_data,
                "survey_summary": survey_summary,
                "processing_timestamp": datetime.now().isoformat(),
                "ready_for_charts": True,
                "chart_data_prepared": True
            }
            
            # Log summary
            questions_analyzed = len(survey_data.get("survey_questions", {}))
            avg_response_rate = survey_summary.get("overview", {}).get("avg_response_rate", 0)
            
            summary_log = (
                f"Survey data analysis completed:\n"
                f"- Survey columns found: {len(survey_columns)}\n"
                f"- Questions analyzed: {questions_analyzed}\n"
                f"- Average response rate: {avg_response_rate:.1f}%\n"
                f"- Chart recommendations: {len(survey_summary.get('visualization_recommendations', []))}"
            )
            logger.info(summary_log)
        
        return StepOutput(content=json.dumps(analysis_results, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "step": "survey_data_analysis",
            "status": "error",
            "error": str(e),
            "processing_timestamp": datetime.now().isoformat()
        }
        logger.error(f"Survey data analysis failed: {str(e)}")
        return StepOutput(content=json.dumps(error_result, ensure_ascii=False, indent=2))


def execute_report_generation_step(step_input: StepInput) -> StepOutput:
    """
    Execute HTML report generation step using the HTML Report Generator Agent
    
    Args:
        step_input: Input containing analysis results from previous step
        
    Returns:
        StepOutput with HTML report generation results
    """
    # Get analysis results from previous step
    previous_output = step_input.get_step_output("data_analysis_step")
    if not previous_output:
        raise ValueError("Previous data analysis step output not found")
    
    analysis_data = json.loads(previous_output.content)
    
    logger.info("Executing HTML report generation step...")
    
    try:
        # Import HTML report generation functions
        from ai.agents.html_report_generator_agent.agent import (
            generate_html_report,
            save_html_report
        )
        
        # Get original separation data for file info
        separation_output = step_input.get_step_output("excel_separation_step")
        separation_data = json.loads(separation_output.content) if separation_output else {}
        file_info = separation_data.get("file_info", {})
        
        # Check if we have survey data to generate report
        if analysis_data.get("status") == "completed" and analysis_data.get("survey_data"):
            logger.info("📄 Generating HTML report...")
            
            # Extract survey data
            survey_data = analysis_data.get("survey_data", {})
            
            # Generate HTML report
            html_content = generate_html_report(survey_data, file_info)
            
            # Save HTML report
            report_filename = save_html_report(html_content)
            
            # Generate final report results
            final_report = {
                "step": "html_report_generation",
                "status": "completed",
                "html_report_generated": True,
                "report_filename": report_filename,
                "report_size_kb": len(html_content) / 1024,
                "workflow_summary": {
                    "total_steps_executed": 3,
                    "excel_processing_status": separation_data.get("status", "unknown"),
                    "survey_analysis_status": analysis_data.get("status", "unknown"),
                    "html_report_status": "completed",
                    "final_status": "workflow_completed_with_html_report"
                },
                "file_info": file_info,
                "survey_summary": analysis_data.get("survey_summary", {}),
                "processing_timestamp": datetime.now().isoformat(),
                "stakeholder_ready": True,
                "next_steps": [
                    f"Abrir relatório HTML: {report_filename}",
                    "Compartilhar relatório com stakeholders",
                    "Usar insights para tomada de decisões",
                    "Planejar próximas pesquisas baseadas nos resultados"
                ]
            }
            
            logger.info(f"📊 HTML report generated successfully: {report_filename}")
            
        else:
            # No survey data available for report generation
            final_report = {
                "step": "html_report_generation",
                "status": "skipped",
                "html_report_generated": False,
                "reason": "No survey data available for report generation",
                "workflow_summary": {
                    "total_steps_executed": 3,
                    "excel_processing_status": separation_data.get("status", "unknown"),
                    "survey_analysis_status": analysis_data.get("status", "unknown"),
                    "html_report_status": "skipped",
                    "final_status": "workflow_completed_no_report"
                },
                "processing_timestamp": datetime.now().isoformat(),
                "next_steps": [
                    "Verificar se há dados de pesquisa válidos",
                    "Executar análise de dados novamente se necessário"
                ]
            }
            
            logger.warning("HTML report generation skipped - no survey data available")
        
        return StepOutput(content=json.dumps(final_report, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "step": "html_report_generation",
            "status": "error",
            "error": str(e),
            "processing_timestamp": datetime.now().isoformat()
        }
        logger.error(f"HTML report generation failed: {str(e)}")
        return StepOutput(content=json.dumps(error_result, ensure_ascii=False, indent=2))


# Factory function to create workflow
def get_excel_processing_workflow_workflow(**kwargs) -> Workflow:
    """Factory function to create Excel processing workflow"""
    
    # Create workflow with step-based architecture
    workflow = Workflow(
        name="excel_processing_workflow",
        description="Workflow for comprehensive Excel file processing with separation, analysis, and reporting",
        steps=[
            Step(
                name="excel_separation_step",
                description="Read and separate Excel file data into structured format",
                executor=execute_excel_separation_step,
                max_retries=2
            ),
            Step(
                name="data_analysis_step",
                description="Analyze survey data and prepare for chart generation",
                executor=execute_data_analysis_step,
                max_retries=2
            ),
            Step(
                name="report_generation_step",
                description="Generate professional HTML report for stakeholders",
                executor=execute_report_generation_step,
                max_retries=1
            )
        ],
        **kwargs
    )
    
    logger.info("Excel Processing Workflow initialized successfully")
    return workflow


# For backward compatibility and direct testing
excel_processing_workflow = get_excel_processing_workflow_workflow()


if __name__ == "__main__":
    # Test the workflow
    import asyncio
    
    async def test_excel_processing_workflow():
        """Test Excel processing workflow execution"""
        
        # Example test with a sample Excel file path
        test_file_path = "/path/to/your/test/file.xlsx"
        
        test_input = f"file_path: {test_file_path}"
        
        # Create workflow instance
        workflow = get_excel_processing_workflow_workflow()
        
        logger.info("Testing Excel processing workflow...")
        logger.info(f"🤖 Test file: {test_file_path}")
        
        try:
            # Run workflow
            result = await workflow.arun(message=test_input.strip())
            
            logger.info("Excel processing workflow execution completed:")
            logger.info(f"🤖 {result.content if hasattr(result, 'content') else result}")
            
        except Exception as e:
            logger.error(f"Workflow test failed: {str(e)}")
    
    # Uncomment to run test (make sure to provide a valid Excel file path)
    # asyncio.run(test_excel_processing_workflow()) 