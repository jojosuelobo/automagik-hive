"""
Data Type Classifier Agent - AI-Powered Survey Data Classification
=================================================================

Intelligent data type classifier that analyzes survey columns and automatically
determines data types using AI reasoning combined with statistical analysis.
Provides visualization recommendations and quality assessments.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union
import yaml
import json
import re
from datetime import datetime
from collections import Counter
import statistics

from agno import Agent
from agno.models.anthropic import Claude
from agno.storage.postgres import PostgresStorage
from lib.logging import logger


def create_classifier_model() -> Claude:
    """Create Claude model for data type classification"""
    return Claude(
        id='claude-sonnet-4-20250514',
        temperature=0.1,
        max_tokens=4000
    )


def analyze_column_patterns(column_data: List[Any]) -> Dict[str, Any]:
    """
    Analyze patterns in column data to aid classification
    
    Args:
        column_data: List of values from a column
        
    Returns:
        Dictionary containing pattern analysis results
    """
    # Remove null/empty values for analysis
    clean_data = [val for val in column_data if val is not None and str(val).strip() != '']
    
    if not clean_data:
        return {
            "pattern_type": "empty",
            "confidence": 0.0,
            "analysis": "No valid data found"
        }
    
    analysis = {
        "total_values": len(column_data),
        "valid_values": len(clean_data),
        "null_ratio": (len(column_data) - len(clean_data)) / len(column_data) if column_data else 0,
        "unique_count": len(set(clean_data)),
        "unique_ratio": len(set(clean_data)) / len(clean_data) if clean_data else 0
    }
    
    # Convert to strings for pattern analysis
    str_values = [str(val).strip() for val in clean_data]
    
    # Analyze string lengths
    lengths = [len(val) for val in str_values]
    analysis.update({
        "avg_length": statistics.mean(lengths) if lengths else 0,
        "min_length": min(lengths) if lengths else 0,
        "max_length": max(lengths) if lengths else 0,
        "length_variance": statistics.variance(lengths) if len(lengths) > 1 else 0
    })
    
    # Pattern detection
    patterns = {
        "all_numeric": all(val.replace('.', '').replace('-', '').replace('+', '').isdigit() for val in str_values),
        "mostly_numeric": sum(1 for val in str_values if val.replace('.', '').replace('-', '').replace('+', '').isdigit()) / len(str_values) > 0.8,
        "has_dates": any(re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', val) for val in str_values),
        "has_timestamps": any(re.search(r'\d{4}-\d{2}-\d{2}', val) for val in str_values),
        "binary_like": analysis["unique_count"] == 2,
        "scale_like": analysis["unique_count"] <= 10 and analysis["mostly_numeric"],
        "short_text": analysis["avg_length"] < 50 and not analysis["all_numeric"],
        "long_text": analysis["avg_length"] >= 50
    }
    
    analysis["patterns"] = patterns
    
    # Sample values for further analysis
    analysis["sample_values"] = str_values[:10]
    analysis["value_frequency"] = dict(Counter(str_values).most_common(5))
    
    return analysis


def classify_data_type(column_name: str, column_data: List[Any], context: str = "") -> Dict[str, Any]:
    """
    Classify data type using AI reasoning and statistical analysis
    
    Args:
        column_name: Name of the column
        column_data: List of values from the column
        context: Additional context about the data
        
    Returns:
        Classification results with confidence scores
    """
    # Get pattern analysis
    pattern_analysis = analyze_column_patterns(column_data)
    
    # Initialize classification result
    classification = {
        "column_name": column_name,
        "primary_type": "unknown",
        "sub_type": None,
        "confidence": 0.0,
        "reasoning": "",
        "statistical_summary": {},
        "visualization_recommendations": [],
        "quality_flags": [],
        "classification_timestamp": datetime.now().isoformat()
    }
    
    # Statistical summary
    try:
        numeric_values = []
        for val in column_data:
            if val is not None:
                try:
                    numeric_values.append(float(val))
                except (ValueError, TypeError):
                    pass
        
        if numeric_values:
            classification["statistical_summary"] = {
                "count": len(numeric_values),
                "mean": statistics.mean(numeric_values),
                "median": statistics.median(numeric_values),
                "std_dev": statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0,
                "min_value": min(numeric_values),
                "max_value": max(numeric_values),
                "range": max(numeric_values) - min(numeric_values)
            }
    except Exception:
        pass
    
    # Classification logic
    patterns = pattern_analysis.get("patterns", {})
    
    # Temporal data detection
    if patterns.get("has_dates") or patterns.get("has_timestamps"):
        classification.update({
            "primary_type": "temporal",
            "sub_type": "datetime",
            "confidence": 0.9,
            "reasoning": "Data contains date/time patterns",
            "visualization_recommendations": ["time_series_line", "area_chart", "calendar_heatmap"]
        })
    
    # Numerical data detection
    elif patterns.get("all_numeric") and pattern_analysis["unique_count"] > 10:
        if pattern_analysis["unique_count"] / pattern_analysis["valid_values"] > 0.5:
            classification.update({
                "primary_type": "numerical",
                "sub_type": "continuous",
                "confidence": 0.95,
                "reasoning": "All values are numeric with high variability",
                "visualization_recommendations": ["histogram", "box_plot", "density_plot"]
            })
        else:
            classification.update({
                "primary_type": "numerical", 
                "sub_type": "discrete",
                "confidence": 0.9,
                "reasoning": "Numeric values with limited distinct values",
                "visualization_recommendations": ["bar_chart", "histogram", "line_chart"]
            })
    
    # Categorical data detection
    elif (pattern_analysis["unique_count"] <= 20 and 
          pattern_analysis["unique_ratio"] <= 0.1) or patterns.get("binary_like"):
        
        if patterns.get("binary_like"):
            classification.update({
                "primary_type": "categorical",
                "sub_type": "binary",
                "confidence": 0.95,
                "reasoning": "Exactly two distinct values found",
                "visualization_recommendations": ["pie_chart", "donut_chart", "horizontal_bar_chart"]
            })
        elif patterns.get("scale_like"):
            classification.update({
                "primary_type": "categorical",
                "sub_type": "ordinal",
                "confidence": 0.85,
                "reasoning": "Limited numeric values suggesting rating scale",
                "visualization_recommendations": ["horizontal_bar_chart", "stacked_bar_chart"]
            })
        else:
            classification.update({
                "primary_type": "categorical",
                "sub_type": "nominal",
                "confidence": 0.8,
                "reasoning": "Limited distinct values suggesting categories",
                "visualization_recommendations": ["pie_chart", "horizontal_bar_chart", "donut_chart"]
            })
    
    # Textual data detection
    elif patterns.get("long_text") or pattern_analysis["avg_length"] > 20:
        classification.update({
            "primary_type": "textual",
            "sub_type": "open_ended",
            "confidence": 0.9,
            "reasoning": "Long text values suggesting open-ended responses",
            "visualization_recommendations": ["word_cloud", "sentiment_analysis", "frequency_chart"]
        })
    
    else:
        # Default classification with lower confidence
        if patterns.get("mostly_numeric"):
            classification.update({
                "primary_type": "numerical",
                "sub_type": "mixed",
                "confidence": 0.6,
                "reasoning": "Mostly numeric but with some inconsistencies",
                "visualization_recommendations": ["histogram", "box_plot"]
            })
        else:
            classification.update({
                "primary_type": "textual",
                "sub_type": "mixed",
                "confidence": 0.5,
                "reasoning": "Mixed data types, defaulting to textual",
                "visualization_recommendations": ["frequency_chart", "text_analysis"]
            })
    
    # Quality flags
    if pattern_analysis["null_ratio"] > 0.3:
        classification["quality_flags"].append("high_missing_data")
    
    if classification["confidence"] < 0.7:
        classification["quality_flags"].append("low_confidence_classification")
    
    if pattern_analysis["unique_count"] == pattern_analysis["valid_values"]:
        classification["quality_flags"].append("all_unique_values")
    
    # Add pattern analysis to result
    classification["pattern_analysis"] = pattern_analysis
    
    logger.info(f"🔍 Classified '{column_name}': {classification['primary_type']} ({classification['confidence']:.2f} confidence)")
    
    return classification


def classify_dataset_columns(dataset: Dict[str, List[Any]], context: str = "") -> Dict[str, Any]:
    """
    Classify all columns in a dataset
    
    Args:
        dataset: Dictionary mapping column names to data lists
        context: Additional context about the dataset
        
    Returns:
        Complete classification results for all columns
    """
    results = {
        "classification_timestamp": datetime.now().isoformat(),
        "dataset_context": context,
        "total_columns": len(dataset),
        "classifications": {},
        "summary": {
            "categorical": [],
            "numerical": [],
            "temporal": [],
            "textual": [],
            "uncertain": []
        },
        "quality_overview": {
            "high_confidence": 0,
            "medium_confidence": 0, 
            "low_confidence": 0,
            "quality_issues": []
        }
    }
    
    for column_name, column_data in dataset.items():
        classification = classify_data_type(column_name, column_data, context)
        results["classifications"][column_name] = classification
        
        # Update summary
        primary_type = classification["primary_type"]
        if primary_type in results["summary"]:
            results["summary"][primary_type].append(column_name)
        
        # Update quality overview
        confidence = classification["confidence"]
        if confidence >= 0.8:
            results["quality_overview"]["high_confidence"] += 1
        elif confidence >= 0.6:
            results["quality_overview"]["medium_confidence"] += 1
        else:
            results["quality_overview"]["low_confidence"] += 1
            results["summary"]["uncertain"].append(column_name)
        
        # Collect quality issues
        if classification["quality_flags"]:
            results["quality_overview"]["quality_issues"].extend([
                f"{column_name}: {flag}" for flag in classification["quality_flags"]
            ])
    
    logger.info(f"📊 Dataset classification completed: {len(dataset)} columns classified")
    return results


def generate_visualization_plan(classification_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate comprehensive visualization plan based on classifications
    
    Args:
        classification_results: Results from classify_dataset_columns
        
    Returns:
        Detailed visualization plan
    """
    plan = {
        "generation_timestamp": datetime.now().isoformat(),
        "visualization_groups": {},
        "dashboard_layout": [],
        "export_recommendations": [],
        "technical_requirements": []
    }
    
    classifications = classification_results.get("classifications", {})
    
    # Group columns by visualization type
    viz_groups = {}
    
    for column_name, classification in classifications.items():
        primary_type = classification["primary_type"]
        sub_type = classification.get("sub_type", "default")
        recommendations = classification.get("visualization_recommendations", [])
        
        # Select primary visualization
        primary_viz = recommendations[0] if recommendations else "table"
        
        if primary_viz not in viz_groups:
            viz_groups[primary_viz] = []
        
        viz_groups[primary_viz].append({
            "column": column_name,
            "type": primary_type,
            "sub_type": sub_type,
            "confidence": classification["confidence"]
        })
    
    plan["visualization_groups"] = viz_groups
    
    # Generate dashboard layout recommendations
    layout_sections = []
    
    # Executive summary section
    layout_sections.append({
        "section": "executive_summary",
        "priority": 1,
        "components": ["dataset_overview", "key_insights", "quality_metrics"]
    })
    
    # Main visualizations by type
    for viz_type, columns in viz_groups.items():
        if len(columns) > 0:
            layout_sections.append({
                "section": f"{viz_type}_section",
                "priority": 2,
                "visualization_type": viz_type,
                "columns": [col["column"] for col in columns],
                "estimated_charts": len(columns)
            })
    
    # Detailed analysis section
    layout_sections.append({
        "section": "detailed_analysis", 
        "priority": 3,
        "components": ["statistical_summaries", "data_quality_report", "methodology"]
    })
    
    plan["dashboard_layout"] = layout_sections
    
    # Export recommendations
    plan["export_recommendations"] = [
        "interactive_html_dashboard",
        "pdf_executive_report", 
        "png_chart_collection",
        "csv_processed_data",
        "json_analysis_results"
    ]
    
    # Technical requirements
    plan["technical_requirements"] = [
        "plotly for interactive charts",
        "matplotlib/seaborn for statistical plots",
        "wordcloud for text analysis",
        "pandas for data manipulation",
        "jinja2 for report templates"
    ]
    
    logger.info(f"📈 Visualization plan generated: {len(viz_groups)} chart types, {len(layout_sections)} sections")
    return plan


def get_data_type_classifier_agent(
    version: Optional[int] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = False,
    db_url: Optional[str] = None
) -> Agent:
    """Data type classifier agent factory function"""
    
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Create agent with tools
    agent = Agent(
        name=config["agent"]["name"],
        agent_id=config["agent"]["agent_id"],
        instructions=config["instructions"],
        model=create_classifier_model(),
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
    agent.tools.extend([
        analyze_column_patterns,
        classify_data_type,
        classify_dataset_columns,
        generate_visualization_plan
    ])
    
    logger.info(f"🔍 Data Type Classifier Agent initialized - Version {config['agent']['version']}")
    return agent


# Export the factory function
__all__ = [
    "get_data_type_classifier_agent", 
    "classify_data_type",
    "classify_dataset_columns",
    "generate_visualization_plan"
]


if __name__ == "__main__":
    # Test the agent
    import asyncio
    
    async def test_classifier():
        """Test data type classifier agent"""
        agent = get_data_type_classifier_agent(debug_mode=True)
        
        test_message = """
        I need you to classify the data types for these survey columns:
        
        Column: pesquisa300625_screen0
        Sample values: [1, 2, 3, 1, 4, 2, 3, 1, 5, 2]
        
        Column: pesquisa300625_screen1
        Sample values: ["Yes", "No", "Maybe", "Yes", "No", "Yes", "No", "Maybe"]
        
        Column: pesquisa300625_screen2
        Sample values: ["Very satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very satisfied"]
        
        Please classify each column and recommend appropriate visualizations.
        """
        
        logger.info("Testing data type classifier agent...")
        response = await agent.arun(test_message)
        logger.info(f"🤖 Response: {response.content}")
    
    # Run test
    asyncio.run(test_classifier())