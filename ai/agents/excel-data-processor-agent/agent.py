"""
Excel Data Processor Agent - Survey Data Extraction Specialist
=============================================================

Advanced Excel data processor for survey data extraction, column filtering,
and data quality validation. Specializes in "pesquisa*" pattern recognition
and XLSX file handling with robust error handling.
"""

import pandas as pd
import openpyxl
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import yaml
import json
import re
from datetime import datetime

from agno import Agent
from agno.models.anthropic import Claude
from agno.storage.postgres import PostgresStorage
from lib.logging import logger


def create_excel_processor_model() -> Claude:
    """Create Claude model for Excel data processing"""
    return Claude(
        id='claude-sonnet-4-20250514',
        temperature=0.1,
        max_tokens=4000
    )


def process_xlsx_file(file_path: str, column_pattern: str = "pesquisa") -> Dict[str, Any]:
    """
    Process XLSX file and extract columns matching the pattern
    
    Args:
        file_path: Path to the XLSX file
        column_pattern: Pattern to match columns (default: "pesquisa")
        
    Returns:
        Dictionary containing processed data and metadata
    """
    try:
        # Load the Excel file
        df = pd.read_excel(file_path)
        logger.info(f"📊 Loaded XLSX file: {len(df)} rows, {len(df.columns)} columns")
        
        # Filter columns containing the pattern
        pattern_columns = [col for col in df.columns if column_pattern.lower() in str(col).lower()]
        
        if not pattern_columns:
            raise ValueError(f"No columns found containing pattern '{column_pattern}'")
        
        logger.info(f"🔍 Found {len(pattern_columns)} columns matching pattern '{column_pattern}'")
        
        # Extract filtered dataset
        filtered_df = df[pattern_columns].copy()
        
        # Generate metadata for each column
        column_metadata = {}
        for col in pattern_columns:
            metadata = {
                "column_name": col,
                "data_type": str(filtered_df[col].dtype),
                "null_count": int(filtered_df[col].isnull().sum()),
                "unique_count": int(filtered_df[col].nunique()),
                "sample_values": filtered_df[col].dropna().head(5).tolist(),
                "null_percentage": float(filtered_df[col].isnull().sum() / len(filtered_df) * 100)
            }
            column_metadata[col] = metadata
        
        # Generate processing statistics
        processing_stats = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "filtered_columns_count": len(pattern_columns),
            "filtered_columns": pattern_columns,
            "processing_timestamp": datetime.now().isoformat(),
            "file_name": Path(file_path).name
        }
        
        # Data quality assessment
        quality_assessment = {
            "overall_completeness": float((filtered_df.notna().sum().sum()) / (len(filtered_df) * len(pattern_columns)) * 100),
            "columns_with_missing_data": [col for col, meta in column_metadata.items() if meta["null_count"] > 0],
            "high_missing_columns": [col for col, meta in column_metadata.items() if meta["null_percentage"] > 50],
            "data_quality_score": "excellent" if all(meta["null_percentage"] < 10 for meta in column_metadata.values()) else "good" if all(meta["null_percentage"] < 30 for meta in column_metadata.values()) else "needs_attention"
        }
        
        return {
            "success": True,
            "filtered_data": filtered_df.to_dict('records'),
            "column_metadata": column_metadata,
            "processing_stats": processing_stats,
            "quality_assessment": quality_assessment,
            "original_columns": list(df.columns)
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing XLSX file: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "processing_timestamp": datetime.now().isoformat()
        }


def validate_survey_data_structure(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the structure and quality of survey data
    
    Args:
        data: Processed data dictionary from process_xlsx_file
        
    Returns:
        Validation results and recommendations
    """
    if not data.get("success"):
        return {
            "validation_passed": False,
            "error": "Cannot validate failed data processing",
            "recommendations": ["Fix data processing errors first"]
        }
    
    validation_results = {
        "validation_passed": True,
        "checks_performed": [],
        "warnings": [],
        "recommendations": [],
        "validation_timestamp": datetime.now().isoformat()
    }
    
    # Check minimum data threshold
    if data["processing_stats"]["total_rows"] < 10:
        validation_results["warnings"].append("Dataset has fewer than 10 rows - results may not be statistically meaningful")
        validation_results["recommendations"].append("Consider collecting more survey responses")
    
    # Check for high missing data
    high_missing = data["quality_assessment"]["high_missing_columns"]
    if high_missing:
        validation_results["warnings"].append(f"Columns with >50% missing data: {', '.join(high_missing)}")
        validation_results["recommendations"].append("Review data collection process for incomplete responses")
    
    # Check data quality score
    quality_score = data["quality_assessment"]["data_quality_score"]
    if quality_score == "needs_attention":
        validation_results["warnings"].append("Overall data quality needs attention")
        validation_results["recommendations"].append("Implement data quality improvements before visualization")
    
    validation_results["checks_performed"] = [
        "minimum_data_threshold",
        "missing_data_analysis", 
        "data_quality_scoring"
    ]
    
    return validation_results


def get_excel_data_processor_agent(
    version: Optional[int] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = False,
    db_url: Optional[str] = None
) -> Agent:
    """Excel data processor agent factory function"""
    
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Create agent with tools
    agent = Agent(
        name=config["agent"]["name"],
        agent_id=config["agent"]["agent_id"],
        instructions=config["instructions"],
        model=create_excel_processor_model(),
        storage=PostgresStorage(
            table_name=config["storage"]["table_name"],
            db_url=db_url,
            auto_upgrade_schema=config["storage"]["auto_upgrade_schema"]
        ),
        session_id=session_id,
        debug_mode=debug_mode,
        markdown=config.get("markdown", False),
        show_tool_calls=config.get("show_tool_calls", False)
    )
    
    # Add custom tools
    agent.tools.append(process_xlsx_file)
    agent.tools.append(validate_survey_data_structure)
    
    logger.info(f"📊 Excel Data Processor Agent initialized - Version {config['agent']['version']}")
    return agent


# Export the factory function
__all__ = ["get_excel_data_processor_agent", "process_xlsx_file", "validate_survey_data_structure"]


if __name__ == "__main__":
    # Test the agent
    import asyncio
    
    async def test_excel_processor():
        """Test Excel data processor agent"""
        agent = get_excel_data_processor_agent(debug_mode=True)
        
        test_message = """
        I need you to process a survey XLSX file and extract all columns that contain 'pesquisa' in their name.
        The file has columns like:
        - First name
        - Number 1  
        - Email 1
        - pesquisa300625_screen0
        - pesquisa300625_screen1
        - pesquisa300625_screen2
        - ...
        - pesquisa300625_screen9
        
        Please filter and extract only the 'pesquisa' columns and provide data quality analysis.
        """
        
        logger.info("Testing Excel data processor agent...")
        response = await agent.arun(test_message)
        logger.info(f"🤖 Response: {response.content}")
    
    # Run test
    asyncio.run(test_excel_processor())