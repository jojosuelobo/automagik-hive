"""
Data Type Classifier Tools - Statistical Analysis and Pattern Recognition
=========================================================================

Advanced statistical analysis and pattern recognition utilities for automated
data type classification in survey data analysis workflows.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime
import json

from lib.logging import logger


def detect_numeric_patterns(values: List[Any]) -> Dict[str, Any]:
    """
    Detect numeric patterns and characteristics in data
    
    Args:
        values: List of values to analyze
        
    Returns:
        Dictionary containing numeric pattern analysis
    """
    numeric_analysis = {
        "is_numeric": False,
        "numeric_ratio": 0.0,
        "integer_ratio": 0.0,
        "has_negatives": False,
        "has_decimals": False,
        "numeric_range": None,
        "distribution_type": "unknown"
    }
    
    # Clean and filter values
    clean_values = [val for val in values if val is not None and str(val).strip() != '']
    if not clean_values:
        return numeric_analysis
    
    # Try to convert to numeric
    numeric_values = []
    for val in clean_values:
        try:
            num_val = float(str(val).strip())
            numeric_values.append(num_val)
        except (ValueError, TypeError):
            pass
    
    if not numeric_values:
        return numeric_analysis
    
    # Calculate ratios
    numeric_analysis["numeric_ratio"] = len(numeric_values) / len(clean_values)
    numeric_analysis["is_numeric"] = numeric_analysis["numeric_ratio"] > 0.8
    
    # Integer analysis
    integer_count = sum(1 for val in numeric_values if val == int(val))
    numeric_analysis["integer_ratio"] = integer_count / len(numeric_values)
    
    # Range and characteristics
    numeric_analysis.update({
        "has_negatives": any(val < 0 for val in numeric_values),
        "has_decimals": any(val != int(val) for val in numeric_values),
        "numeric_range": (min(numeric_values), max(numeric_values)),
        "mean": statistics.mean(numeric_values),
        "median": statistics.median(numeric_values),
        "std_dev": statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0
    })
    
    # Distribution analysis
    unique_count = len(set(numeric_values))
    if unique_count <= 10:
        numeric_analysis["distribution_type"] = "discrete"
    elif numeric_analysis["std_dev"] / abs(numeric_analysis["mean"]) < 0.1:
        numeric_analysis["distribution_type"] = "concentrated"
    else:
        numeric_analysis["distribution_type"] = "continuous"
    
    logger.debug(f"📊 Numeric pattern analysis: {numeric_analysis['numeric_ratio']:.2f} numeric ratio")
    return numeric_analysis


def detect_categorical_patterns(values: List[Any]) -> Dict[str, Any]:
    """
    Detect categorical patterns and characteristics
    
    Args:
        values: List of values to analyze
        
    Returns:
        Dictionary containing categorical pattern analysis
    """
    categorical_analysis = {
        "is_categorical": False,
        "unique_count": 0,
        "unique_ratio": 0.0,
        "most_common": [],
        "is_binary": False,
        "is_ordinal": False,
        "category_type": "unknown"
    }
    
    # Clean values
    clean_values = [str(val).strip() for val in values if val is not None and str(val).strip() != '']
    if not clean_values:
        return categorical_analysis
    
    # Basic counts
    unique_values = list(set(clean_values))
    value_counts = Counter(clean_values)
    
    categorical_analysis.update({
        "unique_count": len(unique_values),
        "unique_ratio": len(unique_values) / len(clean_values),
        "most_common": value_counts.most_common(5)
    })
    
    # Categorical determination
    categorical_analysis["is_categorical"] = (
        len(unique_values) <= 20 or 
        categorical_analysis["unique_ratio"] <= 0.1
    )
    
    # Binary detection
    categorical_analysis["is_binary"] = len(unique_values) == 2
    
    # Ordinal pattern detection
    ordinal_patterns = [
        r'^[1-5]$',  # 1-5 scale
        r'^[1-9]|10$',  # 1-10 scale  
        r'(strongly\s+)?(disagree|agree)',  # Likert scale
        r'(very\s+)?(poor|excellent|good|bad)',  # Quality scale
        r'(never|rarely|sometimes|often|always)',  # Frequency scale
        r'(low|medium|high)',  # Level scale
    ]
    
    ordinal_matches = 0
    for pattern in ordinal_patterns:
        if any(re.search(pattern, val.lower()) for val in unique_values):
            ordinal_matches += 1
    
    categorical_analysis["is_ordinal"] = ordinal_matches > 0 or (
        len(unique_values) <= 10 and
        all(str(val).isdigit() for val in unique_values)
    )
    
    # Determine category type
    if categorical_analysis["is_binary"]:
        categorical_analysis["category_type"] = "binary"
    elif categorical_analysis["is_ordinal"]:
        categorical_analysis["category_type"] = "ordinal"
    elif categorical_analysis["is_categorical"]:
        categorical_analysis["category_type"] = "nominal"
    
    logger.debug(f"📂 Categorical analysis: {len(unique_values)} unique values, {categorical_analysis['category_type']}")
    return categorical_analysis


def detect_temporal_patterns(values: List[Any]) -> Dict[str, Any]:
    """
    Detect temporal/date patterns in data
    
    Args:
        values: List of values to analyze
        
    Returns:
        Dictionary containing temporal pattern analysis
    """
    temporal_analysis = {
        "is_temporal": False,
        "date_ratio": 0.0,
        "date_formats": [],
        "temporal_type": "unknown",
        "date_range": None
    }
    
    # Clean values
    clean_values = [str(val).strip() for val in values if val is not None and str(val).strip() != '']
    if not clean_values:
        return temporal_analysis
    
    # Date pattern detection
    date_patterns = [
        (r'\d{4}-\d{2}-\d{2}', 'ISO date'),
        (r'\d{2}/\d{2}/\d{4}', 'US date'),
        (r'\d{2}-\d{2}-\d{4}', 'European date'),
        (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', 'datetime'),
        (r'\d{2}:\d{2}:\d{2}', 'time'),
        (r'\d{1,2}/\d{1,2}/\d{2,4}', 'flexible date')
    ]
    
    date_matches = 0
    detected_formats = []
    
    for value in clean_values:
        for pattern, format_name in date_patterns:
            if re.search(pattern, value):
                date_matches += 1
                if format_name not in detected_formats:
                    detected_formats.append(format_name)
                break
    
    temporal_analysis["date_ratio"] = date_matches / len(clean_values)
    temporal_analysis["is_temporal"] = temporal_analysis["date_ratio"] > 0.5
    temporal_analysis["date_formats"] = detected_formats
    
    # Determine temporal type
    if temporal_analysis["is_temporal"]:
        if any("datetime" in fmt for fmt in detected_formats):
            temporal_analysis["temporal_type"] = "datetime"
        elif any("time" in fmt for fmt in detected_formats):
            temporal_analysis["temporal_type"] = "time"
        else:
            temporal_analysis["temporal_type"] = "date"
    
    logger.debug(f"📅 Temporal analysis: {temporal_analysis['date_ratio']:.2f} date ratio")
    return temporal_analysis


def detect_textual_patterns(values: List[Any]) -> Dict[str, Any]:
    """
    Detect textual patterns and characteristics
    
    Args:
        values: List of values to analyze
        
    Returns:
        Dictionary containing textual pattern analysis
    """
    textual_analysis = {
        "is_textual": False,
        "avg_length": 0.0,
        "max_length": 0,
        "word_count_avg": 0.0,
        "has_sentences": False,
        "language_detected": "unknown",
        "text_type": "unknown"
    }
    
    # Clean values  
    clean_values = [str(val).strip() for val in values if val is not None and str(val).strip() != '']
    if not clean_values:
        return textual_analysis
    
    # Length analysis
    lengths = [len(val) for val in clean_values]
    textual_analysis.update({
        "avg_length": statistics.mean(lengths),
        "max_length": max(lengths),
        "min_length": min(lengths)
    })
    
    # Word count analysis
    word_counts = []
    for val in clean_values:
        words = len(val.split())
        word_counts.append(words)
    
    textual_analysis["word_count_avg"] = statistics.mean(word_counts) if word_counts else 0
    
    # Sentence detection
    sentence_indicators = ['.', '!', '?']
    textual_analysis["has_sentences"] = any(
        any(indicator in val for indicator in sentence_indicators)
        for val in clean_values
    )
    
    # Textual determination
    textual_analysis["is_textual"] = (
        textual_analysis["avg_length"] > 10 or
        textual_analysis["word_count_avg"] > 2 or
        textual_analysis["has_sentences"]
    )
    
    # Text type classification
    if textual_analysis["avg_length"] > 100:
        textual_analysis["text_type"] = "long_form"
    elif textual_analysis["word_count_avg"] > 5:
        textual_analysis["text_type"] = "sentences"
    elif textual_analysis["avg_length"] > 20:
        textual_analysis["text_type"] = "short_form"
    else:
        textual_analysis["text_type"] = "labels"
    
    logger.debug(f"📝 Textual analysis: {textual_analysis['avg_length']:.1f} avg length, {textual_analysis['text_type']}")
    return textual_analysis


def calculate_confidence_score(analyses: Dict[str, Dict[str, Any]]) -> float:
    """
    Calculate overall confidence score for data type classification
    
    Args:
        analyses: Dictionary containing all pattern analyses
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    confidence_factors = []
    
    # Check for clear patterns
    if analyses.get("numeric", {}).get("numeric_ratio", 0) > 0.9:
        confidence_factors.append(0.9)
    
    if analyses.get("categorical", {}).get("is_binary"):
        confidence_factors.append(0.95)
    
    if analyses.get("temporal", {}).get("date_ratio", 0) > 0.8:
        confidence_factors.append(0.9)
    
    if analyses.get("textual", {}).get("avg_length", 0) > 50:
        confidence_factors.append(0.85)
    
    # Penalize for conflicting patterns
    pattern_count = sum(1 for analysis in analyses.values() 
                       if any(key.startswith("is_") and val for key, val in analysis.items()))
    
    if pattern_count > 1:
        confidence_penalty = 0.2 * (pattern_count - 1)
    else:
        confidence_penalty = 0
    
    # Calculate final confidence
    if confidence_factors:
        base_confidence = max(confidence_factors)
    else:
        base_confidence = 0.5  # Default confidence
    
    final_confidence = max(0.0, min(1.0, base_confidence - confidence_penalty))
    
    return final_confidence


def generate_statistical_summary(values: List[Any], data_type: str) -> Dict[str, Any]:
    """
    Generate appropriate statistical summary based on data type
    
    Args:
        values: List of values to analyze
        data_type: Detected data type
        
    Returns:
        Statistical summary appropriate for the data type
    """
    summary = {
        "data_type": data_type,
        "total_count": len(values),
        "null_count": sum(1 for val in values if val is None or str(val).strip() == ''),
        "unique_count": len(set(str(val) for val in values if val is not None))
    }
    
    # Clean values for analysis
    clean_values = [val for val in values if val is not None and str(val).strip() != '']
    
    if data_type == "numerical":
        # Numeric statistics
        try:
            numeric_values = [float(val) for val in clean_values if str(val).replace('.', '').replace('-', '').isdigit()]
            if numeric_values:
                summary.update({
                    "mean": statistics.mean(numeric_values),
                    "median": statistics.median(numeric_values),
                    "std_dev": statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0,
                    "min_value": min(numeric_values),
                    "max_value": max(numeric_values),
                    "quartiles": [
                        np.percentile(numeric_values, 25),
                        np.percentile(numeric_values, 50),
                        np.percentile(numeric_values, 75)
                    ]
                })
        except Exception:
            summary["error"] = "Failed to calculate numeric statistics"
    
    elif data_type == "categorical":
        # Categorical statistics
        value_counts = Counter(str(val) for val in clean_values)
        summary.update({
            "mode": value_counts.most_common(1)[0][0] if value_counts else None,
            "value_counts": dict(value_counts.most_common(10)),
            "entropy": -sum((count/len(clean_values)) * np.log2(count/len(clean_values)) 
                           for count in value_counts.values() if count > 0)
        })
    
    elif data_type == "textual":
        # Text statistics
        lengths = [len(str(val)) for val in clean_values]
        words = [len(str(val).split()) for val in clean_values]
        summary.update({
            "avg_length": statistics.mean(lengths) if lengths else 0,
            "max_length": max(lengths) if lengths else 0,
            "avg_words": statistics.mean(words) if words else 0,
            "total_characters": sum(lengths)
        })
    
    elif data_type == "temporal":
        # Temporal statistics  
        summary.update({
            "date_formats_detected": len(set(str(val)[:10] for val in clean_values)),
            "potential_time_series": len(clean_values) > 10
        })
    
    return summary


def recommend_chart_types(data_type: str, sub_type: str, unique_count: int, total_count: int) -> List[str]:
    """
    Recommend appropriate chart types based on data characteristics
    
    Args:
        data_type: Primary data type
        sub_type: Data sub-type
        unique_count: Number of unique values
        total_count: Total number of values
        
    Returns:
        List of recommended chart types in order of preference
    """
    recommendations = []
    
    if data_type == "categorical":
        if sub_type == "binary":
            recommendations = ["pie_chart", "donut_chart", "horizontal_bar_chart"]
        elif sub_type == "ordinal" or unique_count <= 10:
            recommendations = ["horizontal_bar_chart", "stacked_bar_chart", "radar_chart"]
        else:
            recommendations = ["pie_chart", "horizontal_bar_chart", "treemap"]
    
    elif data_type == "numerical":
        if sub_type == "continuous":
            recommendations = ["histogram", "box_plot", "density_plot", "violin_plot"]
        elif sub_type == "discrete" or unique_count <= 20:
            recommendations = ["bar_chart", "histogram", "line_chart"]
        else:
            recommendations = ["histogram", "scatter_plot", "heatmap"]
    
    elif data_type == "temporal":
        recommendations = ["time_series_line", "area_chart", "calendar_heatmap", "trend_analysis"]
    
    elif data_type == "textual":
        if sub_type == "long_form":
            recommendations = ["word_cloud", "sentiment_analysis", "topic_modeling"]
        else:
            recommendations = ["frequency_chart", "word_cloud", "text_analysis"]
    
    else:
        recommendations = ["table", "frequency_chart"]
    
    return recommendations


# Export all utility functions
__all__ = [
    "detect_numeric_patterns",
    "detect_categorical_patterns", 
    "detect_temporal_patterns",
    "detect_textual_patterns",
    "calculate_confidence_score",
    "generate_statistical_summary",
    "recommend_chart_types"
]