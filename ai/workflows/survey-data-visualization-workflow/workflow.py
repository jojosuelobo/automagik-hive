"""
Survey Data Visualization Workflow - Agno Workflows 2.0 Implementation
======================================================================

Comprehensive automated survey data analysis and visualization pipeline
using Agno Workflows 2.0 step-based architecture with parallel processing
and professional dashboard generation.
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

from agno.workflow.v2 import Workflow, Step, Parallel
from agno.workflow.v2.types import StepInput, StepOutput
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.storage.postgres import PostgresStorage
from lib.logging import logger

# Import our specialized agents - using dynamic imports to avoid path issues
import importlib.util
import sys

def import_agent_dynamically(agent_name: str, function_name: str):
    """Dynamically import agent factory function"""
    agent_path = Path(f"ai/agents/{agent_name}/agent.py")
    spec = importlib.util.spec_from_file_location(f"ai.agents.{agent_name}.agent", agent_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"ai.agents.{agent_name}.agent"] = module
    spec.loader.exec_module(module)
    return getattr(module, function_name)


def create_survey_workflow_model() -> Claude:
    """Create Claude model for survey workflow coordination"""
    return Claude(
        id='claude-sonnet-4-20250514',
        temperature=0.1,
        max_tokens=4000
    )


def execute_excel_processing_step(step_input: StepInput) -> StepOutput:
    """
    Execute Excel data processing step - extract and validate survey data
    
    Args:
        step_input: Workflow step input containing file path or data
        
    Returns:
        StepOutput with processed survey data
    """
    try:
        logger.info("🔄 Starting Excel data processing step...")
        
        # Extract input parameters
        input_message = step_input.message
        file_path = None
        
        # Try to extract file path from message
        if "file_path" in input_message:
            # Extract file path if provided in structured format
            import re
            path_match = re.search(r'file_path[:\s]*["\']([^"\']+)["\']', input_message)
            if path_match:
                file_path = path_match.group(1)
        
        # Create Excel processor agent using dynamic import
        get_excel_data_processor_agent = import_agent_dynamically(
            "excel-data-processor-agent", 
            "get_excel_data_processor_agent"
        )
        excel_processor = get_excel_data_processor_agent(
            session_id=step_input.workflow_session_state.get("session_id"),
            debug_mode=step_input.workflow_session_state.get("debug_mode", False)
        )
        
        # Process the Excel file
        if file_path:
            processing_query = f"""
            Please process the Excel file at: {file_path}
            
            Extract all columns that contain 'pesquisa' in their name and provide:
            1. Filtered dataset with only survey columns
            2. Data quality validation report
            3. Column metadata and statistics
            4. Processing summary
            
            Focus specifically on columns matching patterns like:
            - pesquisa300625_screen0
            - pesquisa300625_screen1
            - etc.
            """
        else:
            # If no file path provided, use the message as-is
            processing_query = f"""
            {input_message}
            
            Please extract survey data columns containing 'pesquisa' pattern and provide:
            1. Filtered dataset
            2. Data quality validation
            3. Processing statistics
            """
        
        # Run Excel processing
        response = excel_processor.run(processing_query)
        
        if not response.content:
            raise ValueError("Excel processing agent returned empty response")
        
        # Store processing results in session state
        step_input.workflow_session_state["excel_processing_results"] = {
            "response": str(response.content),
            "processing_timestamp": datetime.now().isoformat(),
            "agent_used": "excel-data-processor-agent"
        }
        
        # Create structured output
        processing_summary = {
            "step": "excel_processing",
            "status": "completed",
            "results": str(response.content),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("✅ Excel data processing completed successfully")
        return StepOutput(content=json.dumps(processing_summary))
        
    except Exception as e:
        logger.error(f"❌ Excel processing step failed: {str(e)}")
        error_output = {
            "step": "excel_processing",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        return StepOutput(content=json.dumps(error_output))


def execute_data_classification_step(step_input: StepInput) -> StepOutput:
    """
    Execute data type classification step - analyze and classify survey columns
    
    Args:
        step_input: Workflow step input with processed Excel data
        
    Returns:
        StepOutput with data type classifications
    """
    try:
        logger.info("🔄 Starting data type classification step...")
        
        # Get previous step results
        excel_results = step_input.workflow_session_state.get("excel_processing_results", {})
        
        if not excel_results:
            raise ValueError("No Excel processing results found in session state")
        
        # Create data type classifier agent using dynamic import
        get_data_type_classifier_agent = import_agent_dynamically(
            "data-type-classifier-agent",
            "get_data_type_classifier_agent"
        )
        classifier_agent = get_data_type_classifier_agent(
            session_id=step_input.workflow_session_state.get("session_id"),
            debug_mode=step_input.workflow_session_state.get("debug_mode", False)
        )
        
        # Prepare classification query
        classification_query = f"""
        Based on the Excel processing results below, please classify the data types for each survey column:
        
        {excel_results.get('response', 'No processing results available')}
        
        For each column containing 'pesquisa', determine:
        1. Primary data type (categorical, numerical, temporal, textual)
        2. Sub-type classification (e.g., ordinal, binary, continuous)
        3. Confidence score for the classification
        4. Recommended visualization types
        5. Statistical characteristics
        
        Provide detailed reasoning for each classification decision.
        """
        
        # Run classification
        response = classifier_agent.run(classification_query)
        
        if not response.content:
            raise ValueError("Data classifier agent returned empty response")
        
        # Store classification results in session state
        step_input.workflow_session_state["classification_results"] = {
            "response": str(response.content),
            "classification_timestamp": datetime.now().isoformat(),
            "agent_used": "data-type-classifier-agent"
        }
        
        # Create structured output
        classification_summary = {
            "step": "data_classification",
            "status": "completed",
            "results": str(response.content),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("✅ Data type classification completed successfully")
        return StepOutput(content=json.dumps(classification_summary))
        
    except Exception as e:
        logger.error(f"❌ Data classification step failed: {str(e)}")
        error_output = {
            "step": "data_classification",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        return StepOutput(content=json.dumps(error_output))


def execute_visualization_generation_step(step_input: StepInput) -> StepOutput:
    """
    Execute visualization generation step - create professional charts
    
    Args:
        step_input: Workflow step input with classification results
        
    Returns:
        StepOutput with generated visualizations
    """
    try:
        logger.info("🔄 Starting visualization generation step...")
        
        # Get previous step results
        excel_results = step_input.workflow_session_state.get("excel_processing_results", {})
        classification_results = step_input.workflow_session_state.get("classification_results", {})
        
        if not excel_results or not classification_results:
            raise ValueError("Missing Excel processing or classification results")
        
        # Create visualization generator agent using dynamic import
        get_visualization_generator_agent = import_agent_dynamically(
            "visualization-generator-agent",
            "get_visualization_generator_agent"
        )
        viz_agent = get_visualization_generator_agent(
            session_id=step_input.workflow_session_state.get("session_id"),
            debug_mode=step_input.workflow_session_state.get("debug_mode", False)
        )
        
        # Prepare visualization query
        visualization_query = f"""
        Based on the Excel processing and data classification results below, please generate professional visualizations:
        
        Excel Processing Results:
        {excel_results.get('response', 'No processing results')}
        
        Data Classification Results:
        {classification_results.get('response', 'No classification results')}
        
        Please create appropriate charts for each survey column:
        1. Select optimal chart types based on data classification
        2. Apply professional styling and color schemes
        3. Generate interactive features where appropriate
        4. Export charts in multiple formats (PNG, HTML)
        5. Provide chart metadata and descriptions
        
        Ensure all visualizations are stakeholder-ready and presentation-quality.
        """
        
        # Run visualization generation
        response = viz_agent.run(visualization_query)
        
        if not response.content:
            raise ValueError("Visualization generator agent returned empty response")
        
        # Store visualization results in session state
        step_input.workflow_session_state["visualization_results"] = {
            "response": str(response.content),
            "visualization_timestamp": datetime.now().isoformat(),
            "agent_used": "visualization-generator-agent"
        }
        
        # Create structured output
        visualization_summary = {
            "step": "visualization_generation",
            "status": "completed",
            "results": str(response.content),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("✅ Visualization generation completed successfully")
        return StepOutput(content=json.dumps(visualization_summary))
        
    except Exception as e:
        logger.error(f"❌ Visualization generation step failed: {str(e)}")
        error_output = {
            "step": "visualization_generation",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        return StepOutput(content=json.dumps(error_output))


def execute_dashboard_assembly_step(step_input: StepInput) -> StepOutput:
    """
    Execute dashboard assembly step - compile final dashboard and reports
    
    Args:
        step_input: Workflow step input with all previous results
        
    Returns:
        StepOutput with final dashboard and reports
    """
    try:
        logger.info("🔄 Starting dashboard assembly step...")
        
        # Get all previous step results
        excel_results = step_input.workflow_session_state.get("excel_processing_results", {})
        classification_results = step_input.workflow_session_state.get("classification_results", {})
        visualization_results = step_input.workflow_session_state.get("visualization_results", {})
        
        if not all([excel_results, classification_results, visualization_results]):
            raise ValueError("Missing results from previous workflow steps")
        
        # Create dashboard builder agent using dynamic import
        get_dashboard_builder_agent = import_agent_dynamically(
            "dashboard-builder-agent",
            "get_dashboard_builder_agent"
        )
        dashboard_agent = get_dashboard_builder_agent(
            session_id=step_input.workflow_session_state.get("session_id"),
            debug_mode=step_input.workflow_session_state.get("debug_mode", False)
        )
        
        # Prepare dashboard assembly query
        dashboard_query = f"""
        Please compile a comprehensive dashboard and executive report from the survey analysis results:
        
        Excel Processing Results:
        {excel_results.get('response', 'No processing results')}
        
        Data Classification Results:
        {classification_results.get('response', 'No classification results')}
        
        Visualization Results:
        {visualization_results.get('response', 'No visualization results')}
        
        Create the following deliverables:
        1. Interactive HTML dashboard with all visualizations
        2. Executive summary with key insights and recommendations
        3. Professional PDF report for stakeholders
        4. Data quality assessment and methodology notes
        5. Actionable business recommendations with priorities
        
        Ensure all outputs are professional, stakeholder-ready, and provide clear value.
        """
        
        # Run dashboard assembly
        response = dashboard_agent.run(dashboard_query)
        
        if not response.content:
            raise ValueError("Dashboard builder agent returned empty response")
        
        # Store final results in session state
        step_input.workflow_session_state["dashboard_results"] = {
            "response": str(response.content),
            "dashboard_timestamp": datetime.now().isoformat(),
            "agent_used": "dashboard-builder-agent"
        }
        
        # Create comprehensive workflow summary
        workflow_summary = {
            "workflow": "survey-data-visualization",
            "status": "completed",
            "completion_timestamp": datetime.now().isoformat(),
            "steps_completed": [
                "excel_processing",
                "data_classification", 
                "visualization_generation",
                "dashboard_assembly"
            ],
            "final_deliverables": {
                "interactive_dashboard": "HTML dashboard with visualizations",
                "executive_report": "Professional PDF with insights",
                "data_analysis": "Complete statistical analysis",
                "recommendations": "Actionable business recommendations"
            },
            "dashboard_results": str(response.content),
            "session_data": {
                "excel_processing": excel_results,
                "classification": classification_results,
                "visualization": visualization_results
            }
        }
        
        logger.info("✅ Survey data visualization workflow completed successfully")
        return StepOutput(content=json.dumps(workflow_summary))
        
    except Exception as e:
        logger.error(f"❌ Dashboard assembly step failed: {str(e)}")
        error_output = {
            "step": "dashboard_assembly",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        return StepOutput(content=json.dumps(error_output))


def get_survey_data_visualization_workflow(**kwargs) -> Workflow:
    """
    Factory function to create survey data visualization workflow
    
    Args:
        **kwargs: Additional workflow configuration parameters
        
    Returns:
        Configured Agno Workflows 2.0 workflow instance
    """
    # Load workflow configuration
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Create workflow with step-based architecture
    workflow = Workflow(
        name="survey_data_visualization",
        description="Automated survey data analysis and visualization pipeline with professional dashboard generation",
        steps=[
            Step(
                name="excel_processing_step",
                description="Extract and validate survey data from XLSX files",
                function=execute_excel_processing_step,
                max_retries=3
            ),
            Step(
                name="data_classification_step",
                description="Classify data types and analyze survey column characteristics",
                function=execute_data_classification_step,
                max_retries=3
            ),
            Step(
                name="visualization_generation_step",
                description="Generate professional charts and visualizations",
                function=execute_visualization_generation_step,
                max_retries=3
            ),
            Step(
                name="dashboard_assembly_step",
                description="Compile dashboard, reports, and executive insights",
                function=execute_dashboard_assembly_step,
                max_retries=2
            )
        ],
        # Use storage configuration from config file
        storage=PostgresStorage(
            table_name=config["storage"]["table_name"],
            auto_upgrade_schema=config["storage"]["auto_upgrade_schema"]
        ) if not kwargs.get('storage') else kwargs['storage'],
        # Apply other configurations
        **{k: v for k, v in kwargs.items() if k != 'storage'}
    )
    
    logger.info("🚀 Survey Data Visualization Workflow initialized successfully")
    return workflow


# For backward compatibility and direct testing
survey_data_visualization_workflow = get_survey_data_visualization_workflow()


if __name__ == "__main__":
    # Test the workflow
    import asyncio
    
    async def test_survey_workflow():
        """Test survey data visualization workflow"""
        
        test_input = """
        Please process survey data with the following structure:
        
        Sample XLSX file contains columns:
        - First name
        - Number 1
        - Email 1
        - pesquisa300625_screen0: Rating scale 1-5
        - pesquisa300625_screen1: Yes/No responses
        - pesquisa300625_screen2: Open-ended text feedback
        - pesquisa300625_screen3: Multiple choice A/B/C/D
        - pesquisa300625_screen4: Satisfaction rating (Very Poor to Excellent)
        
        Please extract the 'pesquisa' columns, classify their data types, generate appropriate visualizations, and create a professional dashboard with executive insights.
        """
        
        # Create workflow instance with test configuration
        workflow = get_survey_data_visualization_workflow(
            session_id=f"test-session-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        logger.info("Testing survey data visualization workflow...")
        logger.info(f"🔬 Input: Survey analysis for multiple question types")
        
        # Run workflow
        result = await workflow.arun(
            message=test_input.strip(),
            stream=True,
            stream_intermediate_steps=True
        )
        
        logger.info("Survey workflow execution completed:")
        logger.info(f"🎯 {result.content if hasattr(result, 'content') else result}")
        
    # Run test
    asyncio.run(test_survey_workflow())