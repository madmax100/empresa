# Stock Calculation API Documentation

## Overview

The Stock Calculation API provides endpoints for calculating accurate stock levels based on movement history, validating current stock data, and identifying discrepancies between calculated and stored stock values.

## Base URL

All endpoints are available under the base URL:
```
/api/estoque-controle/
```

## Authentication

These endpoints use the same authentication as the existing Django REST Framework setup.

## Endpoints

### 1. Calculate Historical Stock

**Endpoint:** `GET /api/estoque-controle/calculate_historical_stock/`

Calculate stock for a specific product at a specific date using movement history and stock resets.

**Parameters:**
- `produto_id` (required): Integer - ID of the product
- `data` (required): String - Date in YYYY-MM-DD format

**Example Request:**
```bash
curl "http://localhost:8000/api/estoque-controle/calculate_historical_stock/?produto_id=1&data=2025-09-14"
```

**Example Response:**
```json
{
  "produto": {
    "id": 1,
    "codigo": "1",
    "nome": "UNIDADE IMP TIPO 4545A-DX4545/DX3343",
    "ativo": true
  },
  "calculation": {
    "target_date": "2025-09-14",
    "calculated_stock": 0.0,
    "stored_stock": 0.0,
    "difference": 0.0,
    "is_accurate": true
  },
  "stock_reset_info": {
    "has_reset": false,
    "reset_date": null,
    "reset_quantity": null
  },
  "movement_summary": {
    "period": {
      "start_date": "2025-08-15",
      "end_date": "2025-09-14"
    },
    "total_movements": 0,
    "regular_movements": 0,
    "stock_resets": 0,
    "totals": {
      "entrada": 0.0,
      "saida": 0.0,
      "net_movement": 0.0
    }
  }
}
```

### 2. Validate Current Stock

**Endpoint:** `GET /api/estoque-controle/validate_current_stock/`

Compare calculated current stock vs stored stock values for products.

**Parameters:**
- `produto_ids` (optional): String - Comma-separated list of product IDs
- `limit` (optional): Integer - Maximum number of products to validate (default: 100, max: 1000)

**Example Request:**
```bash
# Validate specific products
curl "http://localhost:8000/api/estoque-controle/validate_current_stock/?produto_ids=1,2,3&limit=5"

# Validate sample of products
curl "http://localhost:8000/api/estoque-controle/validate_current_stock/?limit=10"
```

**Example Response:**
```json
{
  "validation_results": {
    "total_products": 5,
    "correct_stock": 5,
    "incorrect_stock": 0,
    "discrepancies": [],
    "validation_date": "2025-09-14T10:30:00.000Z",
    "summary": {
      "accuracy_percentage": 100.0,
      "total_discrepancies": 0,
      "largest_positive_diff": 0,
      "largest_negative_diff": 0
    }
  },
  "parameters": {
    "produto_ids_requested": 5,
    "limit_applied": 100,
    "validation_timestamp": "2025-09-14T10:30:00.000Z"
  }
}
```

### 3. Find Stock Discrepancies

**Endpoint:** `GET /api/estoque-controle/stock_discrepancies/`

Find products with stock discrepancies above a threshold, sorted by magnitude.

**Parameters:**
- `threshold` (optional): Decimal - Minimum difference to consider as discrepancy (default: 0.01)
- `limit` (optional): Integer - Maximum number of discrepancies to return (default: 50, max: 500)

**Example Request:**
```bash
curl "http://localhost:8000/api/estoque-controle/stock_discrepancies/?threshold=1.0&limit=20"
```

**Example Response:**
```json
{
  "discrepancies": [
    {
      "produto_id": 5828,
      "produto_codigo": "5828",
      "produto_nome": "PAPEL A4 BRANCO PRESTIGE 75G 21X29,7 500F",
      "calculated_stock": 5470.085,
      "stored_stock": 0.0,
      "difference": 5470.085,
      "abs_difference": 5470.085
    },
    {
      "produto_id": 4094,
      "produto_codigo": "4094",
      "produto_nome": "GARRAFA TONER PRETO/RC AF 1515/2015/2016/2018",
      "calculated_stock": 1032.0,
      "stored_stock": 0.0,
      "difference": 1032.0,
      "abs_difference": 1032.0
    }
  ],
  "summary": {
    "total_discrepancies_found": 781,
    "discrepancies_returned": 20,
    "average_absolute_difference": 245.678,
    "maximum_absolute_difference": 5470.085,
    "positive_differences": 750,
    "negative_differences": 31,
    "threshold_used": 1.0
  },
  "parameters": {
    "threshold": 1.0,
    "limit_applied": 20,
    "search_timestamp": "2025-09-14T10:30:00.000Z"
  }
}
```

### 4. Generate Validation Report

**Endpoint:** `GET /api/estoque-controle/validation_report/`

Generate comprehensive stock validation report with analysis and recommendations.

**Parameters:**
- `produto_ids` (optional): String - Comma-separated list of product IDs to analyze
- `sample_size` (optional): Integer - Number of products to analyze if no specific IDs (default: 200, max: 1000)

**Example Request:**
```bash
# Report for specific products
curl "http://localhost:8000/api/estoque-controle/validation_report/?produto_ids=1,2,3"

# Report for sample of products
curl "http://localhost:8000/api/estoque-controle/validation_report/?sample_size=100"
```

**Example Response:**
```json
{
  "total_products": 5,
  "correct_stock": 5,
  "incorrect_stock": 0,
  "discrepancies": [],
  "validation_date": "2025-09-14T10:30:00.000Z",
  "summary": {
    "accuracy_percentage": 100.0,
    "total_discrepancies": 0,
    "largest_positive_diff": 0,
    "largest_negative_diff": 0
  },
  "analysis": {
    "products_with_zero_calculated": 0,
    "products_with_zero_stored": 0,
    "products_with_negative_calculated": 0,
    "products_with_negative_stored": 0,
    "average_difference": 0,
    "median_difference": 0
  },
  "recommendations": [],
  "metadata": {
    "report_generated_at": "2025-09-14T10:30:00.000Z",
    "products_analyzed": 5,
    "sample_size_requested": 200,
    "analysis_scope": "specific_products"
  }
}
```

### 5. Product Stock Detail

**Endpoint:** `GET /api/estoque-controle/product_stock_detail/`

Get detailed stock information for a single product including movement history.

**Parameters:**
- `produto_id` (required): Integer - ID of the product
- `days_history` (optional): Integer - Number of days of movement history to include (default: 30, max: 365)

**Example Request:**
```bash
curl "http://localhost:8000/api/estoque-controle/product_stock_detail/?produto_id=1&days_history=30"
```

**Example Response:**
```json
{
  "product_validation": {
    "produto_id": 1,
    "produto_codigo": "1",
    "produto_nome": "UNIDADE IMP TIPO 4545A-DX4545/DX3343",
    "calculated_stock": 0.0,
    "stored_stock": 0.0,
    "difference": 0.0,
    "is_correct": true,
    "stock_reset_info": {
      "has_reset": false,
      "reset_date": null,
      "reset_quantity": null,
      "total_resets": 0
    },
    "movement_info": {
      "total_movements": 0,
      "regular_movements": 0
    },
    "validation_date": "2025-09-14T10:30:00.000Z"
  },
  "current_stock_comparison": {
    "calculated_stock": 0.0,
    "stored_stock": 0.0,
    "difference": 0.0,
    "is_accurate": true,
    "calculation_date": "2025-09-14"
  },
  "movement_history": {
    "period": {
      "start_date": "2025-08-15",
      "end_date": "2025-09-14",
      "days_analyzed": 30
    },
    "summary": {
      "total_movements": 0,
      "total_resets": 0,
      "total_regular_movements": 0
    },
    "totals": {
      "entrada": 0.0,
      "saida": 0.0,
      "net_movement": 0.0
    },
    "stock_resets": [],
    "recent_movements": []
  },
  "metadata": {
    "analysis_timestamp": "2025-09-14T10:30:00.000Z",
    "days_history_requested": 30
  }
}
```

## Error Responses

All endpoints return consistent error responses:

**400 Bad Request:**
```json
{
  "error": "Parameter produto_id is required"
}
```

**404 Not Found:**
```json
{
  "error": "Product with ID 999 not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error: [error details]"
}
```

## Key Features

### Stock Reset Handling
- Properly processes "000000" document references as stock resets
- Uses most recent reset as base stock for calculations
- Ignores movements before the most recent reset

### Chronological Processing
- Applies stock movements in correct date order
- Handles same-day movements properly
- Supports entrada (E) and saída (S) movement types

### Validation & Analysis
- Compares calculated vs stored stock values
- Identifies discrepancies with configurable thresholds
- Provides detailed analysis and recommendations
- Generates comprehensive validation reports

### Performance Considerations
- Includes limits on result sets to prevent timeouts
- Optimized queries with proper database relationships
- Caching-friendly design for frequently accessed data

## Usage Examples

### Check Stock Accuracy for All Products
```bash
# Get validation report for sample of products
curl "http://localhost:8000/api/estoque-controle/validation_report/?sample_size=500"
```

### Find Products with Large Stock Discrepancies
```bash
# Find products with differences > 10 units
curl "http://localhost:8000/api/estoque-controle/stock_discrepancies/?threshold=10&limit=50"
```

### Analyze Specific Product in Detail
```bash
# Get complete analysis for product ID 5828
curl "http://localhost:8000/api/estoque-controle/product_stock_detail/?produto_id=5828&days_history=90"
```

### Calculate Historical Stock
```bash
# Calculate stock for product on specific date
curl "http://localhost:8000/api/estoque-controle/calculate_historical_stock/?produto_id=5828&data=2025-01-01"
```

## Integration Notes

- All endpoints are integrated into the existing EstoqueViewSet
- Uses the same authentication and permissions as other stock endpoints
- Compatible with existing Django REST Framework setup
- Follows the same URL pattern as other endpoints in the system

## Next Steps

After implementing these API endpoints, consider:

1. **Management Commands**: Create Django management commands for batch stock validation and correction
2. **Database Optimization**: Add indexes for better query performance
3. **Caching**: Implement caching for frequently accessed stock calculations
4. **Monitoring**: Add logging and monitoring for stock discrepancy detection
5. **Frontend Integration**: Update frontend components to use the new accurate stock data