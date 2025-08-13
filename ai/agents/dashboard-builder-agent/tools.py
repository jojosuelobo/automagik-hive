"""
Dashboard Builder Tools - Professional Report Generation Utilities
=================================================================

Advanced utilities for creating professional dashboards, executive reports,
and stakeholder presentations with business intelligence capabilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
import json
import base64
import io
from datetime import datetime
from collections import defaultdict, Counter
import statistics
import re

from lib.logging import logger


def calculate_statistical_significance(data1: List[Any], data2: List[Any], 
                                     test_type: str = "auto") -> Dict[str, Any]:
    """
    Calculate statistical significance between two datasets
    
    Args:
        data1: First dataset
        data2: Second dataset
        test_type: Type of statistical test ("auto", "t_test", "chi_square")
        
    Returns:
        Statistical test results
    """
    try:
        from scipy import stats
        
        # Clean and convert data
        clean_data1 = [val for val in data1 if val is not None]
        clean_data2 = [val for val in data2 if val is not None]
        
        if len(clean_data1) < 3 or len(clean_data2) < 3:
            return {
                "test_performed": "none",
                "reason": "Insufficient sample size",
                "p_value": None,
                "significant": False
            }
        
        # Try to convert to numeric for t-test
        try:
            numeric_data1 = [float(val) for val in clean_data1]
            numeric_data2 = [float(val) for val in clean_data2]
            
            # Perform t-test
            statistic, p_value = stats.ttest_ind(numeric_data1, numeric_data2)
            
            return {
                "test_performed": "t_test",
                "statistic": float(statistic),
                "p_value": float(p_value),
                "significant": p_value < 0.05,
                "effect_size": abs(np.mean(numeric_data1) - np.mean(numeric_data2)) / np.sqrt((np.var(numeric_data1) + np.var(numeric_data2)) / 2),
                "interpretation": "Statistically significant difference" if p_value < 0.05 else "No significant difference"
            }
            
        except (ValueError, TypeError):
            # Perform chi-square test for categorical data
            combined_values = list(set(str(val) for val in clean_data1 + clean_data2))
            
            counts1 = [clean_data1.count(val) for val in combined_values]
            counts2 = [clean_data2.count(val) for val in combined_values]
            
            contingency_table = [counts1, counts2]
            
            statistic, p_value, dof, expected = stats.chi2_contingency(contingency_table)
            
            return {
                "test_performed": "chi_square",
                "statistic": float(statistic),
                "p_value": float(p_value),
                "degrees_of_freedom": int(dof),
                "significant": p_value < 0.05,
                "interpretation": "Statistically significant association" if p_value < 0.05 else "No significant association"
            }
            
    except ImportError:
        return {
            "test_performed": "none",
            "reason": "scipy not available",
            "p_value": None,
            "significant": False
        }
    except Exception as e:
        return {
            "test_performed": "error",
            "reason": str(e),
            "p_value": None,
            "significant": False
        }


def identify_key_patterns(dataset: Dict[str, List[Any]], 
                         classifications: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Identify key patterns and insights in the dataset
    
    Args:
        dataset: Dictionary mapping column names to data lists
        classifications: Data type classifications
        
    Returns:
        List of identified patterns and insights
    """
    patterns = []
    
    try:
        column_classifications = classifications.get("classifications", {})
        
        # Pattern 1: High completion rates
        high_completion_columns = []
        for col_name, data in dataset.items():
            completion_rate = len([val for val in data if val is not None and str(val).strip() != '']) / len(data) * 100
            if completion_rate > 90:
                high_completion_columns.append((col_name, completion_rate))
        
        if high_completion_columns:
            patterns.append({
                "type": "completion_rate",
                "title": "High Response Rate Questions",
                "description": f"Found {len(high_completion_columns)} questions with >90% completion rate",
                "details": [f"{col}: {rate:.1f}%" for col, rate in high_completion_columns[:5]],
                "business_impact": "High engagement indicates important topics to respondents",
                "confidence": "high"
            })
        
        # Pattern 2: Skewed distributions in numerical data
        for col_name, data in dataset.items():
            classification = column_classifications.get(col_name, {})
            if classification.get("primary_type") == "numerical":
                try:
                    numeric_data = [float(val) for val in data if val is not None and str(val).replace('.', '').replace('-', '').isdigit()]
                    if len(numeric_data) > 10:
                        skewness = statistics.mode([round(val) for val in numeric_data])
                        mean_val = statistics.mean(numeric_data)
                        
                        if abs(skewness - mean_val) > statistics.stdev(numeric_data):
                            patterns.append({
                                "type": "distribution_skew",
                                "title": f"Skewed Distribution in {col_name}",
                                "description": f"Data shows significant skew with mode at {skewness:.2f} vs mean at {mean_val:.2f}",
                                "business_impact": "May indicate polarized opinions or measurement bias",
                                "confidence": "medium"
                            })
                except (ValueError, statistics.StatisticsError):
                    pass
        
        # Pattern 3: Categorical dominance
        for col_name, data in dataset.items():
            classification = column_classifications.get(col_name, {})
            if classification.get("primary_type") == "categorical":
                clean_data = [str(val) for val in data if val is not None and str(val).strip() != '']
                if clean_data:
                    value_counts = Counter(clean_data)
                    most_common = value_counts.most_common(1)[0]
                    dominance_ratio = most_common[1] / len(clean_data)
                    
                    if dominance_ratio > 0.7:
                        patterns.append({
                            "type": "categorical_dominance",
                            "title": f"Strong Preference in {col_name}",
                            "description": f"'{most_common[0]}' accounts for {dominance_ratio:.1%} of responses",
                            "business_impact": "Clear consensus or preference among respondents",
                            "confidence": "high"
                        })
        
        # Pattern 4: Low variance in scales
        for col_name, data in dataset.items():
            classification = column_classifications.get(col_name, {})
            if classification.get("sub_type") == "ordinal":
                try:
                    numeric_data = [float(val) for val in data if val is not None and str(val).isdigit()]
                    if len(numeric_data) > 5:
                        variance = statistics.variance(numeric_data)
                        data_range = max(numeric_data) - min(numeric_data)
                        
                        if variance < (data_range * 0.1):  # Low variance relative to range
                            patterns.append({
                                "type": "low_variance",
                                "title": f"Consistent Ratings in {col_name}",
                                "description": f"Low variance ({variance:.2f}) indicates consistent responses",
                                "business_impact": "Strong agreement or satisfaction among respondents",
                                "confidence": "medium"
                            })
                except (ValueError, statistics.StatisticsError):
                    pass
        
        logger.info(f"🔍 Identified {len(patterns)} key patterns in the dataset")
        
    except Exception as e:
        logger.error(f"❌ Pattern identification failed: {str(e)}")
        patterns.append({
            "type": "error",
            "title": "Pattern Analysis Error",
            "description": f"Failed to identify patterns: {str(e)}",
            "confidence": "low"
        })
    
    return patterns


def generate_business_recommendations(patterns: List[Dict[str, Any]], 
                                   data_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate actionable business recommendations based on identified patterns
    
    Args:
        patterns: Identified data patterns
        data_summary: Dataset summary statistics
        
    Returns:
        List of business recommendations
    """
    recommendations = []
    
    try:
        # Recommendation based on completion rates
        high_completion_patterns = [p for p in patterns if p.get("type") == "completion_rate"]
        if high_completion_patterns:
            recommendations.append({
                "priority": "High",
                "category": "Survey Design",
                "title": "Leverage High-Engagement Questions",
                "description": "Questions with >90% completion rates indicate topics of high interest to respondents",
                "action_items": [
                    "Expand on high-completion topics in future surveys",
                    "Use these questions as templates for survey design",
                    "Consider these topics for detailed follow-up research"
                ],
                "expected_impact": "Improved response rates and data quality",
                "implementation_effort": "Low",
                "timeframe": "Immediate",
                "success_metrics": ["Response rate improvement", "Survey completion time"]
            })
        
        # Recommendation based on categorical dominance
        dominance_patterns = [p for p in patterns if p.get("type") == "categorical_dominance"]
        if dominance_patterns:
            recommendations.append({
                "priority": "Medium",
                "category": "Business Strategy",
                "title": "Act on Clear Preferences",
                "description": f"Found {len(dominance_patterns)} areas with strong consensus (>70% agreement)",
                "action_items": [
                    "Prioritize initiatives aligned with majority preferences",
                    "Investigate minority preferences for potential opportunities",
                    "Develop communication strategies around consensus areas"
                ],
                "expected_impact": "Better alignment with customer/stakeholder preferences",
                "implementation_effort": "Medium",
                "timeframe": "Short-term",
                "success_metrics": ["Customer satisfaction", "Initiative success rate"]
            })
        
        # Recommendation based on low variance
        low_variance_patterns = [p for p in patterns if p.get("type") == "low_variance"]
        if low_variance_patterns:
            recommendations.append({
                "priority": "Medium",
                "category": "Quality Assurance",
                "title": "Maintain Consistent Performance",
                "description": "Identified areas with consistently positive ratings - maintain current performance",
                "action_items": [
                    "Document best practices for consistent areas",
                    "Use as benchmarks for other initiatives",
                    "Monitor for any degradation in performance"
                ],
                "expected_impact": "Sustained high performance and satisfaction",
                "implementation_effort": "Low",
                "timeframe": "Ongoing",
                "success_metrics": ["Performance consistency", "Satisfaction stability"]
            })
        
        # Recommendation based on data quality
        total_columns = data_summary.get("total_columns", 0)
        if total_columns > 10:
            recommendations.append({
                "priority": "High",
                "category": "Data Strategy",
                "title": "Establish Regular Reporting",
                "description": f"With {total_columns} data points, establish systematic reporting and monitoring",
                "action_items": [
                    "Create automated dashboard for key metrics",
                    "Set up regular reporting schedule",
                    "Define data quality standards and monitoring",
                    "Train stakeholders on data interpretation"
                ],
                "expected_impact": "Improved decision-making through regular data insights",
                "implementation_effort": "High",
                "timeframe": "Medium-term",
                "success_metrics": ["Dashboard usage", "Data-driven decisions", "Response time to issues"]
            })
        
        # General recommendation for text analysis
        text_columns = sum(1 for col_summary in data_summary.get("column_summaries", {}).values()
                          if "most_common" in col_summary)  # Indicates text/categorical data
        
        if text_columns > 2:
            recommendations.append({
                "priority": "Medium",
                "category": "Analytics Enhancement",
                "title": "Implement Advanced Text Analysis",
                "description": f"Found {text_columns} text/categorical fields suitable for deeper analysis",
                "action_items": [
                    "Implement sentiment analysis on open-ended responses",
                    "Use natural language processing for theme identification",
                    "Create automated categorization of feedback",
                    "Develop text-based early warning systems"
                ],
                "expected_impact": "Deeper insights from qualitative data",
                "implementation_effort": "High",
                "timeframe": "Long-term",
                "success_metrics": ["Insight quality", "Theme identification accuracy"]
            })
        
        # Sort recommendations by priority
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "Medium"), 2))
        
        logger.info(f"💡 Generated {len(recommendations)} business recommendations")
        
    except Exception as e:
        logger.error(f"❌ Recommendation generation failed: {str(e)}")
        recommendations.append({
            "priority": "Low",
            "category": "Technical",
            "title": "Review Analysis Process",
            "description": f"Recommendation generation encountered issues: {str(e)}",
            "action_items": ["Review data quality", "Check analysis parameters"],
            "expected_impact": "Improved analysis reliability",
            "implementation_effort": "Low",
            "timeframe": "Immediate"
        })
    
    return recommendations


def create_executive_summary_text(data_summary: Dict[str, Any], patterns: List[Dict[str, Any]], 
                                recommendations: List[Dict[str, Any]]) -> str:
    """
    Create executive summary text from analysis results
    
    Args:
        data_summary: Dataset summary statistics
        patterns: Identified patterns
        recommendations: Generated recommendations
        
    Returns:
        Executive summary text
    """
    try:
        summary_parts = []
        
        # Opening statement
        total_columns = data_summary.get("total_columns", 0)
        summary_parts.append(f"**Survey Analysis Summary:** Comprehensive analysis of {total_columns} survey questions completed successfully.")
        
        # Data quality assessment
        column_summaries = data_summary.get("column_summaries", {})
        avg_completion = np.mean([100 - summary.get("null_percentage", 100) 
                                 for summary in column_summaries.values()])
        
        summary_parts.append(f"**Data Quality:** Average response completion rate of {avg_completion:.1f}%, indicating strong survey engagement.")
        
        # Key findings
        if patterns:
            high_confidence_patterns = [p for p in patterns if p.get("confidence") == "high"]
            summary_parts.append(f"**Key Findings:** Identified {len(patterns)} significant patterns, with {len(high_confidence_patterns)} high-confidence insights.")
            
            # Highlight most important pattern
            if high_confidence_patterns:
                top_pattern = high_confidence_patterns[0]
                summary_parts.append(f"**Primary Insight:** {top_pattern.get('description', 'Significant pattern identified')}.")
        
        # Recommendations
        if recommendations:
            high_priority_recs = [r for r in recommendations if r.get("priority") in ["Critical", "High"]]
            summary_parts.append(f"**Recommendations:** {len(recommendations)} actionable recommendations generated, including {len(high_priority_recs)} high-priority initiatives.")
            
            # Highlight top recommendation
            if high_priority_recs:
                top_rec = high_priority_recs[0]
                summary_parts.append(f"**Priority Action:** {top_rec.get('title', 'Key recommendation identified')} - {top_rec.get('description', '')}.")
        
        # Conclusion
        summary_parts.append("**Next Steps:** Review detailed findings and begin implementation of high-priority recommendations to maximize business impact.")
        
        executive_summary = " ".join(summary_parts)
        
        logger.info(f"📝 Generated executive summary: {len(executive_summary)} characters")
        return executive_summary
        
    except Exception as e:
        logger.error(f"❌ Executive summary generation failed: {str(e)}")
        return f"Survey analysis completed with {data_summary.get('total_columns', 0)} questions analyzed. Detailed results available in the dashboard. Error in summary generation: {str(e)}"


def format_data_quality_report(data_summary: Dict[str, Any], 
                             classifications: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format comprehensive data quality report
    
    Args:
        data_summary: Dataset summary statistics
        classifications: Data type classifications
        
    Returns:
        Formatted data quality report
    """
    report = {
        "generation_timestamp": datetime.now().isoformat(),
        "overall_quality_score": 0,
        "quality_dimensions": {},
        "column_quality": {},
        "recommendations": [],
        "summary": ""
    }
    
    try:
        column_summaries = data_summary.get("column_summaries", {})
        column_classifications = classifications.get("classifications", {})
        
        # Calculate overall quality metrics
        completeness_scores = []
        consistency_scores = []
        classification_scores = []
        
        for col_name, summary in column_summaries.items():
            # Completeness
            completeness = 100 - summary.get("null_percentage", 100)
            completeness_scores.append(completeness)
            
            # Consistency (based on unique ratio for categorical data)
            unique_ratio = summary.get("unique_ratio", 0)
            if unique_ratio < 0.1:  # Low unique ratio = high consistency for categorical
                consistency_scores.append(90)
            elif unique_ratio < 0.5:
                consistency_scores.append(70)
            else:
                consistency_scores.append(50)
            
            # Classification confidence
            classification = column_classifications.get(col_name, {})
            confidence = classification.get("confidence", 0) * 100
            classification_scores.append(confidence)
            
            # Column-specific quality
            report["column_quality"][col_name] = {
                "completeness": completeness,
                "consistency": consistency_scores[-1],
                "classification_confidence": confidence,
                "overall_score": (completeness + consistency_scores[-1] + confidence) / 3,
                "issues": []
            }
            
            # Identify issues
            if completeness < 70:
                report["column_quality"][col_name]["issues"].append("Low completion rate")
            if confidence < 60:
                report["column_quality"][col_name]["issues"].append("Uncertain data type classification")
        
        # Calculate dimension scores
        report["quality_dimensions"] = {
            "completeness": np.mean(completeness_scores) if completeness_scores else 0,
            "consistency": np.mean(consistency_scores) if consistency_scores else 0,
            "classification_accuracy": np.mean(classification_scores) if classification_scores else 0
        }
        
        # Overall quality score
        report["overall_quality_score"] = np.mean(list(report["quality_dimensions"].values()))
        
        # Generate recommendations based on quality issues
        if report["quality_dimensions"]["completeness"] < 80:
            report["recommendations"].append({
                "area": "Data Completeness",
                "issue": "Low response rates detected",
                "recommendation": "Review survey design and distribution methods",
                "priority": "High"
            })
        
        if report["quality_dimensions"]["classification_accuracy"] < 70:
            report["recommendations"].append({
                "area": "Data Classification",
                "issue": "Uncertain data type classifications",
                "recommendation": "Review data formats and consider manual validation",
                "priority": "Medium"
            })
        
        # Generate summary
        quality_level = "Excellent" if report["overall_quality_score"] > 90 else \
                       "Good" if report["overall_quality_score"] > 75 else \
                       "Fair" if report["overall_quality_score"] > 60 else "Poor"
        
        report["summary"] = f"Overall data quality: {quality_level} ({report['overall_quality_score']:.1f}/100). " \
                           f"Completeness: {report['quality_dimensions']['completeness']:.1f}%, " \
                           f"Consistency: {report['quality_dimensions']['consistency']:.1f}%, " \
                           f"Classification Accuracy: {report['quality_dimensions']['classification_accuracy']:.1f}%."
        
        logger.info(f"📊 Data quality report generated: {quality_level} quality ({report['overall_quality_score']:.1f}/100)")
        
    except Exception as e:
        logger.error(f"❌ Data quality report generation failed: {str(e)}")
        report["error"] = str(e)
        report["summary"] = f"Data quality assessment failed: {str(e)}"
    
    return report


def export_analysis_package(analysis_results: Dict[str, Any], 
                          output_dir: str = "survey_analysis_package") -> Dict[str, Any]:
    """
    Export complete analysis package with all deliverables
    
    Args:
        analysis_results: Complete analysis results
        output_dir: Output directory for package
        
    Returns:
        Export summary and file list
    """
    from pathlib import Path
    import json
    import zipfile
    
    try:
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        export_summary = {
            "export_timestamp": datetime.now().isoformat(),
            "output_directory": str(output_path.absolute()),
            "files_created": [],
            "package_contents": {}
        }
        
        # Export interactive dashboard
        if "interactive_dashboard" in analysis_results:
            dashboard_file = output_path / "interactive_dashboard.html"
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(analysis_results["interactive_dashboard"])
            
            export_summary["files_created"].append({
                "filename": "interactive_dashboard.html",
                "type": "dashboard",
                "description": "Interactive HTML dashboard with visualizations"
            })
        
        # Export PDF report
        if "pdf_report" in analysis_results:
            pdf_data = base64.b64decode(analysis_results["pdf_report"])
            pdf_file = output_path / "executive_report.pdf"
            with open(pdf_file, 'wb') as f:
                f.write(pdf_data)
            
            export_summary["files_created"].append({
                "filename": "executive_report.pdf",
                "type": "report",
                "description": "Executive summary PDF report"
            })
        
        # Export analysis data as JSON
        analysis_json = output_path / "analysis_results.json"
        with open(analysis_json, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        export_summary["files_created"].append({
            "filename": "analysis_results.json",
            "type": "data",
            "description": "Complete analysis results in JSON format"
        })
        
        # Create README
        readme_content = f"""# Survey Analysis Package
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Package Contents

### Interactive Dashboard (interactive_dashboard.html)
Open this file in a web browser to view the interactive dashboard with all visualizations and insights.

### Executive Report (executive_report.pdf)
Professional PDF report with executive summary, key findings, and recommendations.

### Analysis Data (analysis_results.json)
Complete analysis results in JSON format for further processing or integration.

## Key Findings Summary
{analysis_results.get('executive_insights', {}).get('executive_summary', 'Analysis completed successfully.')}

## Recommendations Count
{len(analysis_results.get('executive_insights', {}).get('business_recommendations', []))} actionable recommendations generated.

## Usage Instructions
1. Open interactive_dashboard.html in a web browser for interactive exploration
2. Share executive_report.pdf with stakeholders for decision-making
3. Use analysis_results.json for further data processing or system integration

Generated by Survey Data Visualization Workflow
"""
        
        readme_file = output_path / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        export_summary["files_created"].append({
            "filename": "README.md",
            "type": "documentation",
            "description": "Package documentation and usage instructions"
        })
        
        # Create ZIP package
        zip_file = output_path.parent / f"{output_path.name}.zip"
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_info in export_summary["files_created"]:
                file_path = output_path / file_info["filename"]
                if file_path.exists():
                    zipf.write(file_path, file_info["filename"])
        
        export_summary["files_created"].append({
            "filename": f"{output_path.name}.zip",
            "type": "package",
            "description": "Complete analysis package in ZIP format"
        })
        
        # Package summary
        export_summary["package_contents"] = {
            "dashboard": "Interactive web dashboard",
            "report": "Executive PDF report",
            "data": "JSON analysis results",
            "documentation": "Usage instructions",
            "package": "Complete ZIP archive"
        }
        
        logger.info(f"📦 Analysis package exported: {len(export_summary['files_created'])} files created")
        return export_summary
        
    except Exception as e:
        logger.error(f"❌ Package export failed: {str(e)}")
        return {
            "export_timestamp": datetime.now().isoformat(),
            "error": str(e),
            "files_created": []
        }


# Export all utility functions
__all__ = [
    "calculate_statistical_significance",
    "identify_key_patterns",
    "generate_business_recommendations",
    "create_executive_summary_text",
    "format_data_quality_report",
    "export_analysis_package"
]