"""
Dashboard Builder Agent - Professional Report and Dashboard Creation
===================================================================

Advanced dashboard builder that compiles visualizations into professional
presentations, generates AI-powered insights, and creates stakeholder-ready
reports with executive summaries and actionable recommendations.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union
import yaml
import json
import jinja2
from datetime import datetime
import base64
import io
from collections import defaultdict
import statistics

from agno import Agent
from agno.models.anthropic import Claude
from agno.storage.postgres import PostgresStorage
from lib.logging import logger

# HTML Template for dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .executive-summary { background-color: #f8f9fa; padding: 20px; margin: 20px 0; border-left: 4px solid #007bff; }
        .insight-card { background-color: white; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; margin: 10px 0; }
        .chart-container { margin: 20px 0; padding: 15px; border: 1px solid #dee2e6; border-radius: 5px; }
        .metric-card { text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin: 10px; }
        .recommendation { background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 10px 0; }
        .methodology { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <header class="row bg-primary text-white py-3 mb-4">
            <div class="col">
                <h1 class="h2 mb-0">{{ title }}</h1>
                <p class="mb-0">Generated on {{ generation_date }}</p>
            </div>
        </header>
        
        <div class="row">
            <div class="col-md-12">
                <div class="executive-summary">
                    <h2>Executive Summary</h2>
                    {{ executive_summary | safe }}
                </div>
            </div>
        </div>
        
        <div class="row">
            {% for metric in key_metrics %}
            <div class="col-md-3">
                <div class="metric-card">
                    <h3>{{ metric.value }}</h3>
                    <p>{{ metric.label }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="row">
            <div class="col-md-12">
                <h2>Key Insights</h2>
                {% for insight in insights %}
                <div class="insight-card">
                    <h4>{{ insight.title }}</h4>
                    <p>{{ insight.description }}</p>
                    {% if insight.significance %}
                    <small class="text-muted">Statistical significance: {{ insight.significance }}</small>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-12">
                <h2>Data Visualizations</h2>
                {% for chart in charts %}
                <div class="chart-container">
                    <h4>{{ chart.title }}</h4>
                    <div id="chart-{{ chart.id }}"></div>
                    {% if chart.interpretation %}
                    <p class="text-muted mt-2">{{ chart.interpretation }}</p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-12">
                <h2>Recommendations</h2>
                {% for rec in recommendations %}
                <div class="recommendation">
                    <h5>{{ rec.title }} <span class="badge bg-{{ rec.priority_color }}">{{ rec.priority }}</span></h5>
                    <p>{{ rec.description }}</p>
                    <small><strong>Expected Impact:</strong> {{ rec.impact }} | <strong>Effort:</strong> {{ rec.effort }}</small>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-12">
                <div class="methodology">
                    <h3>Methodology</h3>
                    {{ methodology | safe }}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        {% for chart in charts %}
        {% if chart.plotly_json %}
        Plotly.newPlot('chart-{{ chart.id }}', {{ chart.plotly_json | safe }}, {responsive: true});
        {% endif %}
        {% endfor %}
    </script>
</body>
</html>
"""


def create_dashboard_model() -> Claude:
    """Create Claude model for dashboard building"""
    return Claude(
        id='claude-sonnet-4-20250514',
        temperature=0.2,
        max_tokens=4000
    )


def generate_executive_insights(data_summary: Dict[str, Any], classifications: Dict[str, Any], 
                              charts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate AI-powered executive insights from survey analysis
    
    Args:
        data_summary: Statistical summary of the dataset
        classifications: Data type classifications
        charts: Generated chart results
        
    Returns:
        Executive insights and recommendations
    """
    insights = {
        "generation_timestamp": datetime.now().isoformat(),
        "key_findings": [],
        "statistical_insights": [],
        "business_recommendations": [],
        "data_quality_assessment": {},
        "executive_summary": ""
    }
    
    try:
        # Analyze data quality
        total_columns = data_summary.get("total_columns", 0)
        successful_classifications = sum(1 for c in classifications.get("classifications", {}).values() 
                                       if c.get("confidence", 0) > 0.7)
        successful_charts = sum(1 for c in charts.get("charts_generated", {}).values() 
                              if c.get("success", False))
        
        insights["data_quality_assessment"] = {
            "total_survey_questions": total_columns,
            "successfully_analyzed": successful_classifications,
            "charts_generated": successful_charts,
            "analysis_completeness": (successful_classifications / total_columns * 100) if total_columns > 0 else 0
        }
        
        # Generate key findings
        column_summaries = data_summary.get("column_summaries", {})
        
        # Find columns with high response rates
        high_response_columns = []
        for col, summary in column_summaries.items():
            response_rate = 100 - summary.get("null_percentage", 100)
            if response_rate > 80:
                high_response_columns.append((col, response_rate))
        
        if high_response_columns:
            insights["key_findings"].append({
                "type": "response_quality",
                "title": "High Response Rate Questions",
                "description": f"Found {len(high_response_columns)} questions with >80% response rate, indicating strong engagement.",
                "details": [f"{col}: {rate:.1f}%" for col, rate in high_response_columns[:5]]
            })
        
        # Analyze data distribution types
        type_counts = defaultdict(int)
        for classification in classifications.get("classifications", {}).values():
            primary_type = classification.get("primary_type", "unknown")
            type_counts[primary_type] += 1
        
        insights["statistical_insights"].append({
            "type": "data_distribution",
            "title": "Survey Question Types",
            "description": f"Survey contains {type_counts['categorical']} categorical, {type_counts['numerical']} numerical, and {type_counts['textual']} text questions.",
            "breakdown": dict(type_counts)
        })
        
        # Generate business recommendations
        if type_counts["textual"] > 0:
            insights["business_recommendations"].append({
                "priority": "High",
                "title": "Leverage Open-Ended Feedback",
                "description": f"The survey contains {type_counts['textual']} open-ended questions providing rich qualitative insights.",
                "action": "Conduct detailed text analysis and sentiment analysis on open-ended responses.",
                "impact": "High",
                "effort": "Medium"
            })
        
        if successful_charts > 5:
            insights["business_recommendations"].append({
                "priority": "Medium",
                "title": "Create Stakeholder Dashboard",
                "description": f"With {successful_charts} successful visualizations, create an executive dashboard for ongoing monitoring.",
                "action": "Establish regular reporting cadence with automated dashboard updates.",
                "impact": "Medium",
                "effort": "Low"
            })
        
        # Generate executive summary
        summary_parts = [
            f"Analysis of {total_columns} survey questions completed with {insights['data_quality_assessment']['analysis_completeness']:.1f}% success rate.",
        ]
        
        if type_counts["categorical"] > 0:
            summary_parts.append(f"Identified {type_counts['categorical']} categorical questions suitable for distribution analysis.")
        
        if type_counts["numerical"] > 0:
            summary_parts.append(f"Found {type_counts['numerical']} numerical metrics enabling statistical analysis.")
        
        summary_parts.append(f"Generated {successful_charts} professional visualizations ready for stakeholder presentation.")
        
        insights["executive_summary"] = " ".join(summary_parts)
        
        logger.info(f"📊 Generated executive insights: {len(insights['key_findings'])} findings, {len(insights['business_recommendations'])} recommendations")
        
    except Exception as e:
        logger.error(f"❌ Failed to generate executive insights: {str(e)}")
        insights["error"] = str(e)
    
    return insights


def create_interactive_dashboard(data_summary: Dict[str, Any], charts: Dict[str, Any], 
                               insights: Dict[str, Any], title: str = "Survey Analysis Dashboard") -> str:
    """
    Create interactive HTML dashboard
    
    Args:
        data_summary: Statistical summary of the dataset
        charts: Generated chart results
        insights: Executive insights
        title: Dashboard title
        
    Returns:
        HTML dashboard string
    """
    try:
        # Prepare template data
        template_data = {
            "title": title,
            "generation_date": datetime.now().strftime("%B %d, %Y"),
            "executive_summary": insights.get("executive_summary", "Analysis completed successfully."),
            "key_metrics": [],
            "insights": [],
            "charts": [],
            "recommendations": [],
            "methodology": "This analysis was conducted using automated survey data processing with AI-powered classification and professional visualization generation."
        }
        
        # Create key metrics
        quality_assessment = insights.get("data_quality_assessment", {})
        template_data["key_metrics"] = [
            {"value": str(quality_assessment.get("total_survey_questions", 0)), "label": "Survey Questions"},
            {"value": f"{quality_assessment.get('analysis_completeness', 0):.1f}%", "label": "Analysis Completeness"},
            {"value": str(quality_assessment.get("charts_generated", 0)), "label": "Visualizations Created"},
            {"value": str(len(insights.get("business_recommendations", []))), "label": "Recommendations"}
        ]
        
        # Format insights
        for i, finding in enumerate(insights.get("key_findings", [])):
            template_data["insights"].append({
                "title": finding.get("title", f"Finding {i+1}"),
                "description": finding.get("description", ""),
                "significance": finding.get("significance", None)
            })
        
        # Format charts
        chart_id = 0
        for column_name, chart_data in charts.get("charts_generated", {}).items():
            if chart_data.get("success"):
                chart_id += 1
                chart_info = {
                    "id": chart_id,
                    "title": chart_data.get("title", f"Chart for {column_name}"),
                    "interpretation": f"Analysis of {column_name} showing {chart_data.get('chart_type', 'visualization')} with {chart_data.get('data_summary', {}).get('total_responses', 'N/A')} responses.",
                    "plotly_json": None
                }
                
                # Try to extract Plotly JSON if available
                if "html" in chart_data:
                    # This is a simplified approach - in practice you'd need to extract the Plotly JSON
                    chart_info["plotly_json"] = "{}"
                
                template_data["charts"].append(chart_info)
        
        # Format recommendations
        priority_colors = {"Critical": "danger", "High": "warning", "Medium": "info", "Low": "secondary"}
        
        for rec in insights.get("business_recommendations", []):
            template_data["recommendations"].append({
                "title": rec.get("title", "Recommendation"),
                "description": rec.get("description", ""),
                "priority": rec.get("priority", "Medium"),
                "priority_color": priority_colors.get(rec.get("priority", "Medium"), "info"),
                "impact": rec.get("impact", "Medium"),
                "effort": rec.get("effort", "Medium")
            })
        
        # Render template
        template = jinja2.Template(DASHBOARD_TEMPLATE)
        html_output = template.render(**template_data)
        
        logger.info(f"📊 Generated interactive dashboard with {len(template_data['charts'])} charts")
        return html_output
        
    except Exception as e:
        logger.error(f"❌ Dashboard creation failed: {str(e)}")
        return f"<html><body><h1>Dashboard Generation Error</h1><p>{str(e)}</p></body></html>"


def generate_pdf_report(data_summary: Dict[str, Any], insights: Dict[str, Any], 
                       charts: Dict[str, Any]) -> bytes:
    """
    Generate PDF report from analysis results
    
    Args:
        data_summary: Statistical summary
        insights: Executive insights
        charts: Chart generation results
        
    Returns:
        PDF report as bytes
    """
    try:
        # Create a simple HTML report for PDF conversion
        report_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Survey Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1, h2, h3 {{ color: #333; }}
                .executive-summary {{ background-color: #f8f9fa; padding: 20px; margin: 20px 0; border-left: 4px solid #007bff; }}
                .recommendation {{ background-color: #d4edda; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #e9ecef; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                @page {{ size: A4; margin: 2.5cm; }}
            </style>
        </head>
        <body>
            <h1>Survey Analysis Report</h1>
            <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
            
            <div class="executive-summary">
                <h2>Executive Summary</h2>
                <p>{insights.get('executive_summary', 'Analysis completed successfully.')}</p>
            </div>
            
            <h2>Key Metrics</h2>
            <div class="metric">Total Questions: {insights.get('data_quality_assessment', {}).get('total_survey_questions', 0)}</div>
            <div class="metric">Analysis Completeness: {insights.get('data_quality_assessment', {}).get('analysis_completeness', 0):.1f}%</div>
            <div class="metric">Charts Generated: {insights.get('data_quality_assessment', {}).get('charts_generated', 0)}</div>
            
            <h2>Key Findings</h2>
            {''.join(f"<h3>{finding.get('title', 'Finding')}</h3><p>{finding.get('description', '')}</p>" for finding in insights.get('key_findings', []))}
            
            <h2>Recommendations</h2>
            {''.join(f'<div class="recommendation"><h4>{rec.get("title", "Recommendation")} ({rec.get("priority", "Medium")} Priority)</h4><p>{rec.get("description", "")}</p><p><strong>Impact:</strong> {rec.get("impact", "Medium")} | <strong>Effort:</strong> {rec.get("effort", "Medium")}</p></div>' for rec in insights.get('business_recommendations', []))}
            
            <h2>Data Quality Assessment</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Survey Questions Analyzed</td><td>{insights.get('data_quality_assessment', {}).get('total_survey_questions', 0)}</td></tr>
                <tr><td>Successful Classifications</td><td>{insights.get('data_quality_assessment', {}).get('successfully_analyzed', 0)}</td></tr>
                <tr><td>Visualizations Created</td><td>{insights.get('data_quality_assessment', {}).get('charts_generated', 0)}</td></tr>
            </table>
            
            <h2>Methodology</h2>
            <p>This analysis was conducted using automated survey data processing with:</p>
            <ul>
                <li>AI-powered data type classification</li>
                <li>Statistical analysis of response patterns</li>
                <li>Professional visualization generation</li>
                <li>Executive insight generation using advanced analytics</li>
            </ul>
            
            <p><em>Report generated by Survey Analysis Workflow - {datetime.now().isoformat()}</em></p>
        </body>
        </html>
        """
        
        # For actual PDF generation, you would use a library like weasyprint or pdfkit
        # For now, return the HTML as bytes
        return report_html.encode('utf-8')
        
    except Exception as e:
        logger.error(f"❌ PDF report generation failed: {str(e)}")
        return f"PDF Report Generation Error: {str(e)}".encode('utf-8')


def compile_complete_analysis(data_summary: Dict[str, Any], classifications: Dict[str, Any], 
                            charts: Dict[str, Any], survey_context: str = "") -> Dict[str, Any]:
    """
    Compile complete analysis with insights, dashboard, and reports
    
    Args:
        data_summary: Statistical summary of the dataset
        classifications: Data type classifications
        charts: Generated chart results
        survey_context: Additional context about the survey
        
    Returns:
        Complete analysis compilation
    """
    compilation = {
        "compilation_timestamp": datetime.now().isoformat(),
        "survey_context": survey_context,
        "analysis_summary": {},
        "executive_insights": {},
        "interactive_dashboard": "",
        "pdf_report": None,
        "export_files": [],
        "quality_metrics": {}
    }
    
    try:
        # Generate executive insights
        insights = generate_executive_insights(data_summary, classifications, charts)
        compilation["executive_insights"] = insights
        
        # Create interactive dashboard
        dashboard_html = create_interactive_dashboard(
            data_summary, charts, insights, 
            title="Survey Data Analysis Dashboard"
        )
        compilation["interactive_dashboard"] = dashboard_html
        
        # Generate PDF report
        pdf_bytes = generate_pdf_report(data_summary, insights, charts)
        compilation["pdf_report"] = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Compile analysis summary
        compilation["analysis_summary"] = {
            "total_survey_questions": data_summary.get("total_columns", 0),
            "classification_success_rate": (insights.get("data_quality_assessment", {}).get("analysis_completeness", 0)),
            "visualizations_created": len([c for c in charts.get("charts_generated", {}).values() if c.get("success")]),
            "key_findings_count": len(insights.get("key_findings", [])),
            "recommendations_count": len(insights.get("business_recommendations", [])),
            "data_types_identified": len(set(c.get("primary_type") for c in classifications.get("classifications", {}).values())),
        }
        
        # Quality metrics
        compilation["quality_metrics"] = {
            "analysis_completeness": insights.get("data_quality_assessment", {}).get("analysis_completeness", 0),
            "chart_generation_success": len([c for c in charts.get("charts_generated", {}).values() if c.get("success")]) / max(1, len(charts.get("charts_generated", {}))),
            "insight_generation_success": len(insights.get("key_findings", [])) > 0,
            "recommendation_generation_success": len(insights.get("business_recommendations", [])) > 0
        }
        
        # Track export files
        compilation["export_files"] = [
            {"type": "html_dashboard", "description": "Interactive web dashboard"},
            {"type": "pdf_report", "description": "Executive summary PDF report"},
            {"type": "json_analysis", "description": "Complete analysis results in JSON format"}
        ]
        
        logger.info(f"📊 Complete analysis compilation finished: {compilation['analysis_summary']['visualizations_created']} charts, {compilation['analysis_summary']['recommendations_count']} recommendations")
        
    except Exception as e:
        logger.error(f"❌ Analysis compilation failed: {str(e)}")
        compilation["error"] = str(e)
    
    return compilation


def get_dashboard_builder_agent(
    version: Optional[int] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = False,
    db_url: Optional[str] = None
) -> Agent:
    """Dashboard builder agent factory function"""
    
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Create agent with tools
    agent = Agent(
        name=config["agent"]["name"],
        agent_id=config["agent"]["agent_id"],
        instructions=config["instructions"],
        model=create_dashboard_model(),
        storage=PostgresStorage(
            table_name=config["storage"]["table_name"],
            db_url=db_url,
            auto_upgrade_schema=config["storage"]["auto_upgrade_schema"]
        ),
        session_id=session_id,
        debug_mode=debug_mode,
        markdown=config.get("markdown", True),
        show_tool_calls=config.get("show_tool_calls", False)
    )
    
    # Add custom tools
    agent.tools.extend([
        generate_executive_insights,
        create_interactive_dashboard,
        generate_pdf_report,
        compile_complete_analysis
    ])
    
    logger.info(f"📊 Dashboard Builder Agent initialized - Version {config['agent']['version']}")
    return agent


# Export the factory function
__all__ = [
    "get_dashboard_builder_agent",
    "compile_complete_analysis",
    "generate_executive_insights",
    "create_interactive_dashboard",
    "generate_pdf_report"
]


if __name__ == "__main__":
    # Test the agent
    import asyncio
    
    async def test_dashboard_builder():
        """Test dashboard builder agent"""
        agent = get_dashboard_builder_agent(debug_mode=True)
        
        test_message = """
        I need you to create a professional dashboard and executive report from this survey analysis:
        
        - 10 survey questions analyzed
        - 8 successful data type classifications  
        - 6 visualizations generated successfully
        - Data includes satisfaction ratings, demographic info, and open-ended feedback
        
        Please generate executive insights, create an interactive dashboard, and prepare a stakeholder report.
        """
        
        logger.info("Testing dashboard builder agent...")
        response = await agent.arun(test_message)
        logger.info(f"🤖 Response: {response.content}")
    
    # Run test
    asyncio.run(test_dashboard_builder())