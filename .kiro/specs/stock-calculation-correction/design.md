# Stock Calculation Correction - Design Document

## Overview

This design implements a historical stock calculation system that properly handles stock movements and stock resets (documento_referencia "000000") to calculate accurate stock levels for any given date. The system will provide functions to calculate historical stock and validate current stock levels against the produtos table.

## Architecture

### Integration with Existing Django Backend

The solution will integrate with the existing Django backend at `backend/empresa/` using the current models:
- `MovimentacoesEstoque` (stock movements)
- `Produtos` (products with estoque_atual field)
- `TiposMovimentacaoEstoque` (movement types)

### Core Components

1. **StockCalculationService**: Django service class for stock calculations
2. **StockValidationService**: Validates current stock vs calculated stock
3. **StockAPI**: REST API endpoints for stock calculations
4. **Management Commands**: Django commands for data correction

### Data Flow

```
MovimentacoesEstoque → StockCalculationService → Historical Stock Value
                                            ↓
Produtos.estoque_atual ← StockValidationService ← Current Date Calculation
                                            ↓
                              REST API Endpoints ← Frontend Requests
```

## Components and Interfaces

### 1. StockCalculationService (Django Service)

```python
# backend/empresa/contas/services/stock_calculation.py
class StockCalculationService:
    @staticmethod
    def calculate_stock_at_date(produto_id: int, target_date: date) -> Decimal:
        """Calculate stock for a product at a specific date"""
        
    @staticmethod
    def get_base_stock_reset(produto_id: int, target_date: date) -> tuple:
        """Find the most recent '000000' reset before target date"""
        
    @staticmethod
    def apply_movements_after_reset(produto_id: int, reset_date: date, target_date: date, base_stock: Decimal) -> Decimal:
        """Apply all movements between reset date and target date"""
```

### 2. StockValidationService (Django Service)

```python
# backend/empresa/contas/services/stock_validation.py
class StockValidationService:
    @staticmethod
    def validate_current_stock() -> dict:
        """Compare calculated current stock vs produtos.estoque_atual"""
        
    @staticmethod
    def generate_validation_report() -> dict:
        """Generate comprehensive validation report"""
        
    @staticmethod
    def find_stock_discrepancies() -> list:
        """Find products with stock discrepancies"""
```

### 3. Stock API Views (Django REST Framework)

```python
# backend/empresa/contas/views/stock_views.py
class StockCalculationViewSet(viewsets.ViewSet):
    def calculate_historical_stock(self, request):
        """API endpoint to calculate stock at specific date"""
        
    def validate_current_stock(self, request):
        """API endpoint to validate current stock levels"""
        
    def get_stock_discrepancies(self, request):
        """API endpoint to get stock discrepancies report"""
```

### 4. Management Commands (Django Commands)

```python
# backend/empresa/contas/management/commands/fix_stock_data.py
class Command(BaseCommand):
    def handle(self, *args, **options):
        """Fix stock movement data issues"""
        
# backend/empresa/contas/management/commands/validate_stock.py
class Command(BaseCommand):
    def handle(self, *args, **options):
        """Validate all product stock levels"""
```

## Data Models

### Movement Processing Logic

```sql
-- Base stock reset query
SELECT quantidade, data_movimentacao 
FROM movimentacoes_estoque 
WHERE produto_id = ? 
  AND documento_referencia = '000000' 
  AND data_movimentacao <= ?
ORDER BY data_movimentacao DESC 
LIMIT 1;

-- Movements after reset query
SELECT quantidade, tipo_movimentacao_id, data_movimentacao
FROM movimentacoes_estoque me
JOIN tipos_movimentacao_estoque tme ON me.tipo_movimentacao_id = tme.id
WHERE me.produto_id = ?
  AND me.documento_referencia != '000000'
  AND me.data_movimentacao > ?
  AND me.data_movimentacao <= ?
ORDER BY me.data_movimentacao ASC;
```

### Stock Calculation Algorithm

1. **Find Base Stock**: Look for most recent "000000" movement before target date
2. **Set Starting Point**: Use reset quantity or 0 if no reset found
3. **Apply Movements**: Process all non-"000000" movements chronologically
4. **Calculate Result**: Apply entrada (+) and saída (-) operations

## Error Handling

### Data Quality Issues

1. **Missing Movement Types**: Log warning and skip movement
2. **Invalid Dates**: Use current date as fallback
3. **Negative Stock**: Allow but log warning for investigation
4. **Duplicate Resets**: Use most recent reset on same date

### Performance Considerations

1. **Caching**: Cache recent calculations for frequently accessed products
2. **Batch Processing**: Process multiple products in single database query
3. **Indexing**: Ensure proper indexes on produto_id, data_movimentacao, documento_referencia

## Testing Strategy

### Unit Tests

1. **Stock Calculation Logic**: Test various scenarios with resets and movements
2. **Edge Cases**: Test products with no movements, multiple resets, same-day movements
3. **Data Validation**: Test validation logic with known good/bad data

### Integration Tests

1. **Database Queries**: Test actual database queries with sample data
2. **Performance**: Test calculation speed with large datasets
3. **Migration Correction**: Test correction of actual migration data

### Test Scenarios

```python
# Test Case 1: Product with stock reset
# - Reset on 2024-01-01: quantity = 100
# - Movement on 2024-01-15: entrada +50
# - Movement on 2024-01-20: saída -30
# - Expected stock on 2024-01-25: 120

# Test Case 2: Product with multiple resets
# - Reset on 2024-01-01: quantity = 100
# - Reset on 2024-02-01: quantity = 200
# - Movement on 2024-02-15: entrada +25
# - Expected stock on 2024-02-20: 225

# Test Case 3: Product with no reset
# - Movement on 2024-01-10: entrada +75
# - Movement on 2024-01-20: saída -25
# - Expected stock on 2024-01-25: 50
```

## Django Integration Details

### File Structure
```
backend/empresa/
├── contas/
│   ├── services/
│   │   ├── stock_calculation.py
│   │   └── stock_validation.py
│   ├── views/
│   │   └── stock_views.py
│   ├── management/
│   │   └── commands/
│   │       ├── fix_stock_data.py
│   │       └── validate_stock.py
│   └── tests/
│       ├── test_stock_calculation.py
│       └── test_stock_validation.py
```

### API Endpoints
```
GET /api/stock/calculate/?produto_id=123&date=2024-01-15
GET /api/stock/validate/
GET /api/stock/discrepancies/
POST /api/stock/fix-data/
```

## Implementation Plan

### Phase 1: Core Stock Calculation Service
- Create StockCalculationService in Django services
- Implement calculate_stock_at_date method
- Add unit tests for calculation logic
- Handle "000000" reset logic properly

### Phase 2: Stock Validation Service  
- Create StockValidationService
- Implement current stock validation
- Add discrepancy detection and reporting
- Create validation management command

### Phase 3: REST API Endpoints
- Create StockCalculationViewSet
- Add API endpoints for stock calculations
- Implement proper error handling and responses
- Add API documentation

### Phase 4: Data Quality Management Commands
- Create fix_stock_data management command
- Add data validation and correction logic
- Implement batch processing for large datasets
- Add progress reporting and logging

### Phase 5: Testing and Integration
- Comprehensive unit and integration tests
- Performance testing with real migration data
- Frontend integration testing
- Documentation and deployment