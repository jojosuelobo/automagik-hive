"""
Visualization Generator Tools - Professional Chart Creation Utilities
=====================================================================

Advanced chart generation utilities with professional styling, interactive features,
and multiple export formats for survey data visualization workflows.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
import base64
import io
from datetime import datetime
import json
from collections import Counter
import colorsys

from lib.logging import logger

# Professional styling constants
CHART_FONTS = {
    "title": dict(family="Arial", size=16, color="#2D3436"),
    "labels": dict(family="Arial", size=12, color="#636E72"),
    "annotations": dict(family="Arial", size=10, color="#636E72")
}

CHART_MARGINS = dict(t=80, b=60, l=60, r=60)
STANDARD_DIMENSIONS = (800, 600)


def create_color_palette(n_colors: int, palette_name: str = "professional") -> List[str]:
    """
    Create a color palette with specified number of colors
    
    Args:
        n_colors: Number of colors needed
        palette_name: Name of the base palette
        
    Returns:
        List of hex color codes
    """
    base_palettes = {
        "professional": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"],
        "corporate": ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#5EAFC5", "#B85A7A"],
        "accessible": ["#1B9E77", "#D95F02", "#7570B3", "#E7298A", "#66A61E", "#E6AB02"],
        "grayscale": ["#2D3436", "#636E72", "#B2BEC3", "#74B9FF", "#0984E3", "#6C5CE7"]
    }
    
    base_colors = base_palettes.get(palette_name, base_palettes["professional"])
    
    if n_colors <= len(base_colors):
        return base_colors[:n_colors]
    
    # Generate additional colors by interpolating
    extended_colors = base_colors.copy()
    
    while len(extended_colors) < n_colors:
        for i in range(len(base_colors) - 1):
            if len(extended_colors) >= n_colors:
                break
            
            # Interpolate between adjacent colors
            color1 = base_colors[i].lstrip('#')
            color2 = base_colors[i + 1].lstrip('#')
            
            r1, g1, b1 = tuple(int(color1[j:j+2], 16) for j in (0, 2, 4))
            r2, g2, b2 = tuple(int(color2[j:j+2], 16) for j in (0, 2, 4))
            
            # Midpoint color
            r_mid = int((r1 + r2) / 2)
            g_mid = int((g1 + g2) / 2)
            b_mid = int((b1 + b2) / 2)
            
            mid_color = f"#{r_mid:02x}{g_mid:02x}{b_mid:02x}"
            extended_colors.append(mid_color)
    
    return extended_colors[:n_colors]


def apply_professional_styling(fig: go.Figure, title: str, chart_type: str = "standard") -> go.Figure:
    """
    Apply professional styling to plotly figure
    
    Args:
        fig: Plotly figure object
        title: Chart title
        chart_type: Type of chart for specific styling
        
    Returns:
        Styled figure
    """
    # Base layout updates
    layout_updates = dict(
        title=dict(
            text=title,
            font=CHART_FONTS["title"],
            x=0.5,
            xanchor='center'
        ),
        font=CHART_FONTS["labels"],
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=CHART_MARGINS,
        width=STANDARD_DIMENSIONS[0],
        height=STANDARD_DIMENSIONS[1]
    )
    
    # Chart-specific styling
    if chart_type in ["bar", "histogram"]:
        layout_updates.update({
            "xaxis": dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#E8E8E8',
                showline=True,
                linewidth=1,
                linecolor='#BFBFBF'
            ),
            "yaxis": dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#E8E8E8',
                showline=True,
                linewidth=1,
                linecolor='#BFBFBF'
            )
        })
    
    elif chart_type == "pie":
        layout_updates.update({
            "showlegend": True,
            "legend": dict(
                orientation="v",
                x=1.02,
                y=0.5,
                font=CHART_FONTS["labels"]
            )
        })
    
    elif chart_type == "box":
        layout_updates.update({
            "yaxis": dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#E8E8E8',
                zeroline=False
            )
        })
    
    fig.update_layout(**layout_updates)
    return fig


def create_donut_chart(data_counts: Dict[str, int], title: str, colors: List[str] = None) -> go.Figure:
    """
    Create a professional donut chart
    
    Args:
        data_counts: Dictionary mapping labels to counts
        title: Chart title
        colors: Optional color list
        
    Returns:
        Plotly figure object
    """
    labels = list(data_counts.keys())
    values = list(data_counts.values())
    
    if colors is None:
        colors = create_color_palette(len(labels), "professional")
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        textinfo='label+percent',
        textposition='auto',
        marker=dict(
            colors=colors,
            line=dict(color='white', width=2)
        ),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    # Add center text
    total_count = sum(values)
    fig.add_annotation(
        text=f"Total<br>{total_count}",
        x=0.5, y=0.5,
        font_size=14,
        showarrow=False
    )
    
    fig = apply_professional_styling(fig, title, "pie")
    return fig


def create_grouped_bar_chart(data: Dict[str, Dict[str, int]], title: str, 
                            horizontal: bool = False) -> go.Figure:
    """
    Create a grouped bar chart for multiple series
    
    Args:
        data: Nested dictionary with categories and series
        title: Chart title
        horizontal: Whether to orient bars horizontally
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    categories = list(data.keys())
    series_names = set()
    for cat_data in data.values():
        series_names.update(cat_data.keys())
    series_names = list(series_names)
    
    colors = create_color_palette(len(series_names), "professional")
    
    for i, series in enumerate(series_names):
        values = [data[cat].get(series, 0) for cat in categories]
        
        if horizontal:
            fig.add_trace(go.Bar(
                x=values,
                y=categories,
                name=series,
                orientation='h',
                marker_color=colors[i],
                text=values,
                textposition='outside'
            ))
        else:
            fig.add_trace(go.Bar(
                x=categories,
                y=values,
                name=series,
                marker_color=colors[i],
                text=values,
                textposition='outside'
            ))
    
    fig = apply_professional_styling(fig, title, "bar")
    
    if horizontal:
        fig.update_layout(xaxis_title="Count", yaxis_title="Categories")
    else:
        fig.update_layout(xaxis_title="Categories", yaxis_title="Count")
    
    return fig


def create_distribution_plot(values: List[float], title: str, 
                           show_stats: bool = True) -> go.Figure:
    """
    Create an enhanced distribution plot with statistics
    
    Args:
        values: List of numeric values
        title: Chart title
        show_stats: Whether to show statistical annotations
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Histogram
    fig.add_trace(go.Histogram(
        x=values,
        nbinsx=20,
        name="Distribution",
        marker=dict(
            color=create_color_palette(1, "professional")[0],
            opacity=0.7,
            line=dict(color='white', width=1)
        ),
        hovertemplate='Range: %{x}<br>Count: %{y}<extra></extra>'
    ))
    
    if show_stats and len(values) > 1:
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        # Add mean line
        fig.add_vline(
            x=mean_val,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text=f"Mean: {mean_val:.2f}",
            annotation_position="top"
        )
        
        # Add standard deviation bands
        fig.add_vrect(
            x0=mean_val - std_val,
            x1=mean_val + std_val,
            fillcolor="rgba(255, 0, 0, 0.1)",
            layer="below",
            annotation_text="±1 SD",
            annotation_position="top left"
        )
    
    fig = apply_professional_styling(fig, title, "histogram")
    fig.update_layout(
        xaxis_title="Value",
        yaxis_title="Frequency"
    )
    
    return fig


def create_correlation_heatmap(data: pd.DataFrame, title: str) -> go.Figure:
    """
    Create a correlation heatmap for numerical columns
    
    Args:
        data: DataFrame with numerical columns
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    # Select only numerical columns
    numeric_data = data.select_dtypes(include=[np.number])
    
    if numeric_data.empty:
        raise ValueError("No numerical columns found for correlation analysis")
    
    # Calculate correlation matrix
    corr_matrix = numeric_data.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.round(2).values,
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate='%{x} vs %{y}<br>Correlation: %{z:.3f}<extra></extra>'
    ))
    
    fig = apply_professional_styling(fig, title, "heatmap")
    fig.update_layout(
        xaxis_title="Variables",
        yaxis_title="Variables"
    )
    
    return fig


def create_summary_statistics_table(data: Dict[str, List[Any]]) -> Dict[str, Any]:
    """
    Create a summary statistics table for the dataset
    
    Args:
        data: Dictionary mapping column names to data lists
        
    Returns:
        Dictionary containing summary statistics
    """
    summary = {
        "generation_timestamp": datetime.now().isoformat(),
        "total_columns": len(data),
        "column_summaries": {}
    }
    
    for column_name, values in data.items():
        # Clean values
        clean_values = [val for val in values if val is not None and str(val).strip() != '']
        
        column_summary = {
            "total_count": len(values),
            "valid_count": len(clean_values),
            "null_count": len(values) - len(clean_values),
            "null_percentage": ((len(values) - len(clean_values)) / len(values) * 100) if values else 0,
            "unique_count": len(set(str(val) for val in clean_values))
        }
        
        # Try to calculate numeric statistics
        try:
            numeric_values = [float(val) for val in clean_values if str(val).replace('.', '').replace('-', '').isdigit()]
            
            if numeric_values:
                column_summary.update({
                    "numeric_count": len(numeric_values),
                    "mean": float(np.mean(numeric_values)),
                    "median": float(np.median(numeric_values)),
                    "std_dev": float(np.std(numeric_values)),
                    "min_value": float(min(numeric_values)),
                    "max_value": float(max(numeric_values)),
                    "quartiles": {
                        "q1": float(np.percentile(numeric_values, 25)),
                        "q3": float(np.percentile(numeric_values, 75))
                    }
                })
        except Exception:
            # Not numeric data
            value_counts = Counter(str(val) for val in clean_values)
            column_summary.update({
                "most_common": value_counts.most_common(3),
                "unique_ratio": len(set(str(val) for val in clean_values)) / len(clean_values) if clean_values else 0
            })
        
        summary["column_summaries"][column_name] = column_summary
    
    return summary


def export_chart_collection(charts: Dict[str, Any], output_dir: str = "charts") -> Dict[str, Any]:
    """
    Export collection of charts to files
    
    Args:
        charts: Dictionary of chart results
        output_dir: Directory to save charts
        
    Returns:
        Export results summary
    """
    import os
    from pathlib import Path
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    export_summary = {
        "export_timestamp": datetime.now().isoformat(),
        "output_directory": str(output_path.absolute()),
        "files_created": [],
        "export_stats": {
            "successful": 0,
            "failed": 0,
            "total_size_mb": 0
        }
    }
    
    for column_name, chart_data in charts.items():
        if not chart_data.get("success"):
            continue
        
        try:
            # Export PNG
            if "png_base64" in chart_data:
                png_data = base64.b64decode(chart_data["png_base64"])
                png_filename = f"{column_name}_{chart_data['chart_type']}.png"
                png_path = output_path / png_filename
                
                with open(png_path, 'wb') as f:
                    f.write(png_data)
                
                export_summary["files_created"].append({
                    "filename": png_filename,
                    "format": "png",
                    "size_kb": len(png_data) / 1024,
                    "column": column_name
                })
                
                export_summary["export_stats"]["total_size_mb"] += len(png_data) / (1024 * 1024)
            
            # Export HTML
            if "html" in chart_data:
                html_filename = f"{column_name}_{chart_data['chart_type']}.html"
                html_path = output_path / html_filename
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(chart_data["html"])
                
                export_summary["files_created"].append({
                    "filename": html_filename,
                    "format": "html",
                    "size_kb": len(chart_data["html"]) / 1024,
                    "column": column_name
                })
            
            export_summary["export_stats"]["successful"] += 1
            
        except Exception as e:
            logger.error(f"❌ Export failed for {column_name}: {str(e)}")
            export_summary["export_stats"]["failed"] += 1
    
    logger.info(f"📁 Chart export completed: {export_summary['export_stats']['successful']} files created")
    return export_summary


def create_chart_grid(charts: List[go.Figure], titles: List[str], 
                     rows: int = 2, cols: int = 2) -> go.Figure:
    """
    Create a grid layout of multiple charts
    
    Args:
        charts: List of plotly figures
        titles: List of chart titles
        rows: Number of rows in grid
        cols: Number of columns in grid
        
    Returns:
        Combined figure with subplots
    """
    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=titles[:rows*cols],
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )
    
    for i, chart in enumerate(charts[:rows*cols]):
        row = (i // cols) + 1
        col = (i % cols) + 1
        
        # Add traces from the individual chart
        for trace in chart.data:
            fig.add_trace(trace, row=row, col=col)
    
    fig.update_layout(
        height=300 * rows,
        width=400 * cols,
        showlegend=False,
        title_text="Survey Data Analysis Dashboard",
        title_x=0.5,
        font=CHART_FONTS["labels"]
    )
    
    return fig


# Export all utility functions
__all__ = [
    "create_color_palette",
    "apply_professional_styling",
    "create_donut_chart",
    "create_grouped_bar_chart",
    "create_distribution_plot",
    "create_correlation_heatmap",
    "create_summary_statistics_table",
    "export_chart_collection",
    "create_chart_grid"
]