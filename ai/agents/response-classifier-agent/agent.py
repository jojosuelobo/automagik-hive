"""
Response Classifier Agent - AI-Powered Survey Response Classification
===================================================================

This agent uses AI to classify and normalize survey responses into
standardized categories for better visualization and analysis.
"""

import json
import re
from collections import Counter, defaultdict
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from lib.logging import logger
from lib.utils.version_factory import create_agent
from agno.models.anthropic import Claude


def create_classifier_model():
    """Create Claude model for response classification"""
    try:
        # Use the factory function to create properly configured model
        from lib.utils.version_factory import create_agent
        return Claude(
            id='claude-sonnet-4-20250514',
            temperature=0.1,
            max_tokens=1000
        )
    except:
        # Fallback: basic Claude instance
        return Claude()


def classify_response_with_ai(response: str, question_context: str = "") -> Dict[str, Any]:
    """
    Use AI to classify a single response
    
    Args:
        response: The response text to classify
        question_context: Context about the question being answered
        
    Returns:
        Classification result with category, confidence, and explanation
    """
    
    model = create_classifier_model()
    
    prompt = f"""
Você é um especialista em análise de respostas de pesquisa. Sua tarefa é classificar a resposta abaixo.

CONTEXTO DA PERGUNTA: {question_context}

RESPOSTA PARA CLASSIFICAR: "{response}"

Classifique esta resposta em uma das seguintes categorias:
- SIM: Se indica problemas, dificuldades, resposta afirmativa/positiva
- NÃO: Se indica ausência de problemas, facilidade, resposta negativa
- OUTRAS: Se é ambígua, neutra, ou não se encaixa claramente

IMPORTANTE:
- Considere erros de digitação e linguagem coloquial
- Foque no SIGNIFICADO, não apenas nas palavras exatas
- "Não" pode significar SIM se estiver negando facilidade (ex: "não foi fácil")
- Pontos, vírgulas ou respostas muito curtas podem ser ambíguas

Responda APENAS em formato JSON:
{{
    "categoria": "SIM|NÃO|OUTRAS",
    "confianca": 85,
    "explicacao": "Breve explicação da decisão",
    "subcategoria": "Descrição mais específica se necessário"
}}
"""
    
    try:
        # Use invoke instead of run for the Claude model
        response_obj = model.invoke(prompt)
        result = json.loads(response_obj.content)
        
        # Validate and normalize result
        result["categoria"] = result.get("categoria", "OUTRAS").upper()
        result["confianca"] = min(100, max(0, result.get("confianca", 50)))
        result["explicacao"] = result.get("explicacao", "Classificação automática")
        result["subcategoria"] = result.get("subcategoria", "")
        
        return result
        
    except Exception as e:
        logger.warning(f"AI classification failed for response '{response}': {str(e)}")
        # Fallback to rule-based classification
        return classify_response_fallback(response)


def classify_response_fallback(response: str) -> Dict[str, Any]:
    """
    Fallback rule-based classification if AI fails
    
    Args:
        response: The response text to classify
        
    Returns:
        Classification result
    """
    
    response_lower = response.lower().strip()
    
    # Definir padrões para classificação
    sim_patterns = [
        r'\bsim\b', r'\bs\b', r'\byes\b', r'\bsi\b',
        r'problema', r'dificuldade', r'difícil', r'complicado',
        r'erro', r'bug', r'falha', r'travou', r'não funcionou',
        r'lento', r'demorou', r'complicou', r'confuso'
    ]
    
    nao_patterns = [
        r'\bnão\b', r'\bnao\b', r'\bno\b', r'\bn\b',
        r'fácil', r'tranquilo', r'simples', r'ok', r'\bok\b',
        r'sem problema', r'funcionou', r'normal', r'tudo bem',
        r'suave', r'beleza', r'perfeito'
    ]
    
    # Verificar padrões SIM
    sim_score = sum(1 for pattern in sim_patterns if re.search(pattern, response_lower))
    
    # Verificar padrões NÃO
    nao_score = sum(1 for pattern in nao_patterns if re.search(pattern, response_lower))
    
    # Casos especiais
    if len(response_lower) <= 2:  # Respostas muito curtas
        if response_lower in ['s', 'sim', 'si', 'yes']:
            return {"categoria": "SIM", "confianca": 90, "explicacao": "Resposta afirmativa curta", "subcategoria": ""}
        elif response_lower in ['n', 'não', 'nao', 'no']:
            return {"categoria": "NÃO", "confianca": 90, "explicacao": "Resposta negativa curta", "subcategoria": ""}
        else:
            return {"categoria": "OUTRAS", "confianca": 30, "explicacao": "Resposta muito curta e ambígua", "subcategoria": ""}
    
    # Decisão baseada em pontuação
    if sim_score > nao_score:
        return {"categoria": "SIM", "confianca": min(80, 50 + sim_score * 10), "explicacao": "Indica problemas/dificuldades", "subcategoria": ""}
    elif nao_score > sim_score:
        return {"categoria": "NÃO", "confianca": min(80, 50 + nao_score * 10), "explicacao": "Indica ausência de problemas", "subcategoria": ""}
    else:
        return {"categoria": "OUTRAS", "confianca": 40, "explicacao": "Resposta ambígua ou neutra", "subcategoria": ""}


def classify_question_responses(question_data: Dict[str, Any], question_context: str = "") -> Dict[str, Any]:
    """
    Classify all responses for a specific question
    
    Args:
        question_data: Question data from survey analysis
        question_context: Context about the question
        
    Returns:
        Classified responses with statistics
    """
    
    logger.info(f"Classifying responses for question: {question_context}")
    
    responses = question_data.get("responses", [])
    frequency_analysis = question_data.get("frequency_analysis", {})
    
    classified_responses = {}
    category_stats = defaultdict(lambda: {"count": 0, "percentage": 0.0, "responses": []})
    
    total_responses = len(responses)
    
    # Classificar cada resposta única baseada na frequency_analysis
    for response_text, freq_data in frequency_analysis.items():
        classification = classify_response_with_ai(response_text, question_context)
        
        category = classification["categoria"]
        count = freq_data["count"]
        
        classified_responses[response_text] = classification
        category_stats[category]["count"] += count
        category_stats[category]["responses"].append({
            "text": response_text,
            "count": count,
            "classification": classification
        })
    
    # Calcular percentuais
    for category in category_stats:
        if total_responses > 0:
            category_stats[category]["percentage"] = round(
                (category_stats[category]["count"] / total_responses) * 100, 2
            )
    
    # Gerar resumo
    classification_summary = {
        "total_responses": total_responses,
        "categories": dict(category_stats),
        "classification_details": classified_responses,
        "confidence_avg": round(
            sum(c["confianca"] for c in classified_responses.values()) / len(classified_responses)
            if classified_responses else 0, 1
        ),
        "processed_at": datetime.now().isoformat()
    }
    
    # Log resultados
    logger.info(f"Classification completed:")
    for category, stats in category_stats.items():
        logger.info(f"  {category}: {stats['count']} ({stats['percentage']}%)")
    
    return classification_summary


def create_simplified_frequency_analysis(classification_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a simplified frequency analysis with only the main categories
    
    Args:
        classification_summary: Results from classify_question_responses
        
    Returns:
        Simplified frequency analysis for chart generation
    """
    
    categories = classification_summary.get("categories", {})
    total_responses = classification_summary.get("total_responses", 0)
    
    simplified_freq = {}
    
    for category, stats in categories.items():
        if stats["count"] > 0:
            simplified_freq[category] = {
                "count": stats["count"],
                "percentage": stats["percentage"]
            }
    
    return simplified_freq


def enhance_question_with_classification(question_data: Dict[str, Any], question_name: str) -> Dict[str, Any]:
    """
    Enhance question data with AI classification for clearer visualization
    
    Args:
        question_data: Original question data
        question_name: Name/ID of the question
        
    Returns:
        Enhanced question data with classification
    """
    
    # Determine if this question needs classification
    question_type = question_data.get("question_type", "")
    total_responses = question_data.get("total_responses", 0)
    
    # Only classify questions that would benefit from it
    if total_responses == 0:
        return question_data
    
    # Specific logic for question 8 (problems/difficulties)
    if "screen8" in question_name or "problema" in question_name.lower():
        question_context = "8 - Você teve algum problema ou dificuldade para participar?"
        
        # Perform classification
        classification_summary = classify_question_responses(question_data, question_context)
        
        # Create simplified frequency analysis
        simplified_freq = create_simplified_frequency_analysis(classification_summary)
        
        # Enhanced question data
        enhanced_data = question_data.copy()
        enhanced_data.update({
            "original_frequency_analysis": question_data.get("frequency_analysis", {}),
            "frequency_analysis": simplified_freq,  # Replace with simplified version
            "classification_summary": classification_summary,
            "question_type": "yes_no",  # Change to yes_no for better chart type
            "enhanced_with_ai": True,
            "enhancement_timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Enhanced question {question_name} with AI classification")
        return enhanced_data
    
    # Return original data for other questions
    return question_data


def enhance_survey_data_with_classification(survey_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance entire survey data with AI classification where appropriate
    
    Args:
        survey_data: Complete survey data
        
    Returns:
        Enhanced survey data
    """
    
    logger.info("Enhancing survey data with AI classification...")
    
    enhanced_survey = survey_data.copy()
    questions = enhanced_survey.get("survey_questions", {})
    
    enhanced_questions = {}
    classification_applied = []
    
    for question_name, question_data in questions.items():
        enhanced_question = enhance_question_with_classification(question_data, question_name)
        enhanced_questions[question_name] = enhanced_question
        
        if enhanced_question.get("enhanced_with_ai", False):
            classification_applied.append(question_name)
    
    enhanced_survey["survey_questions"] = enhanced_questions
    enhanced_survey["ai_classification_applied"] = classification_applied
    enhanced_survey["enhancement_summary"] = {
        "total_questions": len(questions),
        "questions_enhanced": len(classification_applied),
        "enhanced_at": datetime.now().isoformat()
    }
    
    logger.info(f"AI classification applied to {len(classification_applied)} questions")
    
    return enhanced_survey


# Agent factory function
async def get_response_classifier_agent(**kwargs):
    """Factory function to create response classifier agent"""
    return await create_agent("response-classifier-agent", **kwargs) 