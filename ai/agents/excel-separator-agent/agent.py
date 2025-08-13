"""
Excel Separator Agent - Specialized Excel File Processing
========================================================

This agent handles Excel file reading, column separation, and data structuring
for the Excel processing workflow.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from lib.logging import logger
from lib.utils.version_factory import create_agent


def read_excel_file(file_path: str) -> Dict[str, Any]:
    """
    Read Excel file and extract basic information
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Dictionary with file information and basic structure
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Extract basic information
        file_info = {
            "file_path": file_path,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "file_size_mb": Path(file_path).stat().st_size / (1024 * 1024),
            "processed_at": datetime.now().isoformat()
        }
        
        logger.info(f"Excel file read successfully: {file_info['total_rows']} rows, {file_info['total_columns']} columns")
        return file_info
        
    except Exception as e:
        logger.error(f"Error reading Excel file: {str(e)}")
        raise


def separate_columns_data(file_path: str) -> Dict[str, Any]:
    """
    Separate and structure column data from Excel file
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Dictionary with separated column data and metadata
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Process each column
        separated_data = {
            "columns": {},
            "metadata": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "processed_at": datetime.now().isoformat(),
                "file_path": file_path
            }
        }
        
        for column in df.columns:
            column_data = df[column]
            
            # Determine column type
            if pd.api.types.is_numeric_dtype(column_data):
                col_type = "numeric"
            elif pd.api.types.is_datetime64_any_dtype(column_data):
                col_type = "datetime"
            else:
                col_type = "text"
            
            # Extract column information
            separated_data["columns"][column] = {
                "data": column_data.fillna("").tolist(),  # Replace NaN with empty string
                "type": col_type,
                "non_null_count": column_data.count(),
                "null_count": column_data.isnull().sum(),
                "unique_values": column_data.nunique(),
                "sample_values": column_data.dropna().head(5).tolist()
            }
            
            # Add type-specific metadata
            if col_type == "numeric":
                separated_data["columns"][column].update({
                    "min_value": float(column_data.min()) if not column_data.empty else None,
                    "max_value": float(column_data.max()) if not column_data.empty else None,
                    "mean_value": float(column_data.mean()) if not column_data.empty else None
                })
            elif col_type == "text":
                separated_data["columns"][column].update({
                    "avg_length": column_data.astype(str).str.len().mean() if not column_data.empty else 0,
                    "max_length": column_data.astype(str).str.len().max() if not column_data.empty else 0
                })
        
        logger.info(f"Column separation completed: {len(separated_data['columns'])} columns processed")
        return separated_data
        
    except Exception as e:
        logger.error(f"Error separating columns: {str(e)}")
        raise


def validate_excel_data(separated_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the separated Excel data
    
    Args:
        separated_data: The separated column data
        
    Returns:
        Validation report
    """
    validation_report = {
        "is_valid": True,
        "issues": [],
        "warnings": [],
        "summary": {},
        "validated_at": datetime.now().isoformat()
    }
    
    try:
        total_rows = separated_data["metadata"]["total_rows"]
        columns = separated_data["columns"]
        
        # Check for empty columns
        empty_columns = [col for col, data in columns.items() if data["non_null_count"] == 0]
        if empty_columns:
            validation_report["warnings"].append(f"Empty columns found: {empty_columns}")
        
        # Check for columns with high null percentage
        high_null_columns = []
        for col, data in columns.items():
            null_percentage = (data["null_count"] / total_rows) * 100
            if null_percentage > 50:
                high_null_columns.append(f"{col} ({null_percentage:.1f}% null)")
        
        if high_null_columns:
            validation_report["warnings"].append(f"Columns with high null percentage: {high_null_columns}")
        
        # Check data consistency
        for col, data in columns.items():
            if data["type"] == "numeric" and data["non_null_count"] > 0:
                if data["min_value"] is None or data["max_value"] is None:
                    validation_report["issues"].append(f"Numeric column {col} has invalid min/max values")
        
        # Generate summary
        validation_report["summary"] = {
            "total_columns": len(columns),
            "numeric_columns": len([c for c in columns.values() if c["type"] == "numeric"]),
            "text_columns": len([c for c in columns.values() if c["type"] == "text"]),
            "datetime_columns": len([c for c in columns.values() if c["type"] == "datetime"]),
            "empty_columns": len(empty_columns),
            "total_issues": len(validation_report["issues"]),
            "total_warnings": len(validation_report["warnings"])
        }
        
        if validation_report["issues"]:
            validation_report["is_valid"] = False
        
        logger.info(f"Data validation completed: {validation_report['summary']}")
        return validation_report
        
    except Exception as e:
        logger.error(f"Error validating data: {str(e)}")
        validation_report["is_valid"] = False
        validation_report["issues"].append(f"Validation error: {str(e)}")
        return validation_report


# Agent factory function
async def get_excel_separator_agent(**kwargs):
    """Factory function to create Excel separator agent"""
    return await create_agent("excel-separator-agent", **kwargs) 