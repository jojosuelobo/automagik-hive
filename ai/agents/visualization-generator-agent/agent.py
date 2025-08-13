"""
Visualization Generator Agent - Professional Chart and Graph Creation
====================================================================

Advanced visualization generator that creates professional, stakeholder-ready
charts and graphs based on classified survey data with interactive features
and multiple export formats.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union
import yaml
import json
import base64
from datetime import datetime
from collections import Counter
import io

from agno import Agent
from agno.models.anthropic import Claude
from agno.storage.postgres import PostgresStorage
from lib.logging import logger

# Optional imports for additional chart types
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("⚠️ matplotlib/seaborn not available - using plotly only")

try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False
    logger.warning("⚠️ wordcloud not available - text visualizations limited")


def create_visualization_model() -> Claude:
    """Create Claude model for visualization generation"""
    return Claude(
        id='claude-sonnet-4-20250514',
        temperature=0.1,
        max_tokens=4000
    )


# Professional color palettes
COLOR_PALETTES = {
    "primary": ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D"],
    "secondary": ["#5EAFC5", "#B85A7A", "#F4A73B", "#D1654A"],
    "grayscale": ["#2D3436", "#636E72", "#B2BEC3", "#DDD"],
    "accessible": ["#1B9E77", "#D95F02", "#7570B3", "#E7298A"],
    "blues": ["#08519C", "#3182BD", "#6BAED6", "#BDD7E7"],
    "professional": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
}


def generate_pie_chart(data: Dict[str, Any], column_name: str, title: str = None) -> Dict[str, Any]:
    """
    Generate professional pie chart for categorical data
    
    Args:
        data: Data dictionary with values
        column_name: Name of the column
        title: Optional custom title
        
    Returns:
        Chart generation results
    """
    try:
        # Prepare data
        values = data.get(column_name, [])
        value_counts = Counter(str(val) for val in values if val is not None and str(val).strip() != '')
        
        if not value_counts:
            raise ValueError("No valid data for pie chart")
        
        # Limit categories for readability
        if len(value_counts) > 6:
            top_categories = dict(value_counts.most_common(5))
            other_count = sum(value_counts.values()) - sum(top_categories.values())
            if other_count > 0:
                top_categories["Others"] = other_count
            value_counts = top_categories
        
        labels = list(value_counts.keys())
        values = list(value_counts.values())
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0,
            textinfo='label+percent',
            textposition='auto',
            marker=dict(colors=COLOR_PALETTES["primary"][:len(labels)]),
            showlegend=True
        )])
        
        # Update layout
        chart_title = title or f"Distribution of {column_name}"
        fig.update_layout(
            title=dict(
                text=chart_title,
                font=dict(size=16, family="Arial"),
                x=0.5
            ),
            font=dict(family="Arial", size=12),
            width=800,
            height=600,
            margin=dict(t=80, b=40, l=40, r=40)
        )
        
        # Generate exports
        html_str = fig.to_html(include_plotlyjs='cdn')
        png_bytes = fig.to_image(format="png", width=800, height=600)
        
        result = {
            "success": True,
            "chart_type": "pie_chart",
            "column": column_name,
            "title": chart_title,
            "html": html_str,
            "png_base64": base64.b64encode(png_bytes).decode('utf-8'),
            "data_summary": {
                "categories": len(labels),
                "total_responses": sum(values),
                "most_common": labels[0] if labels else None
            },
            "generation_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"🥧 Generated pie chart for {column_name}: {len(labels)} categories")
        return result
        
    except Exception as e:
        logger.error(f"❌ Pie chart generation failed for {column_name}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "chart_type": "pie_chart",
            "column": column_name
        }


def generate_bar_chart(data: Dict[str, Any], column_name: str, title: str = None, horizontal: bool = True) -> Dict[str, Any]:
    """
    Generate professional bar chart for categorical data
    
    Args:
        data: Data dictionary with values
        column_name: Name of the column
        title: Optional custom title
        horizontal: Whether to create horizontal bars
        
    Returns:
        Chart generation results
    """
    try:
        # Prepare data
        values = data.get(column_name, [])
        value_counts = Counter(str(val) for val in values if val is not None and str(val).strip() != '')
        
        if not value_counts:
            raise ValueError("No valid data for bar chart")
        
        # Sort by count (descending)
        sorted_items = value_counts.most_common()
        labels = [item[0] for item in sorted_items]
        counts = [item[1] for item in sorted_items]
        
        # Create bar chart
        if horizontal:
            fig = go.Figure(data=[go.Bar(
                x=counts,
                y=labels,
                orientation='h',
                marker=dict(color=COLOR_PALETTES["professional"][0]),
                text=counts,
                textposition='outside'
            )])
            fig.update_layout(xaxis_title="Count", yaxis_title="Categories")
        else:
            fig = go.Figure(data=[go.Bar(
                x=labels,
                y=counts,
                marker=dict(color=COLOR_PALETTES["professional"][0]),
                text=counts,
                textposition='outside'
            )])
            fig.update_layout(xaxis_title="Categories", yaxis_title="Count")
        
        # Update layout
        chart_title = title or f"Distribution of {column_name}"
        fig.update_layout(
            title=dict(
                text=chart_title,
                font=dict(size=16, family="Arial"),
                x=0.5
            ),
            font=dict(family="Arial", size=12),
            width=800,
            height=600,
            margin=dict(t=80, b=40, l=40, r=40),
            showlegend=False
        )
        
        # Generate exports
        html_str = fig.to_html(include_plotlyjs='cdn')
        png_bytes = fig.to_image(format="png", width=800, height=600)
        
        result = {
            "success": True,
            "chart_type": "bar_chart",
            "orientation": "horizontal" if horizontal else "vertical",
            "column": column_name,
            "title": chart_title,
            "html": html_str,
            "png_base64": base64.b64encode(png_bytes).decode('utf-8'),
            "data_summary": {
                "categories": len(labels),
                "total_responses": sum(counts),
                "max_count": max(counts) if counts else 0,
                "top_category": labels[0] if labels else None
            },
            "generation_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"📊 Generated bar chart for {column_name}: {len(labels)} categories")
        return result
        
    except Exception as e:
        logger.error(f"❌ Bar chart generation failed for {column_name}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "chart_type": "bar_chart",
            "column": column_name
        }


def generate_histogram(data: Dict[str, Any], column_name: str, title: str = None, bins: int = 20) -> Dict[str, Any]:
    """
    Generate professional histogram for numerical data
    
    Args:
        data: Data dictionary with values
        column_name: Name of the column
        title: Optional custom title
        bins: Number of histogram bins
        
    Returns:
        Chart generation results
    """
    try:
        # Prepare data
        values = data.get(column_name, [])
        numeric_values = []
        
        for val in values:
            if val is not None:
                try:
                    numeric_values.append(float(val))
                except (ValueError, TypeError):
                    pass
        
        if not numeric_values:
            raise ValueError("No valid numeric data for histogram")
        
        # Create histogram
        fig = go.Figure(data=[go.Histogram(
            x=numeric_values,
            nbinsx=bins,
            marker=dict(
                color=COLOR_PALETTES["professional"][0],
                opacity=0.7,
                line=dict(color='white', width=1)
            ),
            name="Distribution"
        )])
        
        # Add statistical annotations
        mean_val = np.mean(numeric_values)
        std_val = np.std(numeric_values)
        
        fig.add_vline(
            x=mean_val,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_val:.2f}"
        )
        
        # Update layout
        chart_title = title or f"Distribution of {column_name}"
        fig.update_layout(
            title=dict(
                text=chart_title,
                font=dict(size=16, family="Arial"),
                x=0.5
            ),
            xaxis_title=column_name,
            yaxis_title="Frequency",
            font=dict(family="Arial", size=12),
            width=800,
            height=600,
            margin=dict(t=80, b=40, l=40, r=40),
            showlegend=False
        )
        
        # Generate exports
        html_str = fig.to_html(include_plotlyjs='cdn')
        png_bytes = fig.to_image(format="png", width=800, height=600)
        
        result = {
            "success": True,
            "chart_type": "histogram",
            "column": column_name,
            "title": chart_title,
            "html": html_str,
            "png_base64": base64.b64encode(png_bytes).decode('utf-8'),
            "data_summary": {
                "sample_size": len(numeric_values),
                "mean": float(mean_val),
                "std_dev": float(std_val),
                "min_value": float(min(numeric_values)),
                "max_value": float(max(numeric_values)),
                "bins_used": bins
            },
            "generation_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"📈 Generated histogram for {column_name}: {len(numeric_values)} values")
        return result
        
    except Exception as e:
        logger.error(f"❌ Histogram generation failed for {column_name}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "chart_type": "histogram",
            "column": column_name
        }


def generate_box_plot(data: Dict[str, Any], column_name: str, title: str = None) -> Dict[str, Any]:
    """
    Generate professional box plot for numerical data
    
    Args:
        data: Data dictionary with values
        column_name: Name of the column
        title: Optional custom title
        
    Returns:
        Chart generation results
    """
    try:
        # Prepare data
        values = data.get(column_name, [])
        numeric_values = []
        
        for val in values:
            if val is not None:
                try:
                    numeric_values.append(float(val))
                except (ValueError, TypeError):
                    pass
        
        if not numeric_values:
            raise ValueError("No valid numeric data for box plot")
        
        # Create box plot
        fig = go.Figure(data=[go.Box(
            y=numeric_values,
            name=column_name,
            marker=dict(color=COLOR_PALETTES["professional"][0]),
            boxpoints='outliers',
            line=dict(width=2)
        )])
        
        # Update layout
        chart_title = title or f"Box Plot of {column_name}"
        fig.update_layout(
            title=dict(
                text=chart_title,
                font=dict(size=16, family="Arial"),
                x=0.5
            ),
            yaxis_title=column_name,
            font=dict(family="Arial", size=12),
            width=800,
            height=600,
            margin=dict(t=80, b=40, l=40, r=40),
            showlegend=False
        )
        
        # Calculate statistics
        q1 = np.percentile(numeric_values, 25)
        median = np.percentile(numeric_values, 50)
        q3 = np.percentile(numeric_values, 75)
        iqr = q3 - q1
        
        # Generate exports
        html_str = fig.to_html(include_plotlyjs='cdn')
        png_bytes = fig.to_image(format="png", width=800, height=600)
        
        result = {
            "success": True,
            "chart_type": "box_plot",
            "column": column_name,
            "title": chart_title,
            "html": html_str,
            "png_base64": base64.b64encode(png_bytes).decode('utf-8'),
            "data_summary": {
                "sample_size": len(numeric_values),
                "quartiles": {
                    "q1": float(q1),
                    "median": float(median),
                    "q3": float(q3),
                    "iqr": float(iqr)
                },
                "outliers_detected": len([x for x in numeric_values if x < q1 - 1.5*iqr or x > q3 + 1.5*iqr])
            },
            "generation_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"📦 Generated box plot for {column_name}: {len(numeric_values)} values")
        return result
        
    except Exception as e:
        logger.error(f"❌ Box plot generation failed for {column_name}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "chart_type": "box_plot",
            "column": column_name
        }


def generate_word_cloud(data: Dict[str, Any], column_name: str, title: str = None) -> Dict[str, Any]:
    """
    Generate word cloud for textual data
    
    Args:
        data: Data dictionary with values
        column_name: Name of the column
        title: Optional custom title
        
    Returns:
        Chart generation results
    """
    if not WORDCLOUD_AVAILABLE:
        return {
            "success": False,
            "error": "WordCloud library not available",
            "chart_type": "word_cloud",
            "column": column_name
        }
    
    try:
        # Prepare data
        values = data.get(column_name, [])
        text_values = [str(val) for val in values if val is not None and str(val).strip() != '']
        
        if not text_values:
            raise ValueError("No valid text data for word cloud")
        
        # Combine all text
        combined_text = ' '.join(text_values)
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800,
            height=600,
            background_color='white',
            max_words=100,
            colormap='viridis',
            font_path=None,
            relative_scaling=0.5
        ).generate(combined_text)
        
        # Convert to image
        plt.figure(figsize=(10, 7.5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        chart_title = title or f"Word Cloud for {column_name}"
        plt.title(chart_title, fontsize=16, fontweight='bold', pad=20)
        
        # Save to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        png_data = img_buffer.getvalue()
        plt.close()
        
        result = {
            "success": True,
            "chart_type": "word_cloud",
            "column": column_name,
            "title": chart_title,
            "png_base64": base64.b64encode(png_data).decode('utf-8'),
            "data_summary": {
                "text_entries": len(text_values),
                "total_words": len(combined_text.split()),
                "unique_words": len(set(combined_text.lower().split()))
            },
            "generation_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"☁️ Generated word cloud for {column_name}: {len(text_values)} text entries")
        return result
        
    except Exception as e:
        logger.error(f"❌ Word cloud generation failed for {column_name}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "chart_type": "word_cloud",
            "column": column_name
        }


def generate_charts_for_dataset(dataset: Dict[str, List[Any]], classifications: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate appropriate charts for entire dataset based on classifications
    
    Args:
        dataset: Dictionary mapping column names to data lists
        classifications: Classification results from data-type-classifier-agent
        
    Returns:
        Complete chart generation results
    """
    results = {
        "generation_timestamp": datetime.now().isoformat(),
        "total_columns": len(dataset),
        "charts_generated": {},
        "generation_summary": {
            "successful": 0,
            "failed": 0,
            "chart_types": {}
        },
        "export_files": []
    }
    
    column_classifications = classifications.get("classifications", {})
    
    for column_name, column_data in dataset.items():
        if column_name not in column_classifications:
            logger.warning(f"⚠️ No classification found for column: {column_name}")
            continue
        
        classification = column_classifications[column_name]
        primary_type = classification.get("primary_type", "unknown")
        sub_type = classification.get("sub_type", "default")
        
        # Select appropriate chart generation function
        chart_result = None
        
        if primary_type == "categorical":
            if sub_type == "binary" or len(set(str(val) for val in column_data if val is not None)) <= 6:
                chart_result = generate_pie_chart(dataset, column_name)
            else:
                chart_result = generate_bar_chart(dataset, column_name, horizontal=True)
                
        elif primary_type == "numerical":
            if sub_type == "continuous":
                chart_result = generate_histogram(dataset, column_name)
            else:
                chart_result = generate_box_plot(dataset, column_name)
                
        elif primary_type == "textual":
            chart_result = generate_word_cloud(dataset, column_name)
            
        else:
            # Default to bar chart for unknown types
            chart_result = generate_bar_chart(dataset, column_name)
        
        # Store results
        if chart_result:
            results["charts_generated"][column_name] = chart_result
            
            if chart_result.get("success"):
                results["generation_summary"]["successful"] += 1
                chart_type = chart_result.get("chart_type", "unknown")
                results["generation_summary"]["chart_types"][chart_type] = \
                    results["generation_summary"]["chart_types"].get(chart_type, 0) + 1
            else:
                results["generation_summary"]["failed"] += 1
    
    logger.info(f"📊 Chart generation completed: {results['generation_summary']['successful']} successful, {results['generation_summary']['failed']} failed")
    return results


def get_visualization_generator_agent(
    version: Optional[int] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = False,
    db_url: Optional[str] = None
) -> Agent:
    """Visualization generator agent factory function"""
    
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Create agent with tools
    agent = Agent(
        name=config["agent"]["name"],
        agent_id=config["agent"]["agent_id"],
        instructions=config["instructions"],
        model=create_visualization_model(),
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
        generate_pie_chart,
        generate_bar_chart,
        generate_histogram,
        generate_box_plot,
        generate_word_cloud,
        generate_charts_for_dataset
    ])
    
    logger.info(f"📊 Visualization Generator Agent initialized - Version {config['agent']['version']}")
    return agent


# Export the factory function
__all__ = [
    "get_visualization_generator_agent",
    "generate_charts_for_dataset",
    "generate_pie_chart",
    "generate_bar_chart",
    "generate_histogram",
    "generate_box_plot",
    "generate_word_cloud"
]


if __name__ == "__main__":
    # Test the agent
    import asyncio
    
    async def test_visualization_generator():
        """Test visualization generator agent"""
        agent = get_visualization_generator_agent(debug_mode=True)
        
        test_message = """
        I need you to generate professional charts for this survey data:
        
        Column: satisfaction_rating
        Data: [5, 4, 5, 3, 4, 5, 2, 4, 5, 4]
        Type: categorical (rating scale)
        
        Column: age_group  
        Data: ["18-25", "26-35", "36-45", "18-25", "26-35", "46-55", "18-25"]
        Type: categorical (nominal)
        
        Please generate appropriate charts with professional styling.
        """
        
        logger.info("Testing visualization generator agent...")
        response = await agent.arun(test_message)
        logger.info(f"🤖 Response: {response.content}")
    
    # Run test
    asyncio.run(test_visualization_generator())