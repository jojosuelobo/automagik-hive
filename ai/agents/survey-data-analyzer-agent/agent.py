"""
Survey Data Analyzer Agent - Specialized Survey Data Processing
==============================================================

This agent handles survey data extraction, organization, and analysis
to prepare data for chart generation.
"""

import json
import pandas as pd
from collections import Counter
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from lib.logging import logger
from lib.utils.version_factory import create_agent


def identify_survey_columns(separated_data: Dict[str, Any]) -> List[str]:
    """
    Identify columns that contain survey data
    
    Args:
        separated_data: Separated Excel data from excel-separator-agent
        
    Returns:
        List of column names that contain survey data
    """
    survey_columns = []
    columns = separated_data.get("columns", {})
    
    # Patterns to identify survey columns
    survey_patterns = [
        r'pesquisa',  # Direct survey reference
        r'screen',    # Screen-based questions
        r'question',  # Question columns
        r'q\d+',      # Q1, Q2, etc.
        r'pergunta',  # Portuguese for question
    ]
    
    for col_name, col_data in columns.items():
        # Skip clearly non-survey columns
        if any(skip_pattern in col_name.lower() for skip_pattern in ['name', 'email', 'number', 'phone', 'telefone']):
            continue
            
        # Check if column name matches survey patterns
        if any(re.search(pattern, col_name.lower()) for pattern in survey_patterns):
            # Also check if column has actual data (not empty)
            if col_data.get('non_null_count', 0) > 0:
                survey_columns.append(col_name)
                
    logger.info(f"Identified {len(survey_columns)} survey columns")
    return survey_columns


def extract_survey_responses(separated_data: Dict[str, Any], survey_columns: List[str]) -> Dict[str, Any]:
    """
    Extract and organize survey responses from identified columns
    
    Args:
        separated_data: Separated Excel data
        survey_columns: List of survey column names
        
    Returns:
        Dictionary with organized survey responses
    """
    survey_data = {
        "survey_questions": {},
        "metadata": {
            "total_survey_columns": len(survey_columns),
            "total_responses": separated_data.get("metadata", {}).get("total_rows", 0),
            "extracted_at": datetime.now().isoformat()
        }
    }
    
    columns = separated_data.get("columns", {})
    
    for col_name in survey_columns:
        if col_name not in columns:
            continue
            
        col_data = columns[col_name]
        responses = col_data.get("data", [])
        
        # Clean responses (remove empty, NaN, etc.)
        clean_responses = []
        for response in responses:
            if response is not None and str(response).strip() and str(response).lower() not in ['nan', 'none', '', 'null']:
                # Handle pandas NaN values
                if str(response) != 'nan':
                    clean_responses.append(str(response).strip())
        
        # Analyze response patterns
        response_analysis = analyze_response_patterns(clean_responses, col_name)
        
        survey_data["survey_questions"][col_name] = {
            "original_column_name": col_name,
            "question_type": response_analysis["question_type"],
            "total_responses": len(clean_responses),
            "response_rate": len(clean_responses) / survey_data["metadata"]["total_responses"] * 100,
            "responses": clean_responses,
            "frequency_analysis": response_analysis["frequency_analysis"],
            "unique_responses": response_analysis["unique_responses"],
            "chart_suggestions": response_analysis["chart_suggestions"]
        }
    
    logger.info(f"Extracted survey data for {len(survey_data['survey_questions'])} questions")
    
    # Apply AI classification to enhance specific questions
    try:
        from ai.agents.response_classifier_agent.agent import enhance_survey_data_with_classification
        enhanced_survey_data = enhance_survey_data_with_classification(survey_data)
        logger.info("AI classification enhancement applied to survey data")
        return enhanced_survey_data
    except Exception as e:
        logger.warning(f"AI classification enhancement failed: {str(e)}")
        return survey_data


def analyze_response_patterns(responses: List[str], column_name: str) -> Dict[str, Any]:
    """
    Analyze patterns in survey responses to determine question type and best visualization
    
    Args:
        responses: List of clean responses
        column_name: Name of the survey column
        
    Returns:
        Analysis of response patterns
    """
    if not responses:
        return {
            "question_type": "empty",
            "frequency_analysis": {},
            "unique_responses": 0,
            "chart_suggestions": []
        }
    
    # Count response frequencies
    response_counts = Counter(responses)
    total_responses = len(responses)
    unique_responses = len(response_counts)
    
    # Calculate percentages
    frequency_analysis = {}
    for response, count in response_counts.items():
        frequency_analysis[response] = {
            "count": count,
            "percentage": round((count / total_responses) * 100, 2)
        }
    
    # Determine question type based on response patterns
    question_type = determine_question_type(responses, response_counts, column_name)
    
    # Suggest appropriate chart types
    chart_suggestions = suggest_chart_types(question_type, unique_responses, response_counts)
    
    return {
        "question_type": question_type,
        "frequency_analysis": frequency_analysis,
        "unique_responses": unique_responses,
        "chart_suggestions": chart_suggestions
    }


def determine_question_type(responses: List[str], response_counts: Counter, column_name: str) -> str:
    """
    Determine the type of survey question based on response patterns
    """
    unique_count = len(response_counts)
    
    # Check for scale questions (1-5, 1-10, etc.)
    if all(response.isdigit() for response in response_counts.keys()):
        numbers = [int(r) for r in response_counts.keys()]
        if max(numbers) - min(numbers) <= 10:
            return "scale_numeric"
    
    # Check for Yes/No questions
    yes_no_patterns = {'sim', 'não', 'yes', 'no', '1_sim', '1_não', '0_não', '1_yes', '0_no'}
    if any(response.lower() in yes_no_patterns for response in response_counts.keys()):
        return "yes_no"
    
    # Check for Likert scale
    likert_patterns = {
        'muito fácil', 'fácil', 'médio', 'difícil', 'muito difícil',
        'super fácil', 'super difícil', 'nenhuma', 'pouca', 'média', 'muita',
        'concordo totalmente', 'concordo', 'neutro', 'discordo', 'discordo totalmente'
    }
    if any(response.lower() in likert_patterns for response in response_counts.keys()):
        return "likert_scale"
    
    # Check for multiple choice with many options
    if unique_count > 10:
        return "multiple_choice_many"
    elif unique_count > 2:
        return "multiple_choice_few"
    
    # Default to text if nothing else matches
    return "text_response"


def suggest_chart_types(question_type: str, unique_responses: int, response_counts: Counter) -> List[Dict[str, str]]:
    """
    Suggest appropriate chart types based on question type and data characteristics
    """
    suggestions = []
    
    if question_type == "yes_no":
        suggestions.extend([
            {"type": "pie_chart", "reason": "Ideal para mostrar proporção binária"},
            {"type": "donut_chart", "reason": "Versão moderna do gráfico de pizza"},
            {"type": "bar_chart", "reason": "Comparação clara entre duas opções"}
        ])
    
    elif question_type == "scale_numeric":
        suggestions.extend([
            {"type": "bar_chart", "reason": "Mostra distribuição da escala numérica"},
            {"type": "histogram", "reason": "Visualiza distribuição de frequências"},
            {"type": "line_chart", "reason": "Se houver progressão temporal"}
        ])
    
    elif question_type == "likert_scale":
        suggestions.extend([
            {"type": "horizontal_bar", "reason": "Ideal para escalas de concordância"},
            {"type": "stacked_bar", "reason": "Mostra proporções da escala"},
            {"type": "diverging_bar", "reason": "Destaca posições positivas/negativas"}
        ])
    
    elif question_type in ["multiple_choice_few", "multiple_choice_many"]:
        if unique_responses <= 5:
            suggestions.extend([
                {"type": "pie_chart", "reason": "Bom para poucas categorias"},
                {"type": "bar_chart", "reason": "Comparação clara entre categorias"}
            ])
        else:
            suggestions.extend([
                {"type": "horizontal_bar", "reason": "Melhor para muitas categorias"},
                {"type": "treemap", "reason": "Visualiza proporções hierárquicas"}
            ])
    
    elif question_type == "text_response":
        suggestions.extend([
            {"type": "word_cloud", "reason": "Visualiza frequência de palavras"},
            {"type": "bar_chart", "reason": "Top respostas mais frequentes"}
        ])
    
    return suggestions


def generate_survey_summary(survey_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comprehensive summary of survey data
    """
    questions = survey_data.get("survey_questions", {})
    
    summary = {
        "overview": {
            "total_questions": len(questions),
            "total_possible_responses": survey_data["metadata"].get("total_responses", 0),
            "question_types": {},
            "avg_response_rate": 0
        },
        "question_breakdown": {},
        "visualization_recommendations": [],
        "generated_at": datetime.now().isoformat()
    }
    
    # Analyze question types
    type_counts = Counter()
    total_response_rate = 0
    
    for q_name, q_data in questions.items():
        q_type = q_data["question_type"]
        type_counts[q_type] += 1
        total_response_rate += q_data["response_rate"]
        
        # Add to breakdown
        summary["question_breakdown"][q_name] = {
            "type": q_type,
            "responses": q_data["total_responses"],
            "response_rate": q_data["response_rate"],
            "top_responses": dict(list(q_data["frequency_analysis"].items())[:3])
        }
    
    summary["overview"]["question_types"] = dict(type_counts)
    summary["overview"]["avg_response_rate"] = round(total_response_rate / len(questions), 2) if questions else 0
    
    # Generate visualization recommendations
    for q_name, q_data in questions.items():
        if q_data["chart_suggestions"]:
            summary["visualization_recommendations"].append({
                "question": q_name,
                "recommended_chart": q_data["chart_suggestions"][0]["type"],
                "reason": q_data["chart_suggestions"][0]["reason"]
            })
    
    return summary


# Agent factory function
async def get_survey_data_analyzer_agent(**kwargs):
    """Factory function to create survey data analyzer agent"""
    return await create_agent("survey-data-analyzer-agent", **kwargs) 