# Stock Validation Management Command

## Overview

The `validate_stock` management command validates product stock levels by comparing calculated stock (based on movement history) against stored stock values in the `produtos.estoque_atual` field.

## Usage

```bash
python manage.py validate_stock [options]
```

## Options

- `--product-ids`: Comma-separated list of specific product IDs to validate
- `--output-format`: Output format (`console`, `csv`, `json`)
- `--output-file`: Output file path (required for csv/json formats)
- `--threshold`: Minimum difference threshold to report as discrepancy (default: 0.01)
- `--show-correct`: Include products with correct stock in detailed output
- `--limit`: Maximum number of products to validate
- `--detailed-report`: Generate detailed validation report with analysis and recommendations

## Examples

### Basic validation (console output)
```bash
python manage.py validate_stock --limit 10
```

### Validate specific products
```bash
python manage.py validate_stock --product-ids 1,2,3,4,5
```

### Generate detailed report
```bash
python manage.py validate_stock --detailed-report --limit 100
```

### Export to CSV
```bash
python manage.py validate_stock --output-format csv --output-file stock_validation.csv --show-correct --limit 50
```

### Export to JSON
```bash
python manage.py validate_stock --output-format json --output-file stock_validation.json --detailed-report
```

## Output Formats

### Console Output
- Summary of validation results
- List of products with discrepancies
- Detailed analysis (if --detailed-report is used)
- Recommendations for data quality issues

### CSV Output
- One row per product
- Columns: produto_id, produto_codigo, produto_nome, calculated_stock, stored_stock, difference, abs_difference, percentage_diff, status
- Status values: CORRECT, DISCREPANCY, ERROR

### JSON Output
- Structured data with metadata
- Complete validation results
- Analysis and recommendations (if --detailed-report is used)

## Features

1. **Stock Calculation**: Uses the StockCalculationService to calculate current stock based on movement history
2. **Discrepancy Detection**: Identifies products where calculated stock differs from stored stock
3. **Error Handling**: Gracefully handles products with calculation errors
4. **Progress Reporting**: Shows progress for large datasets
5. **Flexible Output**: Multiple output formats for different use cases
6. **Detailed Analysis**: Optional detailed analysis with recommendations

## Integration

The command integrates with:
- `StockValidationService`: Core validation logic
- `StockCalculationService`: Historical stock calculation
- Django management command framework
- Existing product and movement models

## Performance

- Processes products in batches
- Includes progress reporting for large datasets
- Optimized database queries through the service layer
- Memory-efficient processing

## Error Handling

- Gracefully handles missing products
- Reports calculation errors without stopping validation
- Provides detailed error messages in output
- Continues processing even if individual products fail

This command is essential for maintaining data quality and identifying discrepancies in stock calculations after migration or data updates.