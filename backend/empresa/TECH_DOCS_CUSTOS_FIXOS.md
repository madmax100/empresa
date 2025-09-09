# 🔧 Documentação Técnica - Endpoint Custos Fixos

## 📝 Especificação da API

### Endpoint Information
- **URL**: `/contas/relatorios/custos-fixos/`
- **Method**: `GET`
- **Content-Type**: `application/json`
- **Response Format**: `JSON`

### Request Parameters

#### Required
```python
data_inicio: str  # Format: YYYY-MM-DD
data_fim: str     # Format: YYYY-MM-DD
```

#### Optional
```python
categorias: str   # CSV format: "cat1,cat2,cat3"
```

### Response Schema

```python
{
    "parametros": {
        "data_inicio": "string (date)",
        "data_fim": "string (date)", 
        "filtro_aplicado": "string",
        "fonte_dados": "string"
    },
    "estatisticas_fornecedores": {
        "total_fornecedores_fixos_cadastrados": "integer",
        "fornecedores_com_pagamentos_no_periodo": "integer"
    },
    "totais_gerais": {
        "total_valor_original": "decimal",
        "total_valor_pago": "decimal",
        "total_juros": "decimal", 
        "total_tarifas": "decimal"
    },
    "resumo_por_tipo_fornecedor": [
        {
            "fornecedor__tipo": "string",
            "total_pago": "decimal",
            "quantidade_contas": "integer",
            "total_valor_original": "decimal",
            "total_juros": "decimal",
            "total_tarifas": "decimal"
        }
    ],
    "resumo_por_fornecedor": [
        {
            "fornecedor__nome": "string",
            "fornecedor__tipo": "string", 
            "total_pago": "decimal",
            "quantidade_contas": "integer",
            "total_valor_original": "decimal",
            "total_juros": "decimal",
            "total_tarifas": "decimal"
        }
    ],
    "total_contas_pagas": "integer",
    "contas_pagas": [
        {
            "id": "integer",
            "data_pagamento": "string (date)",
            "data_vencimento": "string (date)",
            "valor_original": "decimal",
            "valor_pago": "decimal",
            "juros": "decimal",
            "tarifas": "decimal", 
            "valor_total_pago": "decimal",
            "historico": "string",
            "fornecedor": "string",
            "fornecedor_tipo": "string",
            "conta_bancaria": "string",
            "forma_pagamento": "string",
            "numero_duplicata": "string"
        }
    ]
}
```

## 🗄️ Database Schema

### Tables Used

#### ContasPagar
```sql
CREATE TABLE contas_pagar (
    id SERIAL PRIMARY KEY,
    status VARCHAR(1) NOT NULL,           -- 'P' = Pago
    data_pagamento TIMESTAMP,
    vencimento DATE,
    valor DECIMAL(10,2),
    valor_pago DECIMAL(10,2), 
    juros DECIMAL(10,2),
    tarifas DECIMAL(10,2),
    valor_total_pago DECIMAL(10,2),
    historico TEXT,
    forma_pagamento VARCHAR(50),
    numero_duplicata VARCHAR(50),
    fornecedor_id INTEGER REFERENCES fornecedores(id),
    conta_id INTEGER REFERENCES contas_bancarias(id)
);
```

#### Fornecedores
```sql
CREATE TABLE fornecedores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(50),                     -- 'DESPESA FIXA' | 'CUSTO FIXO'
    -- outros campos...
);
```

### Indexes Recommended
```sql
-- Performance indexes
CREATE INDEX idx_contas_pagar_status_data ON contas_pagar(status, data_pagamento);
CREATE INDEX idx_contas_pagar_fornecedor ON contas_pagar(fornecedor_id);
CREATE INDEX idx_fornecedores_tipo ON fornecedores(tipo);

-- Query optimization
CREATE INDEX idx_contas_pagar_vencimento ON contas_pagar(vencimento);
CREATE INDEX idx_fornecedores_nome ON fornecedores(nome);
```

## 💻 Implementation Details

### Class Structure
```python
class RelatorioCustosFixosView(APIView):
    """
    API View for fixed costs reporting
    
    Filters ContasPagar by:
    - Status = 'P' (Paid)
    - Suppliers with type 'DESPESA FIXA' or 'CUSTO FIXO'
    - Payment date within specified range
    """
    
    def get(self, request, *args, **kwargs):
        # 1. Parameter validation
        # 2. Date parsing and validation
        # 3. Business logic filtering
        # 4. Data aggregation
        # 5. Response formatting
```

### Query Logic
```python
# 1. Get eligible suppliers
fornecedores_fixos = Fornecedores.objects.filter(
    Q(tipo__icontains='DESPESA FIXA') | Q(tipo__icontains='CUSTO FIXO')
).values_list('id', flat=True)

# 2. Filter paid accounts in period
queryset = ContasPagar.objects.filter(
    status='P',
    data_pagamento__date__range=(data_inicio, data_fim),
    fornecedor_id__in=fornecedores_fixos
).select_related('fornecedor', 'conta').order_by('-data_pagamento')

# 3. Aggregations
resumo_por_tipo = queryset.values('fornecedor__tipo').annotate(
    total_pago=Sum('valor_total_pago'),
    quantidade_contas=Count('id'),
    total_valor_original=Sum('valor'),
    total_juros=Sum('juros'),
    total_tarifas=Sum('tarifas')
).order_by('-total_pago')
```

## 🚀 Performance Considerations

### Query Optimization
```python
# Use select_related for foreign keys
.select_related('fornecedor', 'conta')

# Use values_list for ID-only queries  
.values_list('id', flat=True)

# Aggregate in database, not Python
.aggregate(soma_total_pago=Sum('valor_total_pago'))

# Use Q objects for complex filters
Q(tipo__icontains='DESPESA FIXA') | Q(tipo__icontains='CUSTO FIXO')
```

### Caching Strategy (Future)
```python
from django.core.cache import cache

def get_custos_fixos_cached(data_inicio, data_fim):
    cache_key = f"custos_fixos_{data_inicio}_{data_fim}"
    result = cache.get(cache_key)
    
    if result is None:
        result = calculate_custos_fixos(data_inicio, data_fim)
        cache.set(cache_key, result, timeout=3600)  # 1 hour
    
    return result
```

## 🧪 Testing

### Unit Tests (To Implement)
```python
# tests/test_relatorios_views.py
from django.test import TestCase
from rest_framework.test import APIClient

class TestRelatorioCustosFixos(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Setup test data
        
    def test_valid_date_range(self):
        response = self.client.get('/contas/relatorios/custos-fixos/', {
            'data_inicio': '2024-01-01',
            'data_fim': '2024-01-31'
        })
        self.assertEqual(response.status_code, 200)
        
    def test_invalid_date_format(self):
        response = self.client.get('/contas/relatorios/custos-fixos/', {
            'data_inicio': 'invalid-date',
            'data_fim': '2024-01-31'
        })
        self.assertEqual(response.status_code, 400)
        
    def test_missing_parameters(self):
        response = self.client.get('/contas/relatorios/custos-fixos/')
        self.assertEqual(response.status_code, 400)
```

### Integration Tests
```python
def test_with_real_data(self):
    """Test with migrated Access data"""
    response = self.client.get('/contas/relatorios/custos-fixos/', {
        'data_inicio': '2023-01-01',
        'data_fim': '2024-12-31'
    })
    
    data = response.json()
    
    # Validate structure
    self.assertIn('parametros', data)
    self.assertIn('totais_gerais', data)
    self.assertIn('contas_pagas', data)
    
    # Validate business logic
    self.assertGreater(data['total_contas_pagas'], 0)
    self.assertGreater(data['totais_gerais']['total_valor_pago'], 0)
```

## 🔍 Debugging and Monitoring

### Logging
```python
import logging

logger = logging.getLogger(__name__)

def get(self, request, *args, **kwargs):
    logger.info(f"Custos fixos request: {request.query_params}")
    
    try:
        # ... business logic ...
        logger.info(f"Custos fixos response: {len(queryset)} records")
        return Response(response_data)
    except Exception as e:
        logger.error(f"Custos fixos error: {str(e)}")
        raise
```

### Performance Monitoring
```python
import time
from django.db import connection

def get(self, request, *args, **kwargs):
    start_time = time.time()
    
    # ... business logic ...
    
    end_time = time.time()
    query_count = len(connection.queries)
    
    logger.info(f"Custos fixos performance: {end_time - start_time:.2f}s, {query_count} queries")
```

## 🚨 Error Handling

### Custom Exceptions
```python
class CustosFixosValidationError(Exception):
    pass

class CustosFixosDataError(Exception):  
    pass
```

### Error Response Format
```python
{
    "error": "string",
    "error_code": "string", 
    "details": "object (optional)"
}
```

### HTTP Status Codes
- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Unexpected error

## 🔧 Configuration

### Settings Variables
```python
# settings.py

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'empresa',
        # ... other config
    }
}

# Pagination (future)
CUSTOS_FIXOS_PAGE_SIZE = 100

# Cache (future)
CUSTOS_FIXOS_CACHE_TIMEOUT = 3600  # 1 hour
```

### Environment Variables
```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/empresa
DEBUG=True
ACCESS_DB_PATH=C:\path\to\database.mdb
```

## 📦 Dependencies

### Python Packages
```txt
Django==5.2.1
djangorestframework==3.14.0
psycopg2-binary==2.9.7
python-decouple==3.8  # For environment variables
```

### System Requirements
- Python 3.8+
- PostgreSQL 12+
- 4GB RAM minimum
- 10GB disk space

## 🔄 Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure proper database credentials
- [ ] Set up SSL/HTTPS
- [ ] Configure authentication/authorization
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set up caching (Redis/Memcached)
- [ ] Configure web server (Nginx/Apache)

### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 📊 Monitoring Metrics

### Key Performance Indicators
- Response time (target: < 1s)
- Query count (target: < 10 queries)
- Memory usage
- Error rate
- Request volume

### Database Metrics
- Connection pool usage
- Query execution time
- Index usage
- Table size growth

---

**📅 Last Updated:** September 8, 2025  
**🔧 API Version:** 1.0.0  
**👨‍💻 Target Audience:** Backend Developers
