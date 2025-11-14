# Reporting Module

## Overview

The reporting module provides comprehensive report generation, export, and visualization capabilities for trade risk analysis. It supports multiple report types, export formats, and visualization options.

## Components

### 1. ReportGenerator

Main class for generating various types of reports.

**Report Types:**
- **Daily Summary Report**: Overview of all alerts and trading activity for a specific day
- **User Risk Profile**: Detailed risk assessment for individual users
- **Pattern Analysis Report**: Analysis of specific pattern types across users and time

**Usage:**
```python
from trade_risk_analyzer.reporting.generator import ReportGenerator
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage

# Initialize with database storage
storage = DatabaseStorage(database_url="postgresql://...")
generator = ReportGenerator(storage=storage)

# Generate daily summary
report = generator.generate_daily_summary(date=datetime(2025, 11, 12))

# Generate user risk profile
profile = generator.generate_user_risk_profile(user_id="user_123", days=30)

# Generate pattern analysis
analysis = generator.generate_pattern_analysis(
    pattern_type=PatternType.WASH_TRADING,
    days=30
)
```

### 2. ReportExporter

Exports reports in multiple formats: JSON, CSV, and PDF.

**Supported Formats:**
- **JSON**: Structured data for API consumption
- **CSV**: Tabular data for spreadsheet analysis
- **PDF**: Professional formatted reports (requires reportlab)

**Usage:**
```python
from trade_risk_analyzer.reporting.exporters import ReportExporter

exporter = ReportExporter()

# Export to JSON
exporter.export(report, "daily_summary.json", format='json')

# Export to CSV
exporter.export(report, "daily_summary.csv", format='csv')

# Export to PDF (requires reportlab)
exporter.export(report, "daily_summary.pdf", format='pdf')
```

### 3. Visualizer

Creates charts and visualizations for reports.

**Visualization Types:**
- Anomaly score distribution (histogram)
- Risk level distribution (pie chart)
- Time series plots (alerts over time)
- Temporal heatmaps (hour/day patterns)
- Pattern distribution (bar chart)
- User risk comparison (horizontal bar chart)
- Comprehensive dashboard (multi-panel)

**Usage:**
```python
from trade_risk_analyzer.reporting.visualizations import Visualizer

visualizer = Visualizer()

# Create anomaly score distribution
visualizer.create_anomaly_score_distribution(
    alerts,
    output_path="anomaly_dist.png"
)

# Create risk level pie chart
visualizer.create_risk_level_distribution(
    alerts,
    output_path="risk_levels.png"
)

# Create time series plot
visualizer.create_time_series_plot(
    alerts,
    output_path="time_series.png",
    resample_freq='D'  # Daily aggregation
)

# Create temporal heatmap
visualizer.create_temporal_heatmap(
    alerts,
    output_path="heatmap.png"
)

# Create comprehensive dashboard
visualizer.create_dashboard(
    alerts,
    output_path="dashboard.png"
)
```

## Report Types

### Daily Summary Report

Contains:
- Total trades and alerts
- Risk level breakdown (HIGH/MEDIUM/LOW)
- Alerts by pattern type
- Top risk users
- Average anomaly score
- Full alert details

**Example:**
```python
report = generator.generate_daily_summary(
    date=datetime(2025, 11, 12),
    include_alerts=True
)

print(f"Total Alerts: {report.total_alerts}")
print(f"High Risk: {report.high_risk_alerts}")
print(f"Average Score: {report.average_anomaly_score:.2f}")
```

### User Risk Profile

Contains:
- User identification
- Overall risk score and level
- Total trades and alerts
- Alerts by pattern type
- Trading statistics
- Risk trend over time
- Recent alerts

**Example:**
```python
profile = generator.generate_user_risk_profile(
    user_id="user_123",
    days=30,
    include_recent_alerts=10
)

print(f"Risk Score: {profile.risk_score:.2f}")
print(f"Risk Level: {profile.risk_level.value}")
print(f"Total Alerts: {profile.total_alerts}")
```

### Pattern Analysis Report

Contains:
- Pattern type
- Total occurrences
- Affected users count
- Average severity
- Temporal distribution
- User distribution
- Example alerts

**Example:**
```python
analysis = generator.generate_pattern_analysis(
    pattern_type=PatternType.WASH_TRADING,
    days=30,
    include_examples=5
)

print(f"Occurrences: {analysis.total_occurrences}")
print(f"Affected Users: {analysis.affected_users}")
print(f"Avg Severity: {analysis.average_severity:.2f}")
```

## Export Formats

### JSON Export

Structured data suitable for:
- API responses
- Data interchange
- Programmatic processing

**Features:**
- Complete data preservation
- Nested structure support
- ISO 8601 timestamps
- Easy parsing

### CSV Export

Tabular data suitable for:
- Spreadsheet analysis (Excel, Google Sheets)
- Data import/export
- Simple reporting

**Features:**
- Header rows with metadata
- Flat structure for alerts
- Compatible with all spreadsheet tools

### PDF Export

Professional formatted reports suitable for:
- Executive summaries
- Compliance documentation
- Printed reports
- Email distribution

**Features:**
- Professional formatting
- Tables and charts
- Consistent styling
- Print-ready output

**Requirements:**
```bash
pip install reportlab
```

## Visualizations

### Anomaly Score Distribution

Histogram showing the distribution of anomaly scores across all alerts.

**Features:**
- 20 bins for score ranges
- Risk threshold lines (50, 80)
- Frequency counts

### Risk Level Distribution

Pie chart showing the proportion of alerts by risk level.

**Features:**
- Color-coded by risk (red=HIGH, orange=MEDIUM, green=LOW)
- Percentage labels
- Clear legend

### Time Series Plot

Line plots showing alerts and scores over time.

**Features:**
- Alert count over time
- Average anomaly score over time
- Risk threshold lines
- Configurable time aggregation (hourly, daily, weekly)

### Temporal Heatmap

Heatmap showing alert patterns by hour of day and day of week.

**Features:**
- Hour (0-23) on x-axis
- Day of week on y-axis
- Color intensity shows alert count
- Identifies peak activity times

### Pattern Distribution

Bar chart showing alert counts by pattern type.

**Features:**
- Sorted by frequency
- Color-coded bars
- Value labels on bars

### User Risk Comparison

Horizontal bar chart comparing risk scores across users.

**Features:**
- Top N users by risk score
- Color-coded by risk level
- Risk threshold lines
- Sorted by score

### Comprehensive Dashboard

Multi-panel dashboard with all key visualizations.

**Features:**
- 6 panels in one figure
- Anomaly distribution
- Risk level pie chart
- Pattern distribution
- Time series
- Optimized layout

**Requirements:**
```bash
pip install matplotlib seaborn
```

## Configuration

No specific configuration required. The module uses the database storage configuration from the main application.

## Examples

See `example_reporting.py` for comprehensive examples of:
1. Daily summary report generation and export
2. User risk profile generation and export
3. Pattern analysis generation and export
4. Visualization creation

Run examples:
```bash
python example_reporting.py
```

## Testing

Run tests:
```bash
python test_reporting.py
```

Tests cover:
- Report generation
- JSON/CSV/PDF export
- All visualization types

## Dependencies

**Required:**
- pandas
- numpy

**Optional:**
- reportlab (for PDF export)
- matplotlib (for visualizations)
- seaborn (for enhanced visualizations)

Install all dependencies:
```bash
pip install pandas numpy reportlab matplotlib seaborn
```

## Output Examples

Generated reports are saved to the specified output directory:

```
reports/
├── daily_summary_20251112.json
├── daily_summary_20251112.csv
├── daily_summary_20251112.pdf
├── user_profile_user123.json
├── user_profile_user123.csv
├── pattern_wash_trading.json
├── anomaly_distribution.png
├── risk_levels.png
├── time_series.png
├── heatmap.png
└── dashboard.png
```

## Best Practices

1. **Use Database Storage**: Connect ReportGenerator to DatabaseStorage for real data
2. **Schedule Reports**: Generate daily summaries automatically
3. **Export Multiple Formats**: Provide JSON for APIs, CSV for analysis, PDF for distribution
4. **Create Visualizations**: Include charts in reports for better insights
5. **Archive Reports**: Keep historical reports for trend analysis
6. **Customize Exports**: Adjust parameters based on audience needs

## API Integration

Reports can be easily integrated into REST APIs:

```python
from fastapi import FastAPI
from trade_risk_analyzer.reporting import ReportGenerator, ReportExporter

app = FastAPI()

@app.get("/reports/daily/{date}")
async def get_daily_report(date: str, format: str = "json"):
    generator = ReportGenerator(storage=storage)
    report = generator.generate_daily_summary(
        date=datetime.fromisoformat(date)
    )
    
    if format == "json":
        return report.to_dict()
    else:
        exporter = ReportExporter()
        path = f"reports/daily_{date}.{format}"
        exporter.export(report, path, format=format)
        return {"file": path}
```

## Future Enhancements

- Email report distribution
- Scheduled report generation
- Custom report templates
- Interactive dashboards
- Real-time report updates
- Report comparison tools
- Trend analysis reports
