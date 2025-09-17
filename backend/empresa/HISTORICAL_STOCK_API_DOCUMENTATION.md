# Historical Stock Analysis API Documentation

## Overview

The Historical Stock Analysis API provides endpoints for calculating historical stock levels, analyzing stock movements over time, and generating reports for audit and business intelligence purposes.

**Important**: This API is designed for **historical analysis only**. Current stock values in `produtos.estoque_atual` are authoritative and should not be modified.

## Base URL

All endpoints are available under:
```
/api/estoque-controle/
```

## Core Concept

The API uses stock movements (`movimentacoes_estoque`) and stock resets (`documento_referencia = "000000"`) to calculate historical stock levels at any point in time.

## Endpoints

### 1. Calculate Historical Stock

**Endpoint:** `GET /api/estoque-controle/calculate_historical_stock/`

Calculate what the stock level was for a specific product at any historical date.

**Parameters:**
- `produto_id` (required): Integer - ID of the product
- `data` (required): String - Date in YYYY-MM-DD format (cannot be future date)

**Example Request:**
```bash
curl "http://localhost:8000/api/estoque-controle/calculate_historical_stock/?produto_id=5828&data=2024-12-31"
```

**Example Response:**
```json
{
  "produto": {
    "id": 5828,
    "codigo": "5828",
    "nome": "PAPEL A4 BRANCO PRESTIGE 75G 21X29,7 500F",
    "ativo": true,
    "current_stock": 0.0
  },
  "historical_calculation": {
    "target_date": "2024-12-31",
    "historical_stock": 5470.085,
    "calculation_method": "movements_and_resets"
  },
  "calculation_basis": {
    "has_stock_reset": false,
    "reset_date": null,
    "reset_quantity": null,
    "base_calculation": "zero_start"
  }
}
```

### 2. Stock Movements Analysis

**Endpoint:** `GET /api/estoque-controle/stock_movements_analysis/`

Analyze stock movements for products over a specified period.

**Parameters:**
- `start_date` (required): String - Start date in YYYY-MM-DD format
- `end_date` (required): String - End date in YYYY-MM-DD format
- `produto_ids` (optional): String - Comma-separated list of product IDs
- `limit` (optional): Integer - Maximum products to analyze (default: 50, max: 500)

**Example Request:**
```bash
curl "http://localhost:8000/api/estoque-controle/stock_movements_analysis/?start_date=2024-01-01&end_date=2024-12-31&limit=10"
```

**Example Response:**
```json
{
  "analysis_results": [
    {
      "produto": {
        "id": 5828,
        "codigo": "5828",
        "nome": "PAPEL A4 BRANCO PRESTIGE 75G 21X29,7 500F",
        "current_stock": 0.0
      },
      "period_analysis": {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "stock_at_start": 5470.085,
        "stock_at_end": 5470.085,
        "net_change": 0.0
      },
      "movements": {
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
  ],
  "summary": {
    "period": {
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "days_analyzed": 365
    },
    "products_analyzed": 1,
    "products_with_movements": 0
  }
}
```

### 3. Stock Timeline

**Endpoint:** `GET /api/estoque-controle/stock_timeline/`

Generate a timeline showing how stock levels changed over time for a specific product.

**Parameters:**
- `produto_id` (required): Integer - ID of the product
- `start_date` (required): String - Start date in YYYY-MM-DD format
- `end_date` (required): String - End date in YYYY-MM-DD format
- `interval` (optional): String - 'daily', 'weekly', or 'monthly' (default: 'daily')

**Example Request:**
```bash
curl "http://localhost:8000/api/estoque-controle/stock_timeline/?produto_id=5828&start_date=2024-01-01&end_date=2024-01-31&interval=weekly"
```

**Example Response:**
```json
{
  "produto": {
    "id": 5828,
    "codigo": "5828",
    "nome": "PAPEL A4 BRANCO PRESTIGE 75G 21X29,7 500F",
    "current_stock": 0.0
  },
  "timeline": {
    "period": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31",
      "interval": "weekly"
    },
    "points": [
      {
        "date": "2024-01-01",
        "stock_level": 5470.085
      },
      {
        "date": "2024-01-08",
        "stock_level": 5470.085
      },
      {
        "date": "2024-01-15",
        "stock_level": 5470.085
      },
      {
        "date": "2024-01-22",
        "stock_level": 5470.085
      },
      {
        "date": "2024-01-29",
        "stock_level": 5470.085
      }
    ],
    "statistics": {
      "total_points": 5,
      "valid_points": 5,
      "min_stock": 5470.085,
      "max_stock": 5470.085,
      "avg_stock": 5470.09
    }
  }
}
```

### 4. Stock Resets Report

**Endpoint:** `GET /api/estoque-controle/stock_resets_report/`

Analyze stock reset patterns and their impact on inventory levels.

**Parameters:**
- `produto_ids` (optional): String - Comma-separated list of product IDs
- `start_date` (optional): String - Start date for analysis in YYYY-MM-DD format
- `end_date` (optional): String - End date for analysis in YYYY-MM-DD format
- `limit` (optional): Integer - Maximum products to analyze (default: 100, max: 500)

**Example Request:**
```bash
curl "http://localhost:8000/api/estoque-controle/stock_resets_report/?start_date=2024-01-01&limit=5"
```

**Example Response:**
```json
{
  "reset_analysis": [
    {
      "produto": {
        "id": 3051,
        "codigo": "3051",
        "nome": "UNIDADE DE IMAGEM TIPO 1175 DSM 516PF",
        "current_stock": 0.0
      },
      "resets": [
        {
          "date": "2024-08-21",
          "quantity": 1.0,
          "movement_type": "Entrada de Estoque"
        }
      ]
    }
  ],
  "summary": {
    "total_resets": 15,
    "products_with_resets": 12,
    "products_returned": 5,
    "reset_date_range": {
      "earliest": "2024-01-01",
      "latest": "2024-08-21"
    },
    "analysis_period": {
      "start_date": "2024-01-01",
      "end_date": null
    }
  }
}
```

### 5. Product Stock History

**Endpoint:** `GET /api/estoque-controle/product_stock_history/`

Get comprehensive stock history for a single product including movements and analysis.

**Parameters:**
- `produto_id` (required): Integer - ID of the product
- `days_history` (optional): Integer - Days of history to include (default: 90, max: 1095)
- `include_movements` (optional): Boolean - Include detailed movement list (default: true)

**Example Request:**
```bash
curl "http://localhost:8000/api/estoque-controle/product_stock_history/?produto_id=5828&days_history=180&include_movements=true"
```

**Example Response:**
```json
{
  "produto": {
    "id": 5828,
    "codigo": "5828",
    "nome": "PAPEL A4 BRANCO PRESTIGE 75G 21X29,7 500F",
    "current_stock": 0.0,
    "ativo": true
  },
  "analysis_period": {
    "start_date": "2024-03-17",
    "end_date": "2024-09-14",
    "days_analyzed": 180
  },
  "stock_levels": {
    "stock_at_period_start": 5470.085,
    "stock_at_period_end": 5470.085,
    "current_stock_from_table": 0.0,
    "net_change_in_period": 0.0
  },
  "stock_reset_info": {
    "has_recent_reset": false,
    "most_recent_reset_date": null,
    "reset_quantity": null,
    "total_resets_in_period": 0
  },
  "movement_summary": {
    "total_movements": 0,
    "regular_movements": 0,
    "stock_resets": 0,
    "totals": {
      "entrada": 0.0,
      "saida": 0.0,
      "net_movement": 0.0
    }
  },
  "detailed_movements": {
    "stock_resets": [],
    "regular_movements": []
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

### Historical Accuracy
- Calculates stock levels at any historical date
- Applies movements chronologically
- Handles entrada (E) and saída (S) movement types correctly

### Reporting & Analytics
- Timeline analysis for trend identification
- Movement pattern analysis
- Stock reset impact analysis
- Comprehensive historical reporting

## Use Cases

### Business Intelligence
```bash
# Analyze stock trends over the year
curl "/api/estoque-controle/stock_timeline/?produto_id=5828&start_date=2024-01-01&end_date=2024-12-31&interval=monthly"
```

### Audit & Compliance
```bash
# Generate stock history for audit
curl "/api/estoque-controle/product_stock_history/?produto_id=5828&days_history=365"
```

### Period-End Reporting
```bash
# Calculate stock levels at month-end
curl "/api/estoque-controle/calculate_historical_stock/?produto_id=5828&data=2024-01-31"
```

### Movement Analysis
```bash
# Analyze movements during Q1
curl "/api/estoque-controle/stock_movements_analysis/?start_date=2024-01-01&end_date=2024-03-31"
```

## Important Notes

1. **Current Stock Authority**: `produtos.estoque_atual` is the authoritative current stock value
2. **Historical Purpose**: This API is for historical analysis, not current stock validation
3. **Date Limitations**: Cannot calculate stock for future dates
4. **Performance**: Large date ranges may take longer to process
5. **Stock Resets**: "000000" movements establish new baseline stock levels

## Integration Guidelines

- Use for historical reporting and analysis
- Do not use to validate or correct current stock values
- Implement appropriate caching for frequently accessed historical data
- Consider date range limitations for performance
- Use appropriate intervals for timeline analysis to avoid excessive data points