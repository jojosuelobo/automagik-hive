"""
Excel Data Processor Tools - Survey Data Processing Utilities
============================================================

Collection of utility functions for Excel data processing, column filtering,
and data quality validation for survey data analysis workflows.
"""

import pandas as pd
import openpyxl
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import re
import io
import base64
from datetime import datetime
import json

from lib.logging import logger


def detect_column_patterns(columns: List[str], patterns: List[str] = None) -> Dict[str, List[str]]:
    """
    Detect column patterns in dataset
    
    Args:
        columns: List of column names
        patterns: List of patterns to search for (default: ["pesquisa", "survey", "screen"])
        
    Returns:
        Dictionary mapping patterns to matching columns
    """
    if patterns is None:
        patterns = ["pesquisa", "survey", "screen"]
    
    pattern_matches = {}
    
    for pattern in patterns:
        matches = []
        for col in columns:
            if re.search(pattern, str(col), re.IGNORECASE):
                matches.append(col)
        pattern_matches[pattern] = matches
    
    logger.info(f"🔍 Pattern detection completed: {len(pattern_matches)} patterns analyzed")
    return pattern_matches


def analyze_data_completeness(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze data completeness and missing value patterns
    
    Args:
        df: Input DataFrame
        
    Returns:
        Completeness analysis results
    """
    total_cells = len(df) * len(df.columns)
    missing_cells = df.isnull().sum().sum()
    
    completeness_by_column = {}
    for col in df.columns:
        null_count = df[col].isnull().sum()
        null_percentage = (null_count / len(df)) * 100
        completeness_by_column[col] = {
            "null_count": int(null_count),
            "null_percentage": float(null_percentage),
            "completeness": float(100 - null_percentage)
        }
    
    analysis = {
        "overall_completeness": float(((total_cells - missing_cells) / total_cells) * 100),
        "total_cells": total_cells,
        "missing_cells": int(missing_cells),
        "columns_analysis": completeness_by_column,
        "complete_columns": [col for col, stats in completeness_by_column.items() if stats["null_count"] == 0],
        "incomplete_columns": [col for col, stats in completeness_by_column.items() if stats["null_count"] > 0],
        "high_missing_columns": [col for col, stats in completeness_by_column.items() if stats["null_percentage"] > 50]
    }
    
    logger.info(f"📊 Data completeness analysis: {analysis['overall_completeness']:.1f}% complete")
    return analysis


def extract_column_sample_data(df: pd.DataFrame, sample_size: int = 10) -> Dict[str, Any]:
    """
    Extract sample data from each column for analysis
    
    Args:
        df: Input DataFrame
        sample_size: Number of sample values to extract per column
        
    Returns:
        Dictionary with sample data for each column
    """
    column_samples = {}
    
    for col in df.columns:
        # Get non-null values for sampling
        non_null_values = df[col].dropna()
        
        if len(non_null_values) == 0:
            sample_data = {
                "sample_values": [],
                "data_type": "unknown",
                "unique_count": 0,
                "is_numeric": False,
                "is_categorical": False,
                "has_text": False
            }
        else:
            # Extract sample values
            sample_values = non_null_values.head(sample_size).tolist()
            
            # Analyze data characteristics
            unique_count = non_null_values.nunique()
            
            # Check if numeric
            is_numeric = pd.api.types.is_numeric_dtype(non_null_values)
            
            # Check if likely categorical (low unique count relative to total)
            is_categorical = unique_count <= min(20, len(non_null_values) * 0.1)
            
            # Check if contains text
            has_text = any(isinstance(val, str) and len(str(val)) > 10 for val in sample_values)
            
            sample_data = {
                "sample_values": sample_values,
                "data_type": str(df[col].dtype),
                "unique_count": int(unique_count),
                "is_numeric": is_numeric,
                "is_categorical": is_categorical,
                "has_text": has_text,
                "total_non_null": int(len(non_null_values))
            }
        
        column_samples[col] = sample_data
    
    logger.info(f"📋 Column sampling completed for {len(column_samples)} columns")
    return column_samples


def validate_xlsx_structure(file_path: str) -> Dict[str, Any]:
    """
    Validate XLSX file structure and readability
    
    Args:
        file_path: Path to XLSX file
        
    Returns:
        Validation results
    """
    validation_results = {
        "is_valid": False,
        "error": None,
        "sheet_info": {},
        "file_info": {},
        "validation_timestamp": datetime.now().isoformat()
    }
    
    try:
        # Check file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file info
        file_path_obj = Path(file_path)
        validation_results["file_info"] = {
            "file_name": file_path_obj.name,
            "file_size": file_path_obj.stat().st_size,
            "file_extension": file_path_obj.suffix.lower()
        }
        
        # Validate file extension
        if validation_results["file_info"]["file_extension"] not in [".xlsx", ".xls"]:
            raise ValueError(f"Unsupported file format: {validation_results['file_info']['file_extension']}")
        
        # Try to open with openpyxl first
        try:
            workbook = openpyxl.load_workbook(file_path, read_only=True)
            sheet_names = workbook.sheetnames
            
            validation_results["sheet_info"] = {
                "sheet_count": len(sheet_names),
                "sheet_names": sheet_names,
                "active_sheet": sheet_names[0] if sheet_names else None
            }
            
            workbook.close()
            
        except Exception as openpyxl_error:
            logger.warning(f"⚠️ openpyxl failed, trying pandas: {str(openpyxl_error)}")
            
            # Fallback to pandas
            df = pd.read_excel(file_path)
            validation_results["sheet_info"] = {
                "sheet_count": 1,
                "sheet_names": ["default"],
                "active_sheet": "default",
                "fallback_method": "pandas"
            }
        
        validation_results["is_valid"] = True
        logger.info(f"✅ XLSX validation successful: {validation_results['file_info']['file_name']}")
        
    except Exception as e:
        validation_results["error"] = str(e)
        validation_results["error_type"] = type(e).__name__
        logger.error(f"❌ XLSX validation failed: {str(e)}")
    
    return validation_results


def clean_column_names(columns: List[str]) -> Dict[str, str]:
    """
    Clean and standardize column names
    
    Args:
        columns: List of original column names
        
    Returns:
        Dictionary mapping original names to cleaned names
    """
    name_mapping = {}
    
    for original_name in columns:
        # Convert to string if not already
        clean_name = str(original_name).strip()
        
        # Remove extra whitespace
        clean_name = re.sub(r'\s+', '_', clean_name)
        
        # Remove special characters except underscores and numbers
        clean_name = re.sub(r'[^\w\d_]', '', clean_name)
        
        # Ensure it doesn't start with a number
        if clean_name and clean_name[0].isdigit():
            clean_name = f"col_{clean_name}"
        
        # Handle empty names
        if not clean_name:
            clean_name = f"unnamed_column_{hash(original_name) % 1000}"
        
        name_mapping[original_name] = clean_name
    
    logger.info(f"🧹 Column name cleaning completed: {len(name_mapping)} columns processed")
    return name_mapping


def export_processing_log(processing_results: Dict[str, Any], output_path: str = None) -> str:
    """
    Export processing results to log file
    
    Args:
        processing_results: Results from data processing
        output_path: Path for output file (optional)
        
    Returns:
        Path to exported log file
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"survey_processing_log_{timestamp}.json"
    
    # Prepare log data
    log_data = {
        "processing_timestamp": datetime.now().isoformat(),
        "processing_results": processing_results,
        "log_version": "1.0",
        "generator": "excel-data-processor-agent"
    }
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📝 Processing log exported: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"❌ Failed to export processing log: {str(e)}")
        raise


def create_data_quality_report(data_analysis: Dict[str, Any]) -> str:
    """
    Create a formatted data quality report
    
    Args:
        data_analysis: Results from data analysis functions
        
    Returns:
        Formatted report string
    """
    report_lines = [
        "# Survey Data Quality Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Processing Summary"
    ]
    
    if "processing_stats" in data_analysis:
        stats = data_analysis["processing_stats"]
        report_lines.extend([
            f"- **File**: {stats.get('file_name', 'Unknown')}",
            f"- **Total Rows**: {stats.get('total_rows', 0):,}",
            f"- **Total Columns**: {stats.get('total_columns', 0)}",
            f"- **Filtered Columns**: {stats.get('filtered_columns_count', 0)}",
            ""
        ])
    
    if "quality_assessment" in data_analysis:
        quality = data_analysis["quality_assessment"]
        report_lines.extend([
            "## Data Quality Assessment",
            f"- **Overall Completeness**: {quality.get('overall_completeness', 0):.1f}%",
            f"- **Quality Score**: {quality.get('data_quality_score', 'Unknown').title()}",
            ""
        ])
        
        if quality.get("high_missing_columns"):
            report_lines.extend([
                "### Columns with High Missing Data (>50%)",
                *[f"- {col}" for col in quality["high_missing_columns"]],
                ""
            ])
    
    if "column_metadata" in data_analysis:
        report_lines.extend([
            "## Column Analysis",
            "| Column | Data Type | Null % | Unique Values |",
            "|--------|-----------|--------|---------------|"
        ])
        
        for col, meta in data_analysis["column_metadata"].items():
            report_lines.append(
                f"| {col} | {meta.get('data_type', 'Unknown')} | "
                f"{meta.get('null_percentage', 0):.1f}% | "
                f"{meta.get('unique_count', 0)} |"
            )
        
        report_lines.append("")
    
    report_lines.extend([
        "---",
        "*Report generated by Excel Data Processor Agent*"
    ])
    
    return "\n".join(report_lines)


# Export all utility functions
__all__ = [
    "detect_column_patterns",
    "analyze_data_completeness", 
    "extract_column_sample_data",
    "validate_xlsx_structure",
    "clean_column_names",
    "export_processing_log",
    "create_data_quality_report"
]