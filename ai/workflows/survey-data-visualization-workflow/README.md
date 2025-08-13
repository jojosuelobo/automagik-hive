# Survey Data Visualization Workflow

## Overview

A comprehensive automated survey data analysis and visualization pipeline built with **Agno Workflows 2.0**. This workflow processes XLSX survey files, automatically classifies data types, generates professional visualizations, and creates stakeholder-ready dashboards with AI-powered insights.

## Features

### 🔄 **Automated Processing Pipeline**
- XLSX file parsing and column extraction
- Automatic filtering of survey columns (pesquisa* pattern)
- Data quality validation and assessment
- Professional error handling and logging

### 🤖 **AI-Powered Classification**
- Intelligent data type detection (categorical, numerical, temporal, textual)
- Sub-type classification (ordinal, binary, continuous, etc.)
- Confidence scoring for all classifications
- Statistical analysis and pattern recognition

### 📊 **Professional Visualizations**
- Automatic chart type selection based on data characteristics
- Professional styling with consistent color palettes
- Interactive features with hover tooltips and zoom
- Multiple export formats (PNG, HTML, SVG, PDF)

### 📈 **Executive Dashboard**
- Interactive HTML dashboard compilation
- AI-generated executive summary and insights
- Actionable business recommendations with priorities
- Data quality reports and methodology documentation

## Workflow Architecture

### Step-Based Processing (Agno Workflows 2.0)

```mermaid
graph TD
    A[Excel Processing] --> B[Data Classification]
    B --> C[Visualization Generation]
    C --> D[Dashboard Assembly]
    
    A1[Column Extraction] --> A2[Data Validation] --> A3[Quality Assessment]
    B1[Type Detection] --> B2[Statistical Analysis] --> B3[Confidence Scoring]
    C1[Chart Selection] --> C2[Professional Styling] --> C3[Export Generation]
    D1[Insight Generation] --> D2[Dashboard Compilation] --> D3[Report Creation]
```

### Specialized Agents

1. **excel-data-processor-agent** - XLSX parsing and survey column extraction
2. **data-type-classifier-agent** - AI-powered data type classification  
3. **visualization-generator-agent** - Professional chart generation
4. **dashboard-builder-agent** - Dashboard assembly and insight generation

## Usage

### Basic Usage

```python
from ai.workflows.survey_data_visualization_workflow.workflow import get_survey_data_visualization_workflow

# Create workflow instance
workflow = get_survey_data_visualization_workflow()

# Process survey data
result = await workflow.arun(
    message="Please analyze survey file: /path/to/survey_data.xlsx"
)
```

### Advanced Configuration

```python
from agno.storage.postgres import PostgresStorage

# Custom storage configuration
workflow = get_survey_data_visualization_workflow(
    storage=PostgresStorage(
        table_name="custom_survey_workflows",
        db_url="postgresql://user:pass@host:port/db"
    ),
    session_id="survey-analysis-2024"
)

# Stream processing with intermediate steps
async for response in workflow.run(
    message="Analyze survey data with columns: pesquisa300625_screen0-9",
    stream=True,
    stream_intermediate_steps=True
):
    print(f"Step: {response.step_name}")
    print(f"Status: {response.content}")
```

## Input Requirements

### XLSX File Structure

The workflow expects XLSX files with columns containing "pesquisa" in their names:

```
Required Columns:
- pesquisa300625_screen0 (any data type)
- pesquisa300625_screen1 (any data type)
- pesquisa300625_screen2 (any data type)
- ... (up to pesquisa300625_screen9)

Optional Columns:
- First name
- Email 1, Email 2
- Number 1, Number 2
- Any other metadata columns
```

### Supported Data Types

- **Categorical**: Multiple choice, Yes/No, rating scales, ordinal data
- **Numerical**: Continuous values, discrete counts, percentages, scores
- **Temporal**: Dates, timestamps, time periods, sequences
- **Textual**: Open-ended responses, comments, descriptions, feedback

## Output Deliverables

### 1. Interactive Dashboard (`interactive_dashboard.html`)
- Responsive web dashboard with all visualizations
- Executive summary and key insights
- Filter controls and interactive features
- Professional styling for stakeholder presentation

### 2. Executive Report (`executive_report.pdf`)
- Professional PDF with executive summary
- Key findings and statistical analysis
- Actionable recommendations with priorities
- Data quality assessment and methodology

### 3. Analysis Data (`analysis_results.json`)
- Complete analysis results in structured format
- Classification results with confidence scores
- Chart specifications and metadata
- Processing logs and quality metrics

### 4. Chart Collection
- Individual PNG charts for presentations
- HTML files for web embedding
- SVG files for scalability
- Professional styling and annotations

## Technical Specifications

### Dependencies

```toml
# Core framework
agno = "1.7.5"

# Data processing
pandas = ">=2.0.0"
openpyxl = ">=3.1.0"

# Visualization
plotly = ">=6.2.0"
matplotlib = ">=3.10.3"
seaborn = ">=0.13.2"

# Text analysis (optional)
wordcloud = ">=1.9.0"

# Templates and reports
jinja2 = ">=3.1.6"
```

### Performance Characteristics

- **Processing Speed**: ~30-60 seconds for 10 survey columns
- **Memory Usage**: ~200-500MB for typical survey datasets
- **Concurrent Processing**: Supports parallel chart generation
- **Scalability**: Handles up to 10,000 survey responses efficiently

### Database Storage

Uses PostgreSQL for workflow state management:

```sql
-- Workflow execution tracking
CREATE TABLE survey_visualization_workflows (
    id UUID PRIMARY KEY,
    session_id VARCHAR(255),
    workflow_state JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Agent-specific storage tables
CREATE TABLE agents_excel_data_processor (...);
CREATE TABLE agents_data_type_classifier (...);
CREATE TABLE agents_visualization_generator (...);
CREATE TABLE agents_dashboard_builder (...);
```

## Configuration

### Workflow Configuration (`config.yaml`)

```yaml
workflow:
  name: Survey Data Visualization Workflow
  version: 1.0.0
  description: Automated survey analysis and visualization

model:
  provider: anthropic
  id: claude-sonnet-4-20250514
  temperature: 0.1

storage:
  type: postgres
  auto_upgrade_schema: true

quality_controls:
  minimum_sample_size: 10
  confidence_threshold: 0.7
  supported_formats: [xlsx, csv]
```

### Agent Versioning

All agents follow semantic versioning:

```yaml
agent:
  version: 1.0.0  # Bump when changes made
```

**Critical**: Version must be bumped whenever agent code, config, or tools are modified.

## Quality Assurance

### Data Quality Checks
- Column presence validation
- Missing value analysis (threshold: <50% missing)
- Data type consistency verification
- Outlier detection and flagging

### Visualization Standards
- Consistent color schemes (colorblind-friendly)
- Professional fonts and sizing
- Accessibility compliance (WCAG 2.1)
- Cross-browser compatibility

### Output Validation
- Chart integrity verification
- Export format validation
- Statistical accuracy checks
- Stakeholder readiness review

## Error Handling

### Graceful Degradation
- Continues processing if individual columns fail
- Provides partial results with clear error messages
- Suggests remediation steps for common issues
- Logs all errors for debugging

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| No 'pesquisa' columns found | Incorrect column naming | Check column names match pattern |
| Classification uncertainty | Ambiguous data types | Manual review flagged columns |
| Visualization failures | Incompatible data format | Check data type classification |
| Export errors | File permissions | Verify output directory access |

## Integration Examples

### REST API Integration

```python
from fastapi import FastAPI, UploadFile
from ai.workflows.survey_data_visualization_workflow.workflow import get_survey_data_visualization_workflow

app = FastAPI()

@app.post("/analyze-survey")
async def analyze_survey(file: UploadFile):
    workflow = get_survey_data_visualization_workflow()
    
    result = await workflow.arun(
        message=f"Please analyze uploaded survey file: {file.filename}"
    )
    
    return {"status": "completed", "results": result.content}
```

### Batch Processing

```python
import asyncio
from pathlib import Path

async def process_survey_batch(file_paths: List[str]):
    workflow = get_survey_data_visualization_workflow()
    
    tasks = []
    for file_path in file_paths:
        task = workflow.arun(
            message=f"Analyze survey file: {file_path}",
            session_id=f"batch-{Path(file_path).stem}"
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

## Roadmap

### Planned Enhancements
- [ ] Real-time survey processing via streaming APIs
- [ ] Advanced statistical testing (ANOVA, regression analysis)
- [ ] Multi-language support for survey content
- [ ] Custom branding and styling options
- [ ] Machine learning-based insight generation
- [ ] Integration with popular survey platforms (SurveyMonkey, Typeform)

### Version History
- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - Planned: Advanced statistical analysis
- **v1.2.0** - Planned: Real-time processing capabilities

## Support

### Troubleshooting
1. Check agent versions are properly bumped after changes
2. Verify all analytics dependencies are installed: `uv pip install -e .[analytics]`
3. Ensure PostgreSQL is running and accessible
4. Check file permissions for input XLSX files
5. Review logs in `logs/` directory for detailed error information

### Contributing
1. Follow the established agent factory pattern
2. Bump version numbers in config.yaml when making changes
3. Add comprehensive tests for new functionality
4. Update documentation for any new features
5. Follow CLAUDE.md coding standards

---

**Generated by Survey Data Visualization Workflow v1.0.0**  
*Automagik Hive - Enterprise Multi-Agent System*