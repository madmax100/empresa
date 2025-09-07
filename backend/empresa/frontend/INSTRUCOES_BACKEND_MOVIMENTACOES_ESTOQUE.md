# 📋 Instruções para Backend - Endpoint de Movimentações de Estoque

## 🎯 Objetivo

Modificar o endpoint `/api/estoque-controle/movimentacoes_periodo/` para incluir todas as informações necessárias para a página de estoque do frontend, especialmente o último preço de entrada de cada produto e cálculos de valor de saída baseados no preço de entrada.

## 🚨 Problema Atual

- Valores de saída com preços de entrada zerados
- Frontend fazendo cálculos que deveriam ser feitos no backend
- Inconsistências entre totais e detalhes das movimentações
- Falta de informação sobre último preço de entrada dos produtos

## 🔧 Modificações Necessárias

### 1. Estrutura de Resposta Expandida

O endpoint deve retornar a seguinte estrutura JSON:

```json
{
  "produtos_movimentados": [
    {
      "produto_id": 6440,
      "nome": "MULTIFUNCIONAL KONICA MINOLTA C258",
      "referencia": "MFC258",
      "quantidade_entrada": 4.0,
      "quantidade_saida": 4.0,
      "valor_entrada": 53048.34,
      "valor_saida": 40091.12,
      "saldo_quantidade": 0.0,
      "saldo_valor": 12957.22,
      "total_movimentacoes": 8,
      "primeira_movimentacao": "2025-01-02 10:30:00",
      "ultima_movimentacao": "2025-01-28 16:45:00",
      
      // ✨ NOVOS CAMPOS OBRIGATÓRIOS
      "ultimo_preco_entrada": 13262.085,
      "data_ultimo_preco_entrada": "2024-12-15 14:20:00",
      "valor_saida_preco_entrada": 53048.34,
      "diferenca_preco": -12957.22,
      "tem_entrada_anterior": true,
      
      // ✨ MOVIMENTAÇÕES DETALHADAS MELHORADAS
      "movimentacoes_detalhadas": [
        {
          "id": 12345,
          "data": "2025-01-02 10:30:00",
          "tipo": "ENT - Entrada de Estoque",
          "tipo_codigo": "ENT",
          "quantidade": 2.0,
          "valor_unitario": 13262.085,
          "valor_total": 26524.17,
          "documento": "7845",
          "operador": "TIAGO",
          "observacoes": "NF COMPRA GER.: 7845 - ENTRADA - Operador: TIAGO",
          "nota_fiscal": {
            "numero": "7845",
            "tipo": "COMPRA",
            "fornecedor": "FORNECEDOR XYZ LTDA"
          },
          "is_entrada": true,
          "is_saida": false
        },
        {
          "id": 12346,
          "data": "2025-01-15 14:20:00",
          "tipo": "SAI - Saída de Estoque",
          "tipo_codigo": "SAI",
          "quantidade": 1.0,
          "valor_unitario": 15000.00,
          "valor_total": 15000.00,
          "valor_saida_preco_entrada": 13262.085,
          "diferenca_unitaria": 1737.915,
          "documento": "41025",
          "operador": "MARIA",
          "observacoes": "NF VENDA GER.: 41025 - SAIDA - Operador: MARIA",
          "nota_fiscal": {
            "numero": "41025",
            "tipo": "VENDA",
            "cliente": "CLIENTE ABC LTDA"
          },
          "is_entrada": false,
          "is_saida": true
        }
      ]
    }
  ],
  "resumo": {
    "periodo": "2025-01-01 a 2025-01-31",
    "total_produtos": 77,
    "total_movimentacoes": 189,
    "valor_total_entradas": 101599.15,
    "valor_total_saidas": 104956.27,
    "valor_total_saidas_preco_entrada": 98234.56,
    "diferenca_total_precos": 6721.71,
    "margem_total": 6.4,
    "saldo_periodo": -3357.12,
    "quantidade_total_entradas": 244.0,
    "quantidade_total_saidas": 223.0,
    "produtos_com_entrada_anterior": 65,
    "produtos_sem_entrada_anterior": 12
  },
  "parametros": {
    "data_inicio": "2025-01-01",
    "data_fim": "2025-01-31",
    "incluir_detalhes": true,
    "limite_aplicado": null
  }
}
```

### 2. Campos Obrigatórios por Produto

#### **Campos Existentes (manter):**
- `produto_id`: ID único do produto
- `nome`: Nome do produto
- `referencia`: Código de referência
- `quantidade_entrada`: Total de entradas no período
- `quantidade_saida`: Total de saídas no período
- `valor_entrada`: Valor total das entradas no período
- `valor_saida`: Valor total das saídas no período
- `saldo_quantidade`: Diferença entre entradas e saídas
- `saldo_valor`: Diferença entre valores de entrada e saída
- `total_movimentacoes`: Número total de movimentações
- `primeira_movimentacao`: Data da primeira movimentação
- `ultima_movimentacao`: Data da última movimentação

#### **Novos Campos Obrigatórios:**
- `ultimo_preco_entrada`: Último preço unitário de entrada (mesmo fora do período)
- `data_ultimo_preco_entrada`: Data da última entrada que definiu o preço
- `valor_saida_preco_entrada`: Quantidade de saída × último preço de entrada
- `diferenca_preco`: Valor saída real - valor saída preço entrada
- `tem_entrada_anterior`: Boolean indicando se existe entrada anterior
- `movimentacoes_detalhadas`: Array com detalhes (quando solicitado)

### 3. Lógica de Cálculo do Último Preço de Entrada

```python
def obter_ultimo_preco_entrada(produto_id, data_limite=None):
    """
    Busca o último preço de entrada do produto, mesmo que seja anterior ao período.
    
    Args:
        produto_id (int): ID do produto
        data_limite (date, optional): Data limite para busca
    
    Returns:
        dict: {
            'preco': float,
            'data': datetime,
            'documento': str,
            'encontrado': bool
        }
    """
    from django.db.models import Q
    
    # Tipos de movimentação considerados como entrada
    tipos_entrada = ['ENT', 'ENTRADA', 'COMPRA', 'AJUSTE_POSITIVO', 'DEVOLUCAO_VENDA']
    
    query = MovimentacaoEstoque.objects.filter(
        produto_id=produto_id,
        tipo__in=tipos_entrada,
        quantidade__gt=0  # Garantir que é entrada positiva
    )
    
    if data_limite:
        query = query.filter(data__lte=data_limite)
    
    # Buscar a última entrada ordenada por data
    ultima_entrada = query.order_by('-data', '-id').first()
    
    if ultima_entrada and ultima_entrada.valor_unitario > 0:
        return {
            'preco': float(ultima_entrada.valor_unitario),
            'data': ultima_entrada.data,
            'documento': ultima_entrada.documento or '',
            'encontrado': True
        }
    
    return {
        'preco': 0.0,
        'data': None,
        'documento': '',
        'encontrado': False
    }
```

### 4. Cálculos Necessários

Para cada produto, calcular:

```python
def calcular_campos_produto(produto_data, ultimo_preco_info):
    """
    Calcula os campos derivados para um produto.
    """
    quantidade_saida = produto_data.get('quantidade_saida', 0)
    valor_saida = produto_data.get('valor_saida', 0)
    ultimo_preco = ultimo_preco_info.get('preco', 0)
    
    # Valor de saída baseado no preço de entrada
    valor_saida_preco_entrada = quantidade_saida * ultimo_preco
    
    # Diferença entre preço real de saída e preço de entrada
    diferenca_preco = valor_saida - valor_saida_preco_entrada
    
    # Percentual de margem (se houver saída)
    margem_percentual = 0
    if valor_saida_preco_entrada > 0:
        margem_percentual = (diferenca_preco / valor_saida_preco_entrada) * 100
    
    return {
        'ultimo_preco_entrada': ultimo_preco,
        'data_ultimo_preco_entrada': ultimo_preco_info.get('data'),
        'valor_saida_preco_entrada': valor_saida_preco_entrada,
        'diferenca_preco': diferenca_preco,
        'margem_percentual': margem_percentual,
        'tem_entrada_anterior': ultimo_preco_info.get('encontrado', False)
    }
```

### 5. Parâmetros do Endpoint

```
GET /api/estoque-controle/movimentacoes_periodo/
```

**Parâmetros:**
- `data_inicio` (obrigatório): Data de início no formato YYYY-MM-DD
- `data_fim` (obrigatório): Data de fim no formato YYYY-MM-DD
- `incluir_detalhes` (opcional, default=false): Incluir movimentações detalhadas
- `limite` (opcional): Limitar número de produtos retornados
- `produto_id` (opcional): Filtrar por produto específico
- `ordenar_por` (opcional): Campo para ordenação (valor_saida, diferenca_preco, etc.)
- `ordem` (opcional): ASC ou DESC

### 6. Query SQL Otimizada

```sql
-- Query principal para movimentações do período
WITH movimentacoes_periodo AS (
    SELECT 
        p.id as produto_id,
        p.nome,
        p.referencia,
        -- Entradas no período
        COALESCE(SUM(CASE 
            WHEN m.tipo IN ('ENT', 'ENTRADA', 'COMPRA') AND m.quantidade > 0 
            THEN m.quantidade ELSE 0 
        END), 0) as quantidade_entrada,
        COALESCE(SUM(CASE 
            WHEN m.tipo IN ('ENT', 'ENTRADA', 'COMPRA') AND m.quantidade > 0 
            THEN m.valor_total ELSE 0 
        END), 0) as valor_entrada,
        -- Saídas no período
        COALESCE(SUM(CASE 
            WHEN m.tipo IN ('SAI', 'SAIDA', 'VENDA') AND m.quantidade > 0 
            THEN m.quantidade ELSE 0 
        END), 0) as quantidade_saida,
        COALESCE(SUM(CASE 
            WHEN m.tipo IN ('SAI', 'SAIDA', 'VENDA') AND m.quantidade > 0 
            THEN m.valor_total ELSE 0 
        END), 0) as valor_saida,
        COUNT(m.id) as total_movimentacoes,
        MIN(m.data) as primeira_movimentacao,
        MAX(m.data) as ultima_movimentacao
    FROM produtos p
    INNER JOIN movimentacoes_estoque m ON p.id = m.produto_id 
        AND m.data BETWEEN :data_inicio AND :data_fim
    GROUP BY p.id, p.nome, p.referencia
),
ultimos_precos AS (
    SELECT DISTINCT
        mp.produto_id,
        FIRST_VALUE(m2.valor_unitario) OVER (
            PARTITION BY mp.produto_id 
            ORDER BY m2.data DESC, m2.id DESC
        ) as ultimo_preco_entrada,
        FIRST_VALUE(m2.data) OVER (
            PARTITION BY mp.produto_id 
            ORDER BY m2.data DESC, m2.id DESC
        ) as data_ultimo_preco_entrada
    FROM movimentacoes_periodo mp
    LEFT JOIN movimentacoes_estoque m2 ON mp.produto_id = m2.produto_id
        AND m2.tipo IN ('ENT', 'ENTRADA', 'COMPRA')
        AND m2.quantidade > 0
        AND m2.valor_unitario > 0
        AND m2.data <= :data_fim
)
SELECT 
    mp.*,
    COALESCE(up.ultimo_preco_entrada, 0) as ultimo_preco_entrada,
    up.data_ultimo_preco_entrada,
    -- Cálculos derivados
    mp.quantidade_saida * COALESCE(up.ultimo_preco_entrada, 0) as valor_saida_preco_entrada,
    mp.valor_saida - (mp.quantidade_saida * COALESCE(up.ultimo_preco_entrada, 0)) as diferenca_preco,
    CASE WHEN up.ultimo_preco_entrada IS NOT NULL THEN true ELSE false END as tem_entrada_anterior
FROM movimentacoes_periodo mp
LEFT JOIN ultimos_precos up ON mp.produto_id = up.produto_id
ORDER BY mp.valor_saida DESC;
```

### 7. Implementação Django/DRF

```python
# views.py
from django.db.models import (
    Sum, Count, Case, When, F, Q, Window, 
    Subquery, OuterRef, Value, BooleanField
)
from django.db.models.functions import Coalesce, FirstValue
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, date

class MovimentacoesPeriodoAPIView(APIView):
    def get(self, request):
        # Validação de parâmetros
        data_inicio = self.validate_date(request.GET.get('data_inicio'))
        data_fim = self.validate_date(request.GET.get('data_fim'))
        incluir_detalhes = request.GET.get('incluir_detalhes', 'false').lower() == 'true'
        produto_id = request.GET.get('produto_id')
        limite = request.GET.get('limite')
        
        if not data_inicio or not data_fim:
            return Response({
                'error': 'data_inicio e data_fim são obrigatórios'
            }, status=400)
        
        # Tipos de movimentação
        tipos_entrada = ['ENT', 'ENTRADA', 'COMPRA', 'AJUSTE_POSITIVO']
        tipos_saida = ['SAI', 'SAIDA', 'VENDA', 'AJUSTE_NEGATIVO']
        
        # Subquery para último preço de entrada
        ultimo_preco_subquery = MovimentacaoEstoque.objects.filter(
            produto_id=OuterRef('produto_id'),
            tipo__in=tipos_entrada,
            quantidade__gt=0,
            valor_unitario__gt=0,
            data__lte=data_fim
        ).order_by('-data', '-id').values('valor_unitario')[:1]
        
        data_ultimo_preco_subquery = MovimentacaoEstoque.objects.filter(
            produto_id=OuterRef('produto_id'),
            tipo__in=tipos_entrada,
            quantidade__gt=0,
            valor_unitario__gt=0,
            data__lte=data_fim
        ).order_by('-data', '-id').values('data')[:1]
        
        # Query principal
        queryset = MovimentacaoEstoque.objects.filter(
            data__range=[data_inicio, data_fim]
        )
        
        if produto_id:
            queryset = queryset.filter(produto_id=produto_id)
        
        produtos_movimentados = queryset.values(
            'produto_id', 
            'produto__nome', 
            'produto__referencia'
        ).annotate(
            nome=F('produto__nome'),
            referencia=F('produto__referencia'),
            
            # Entradas
            quantidade_entrada=Coalesce(Sum(Case(
                When(tipo__in=tipos_entrada, quantidade__gt=0, then=F('quantidade')),
                default=0
            )), 0),
            valor_entrada=Coalesce(Sum(Case(
                When(tipo__in=tipos_entrada, quantidade__gt=0, then=F('valor_total')),
                default=0
            )), 0),
            
            # Saídas
            quantidade_saida=Coalesce(Sum(Case(
                When(tipo__in=tipos_saida, quantidade__gt=0, then=F('quantidade')),
                default=0
            )), 0),
            valor_saida=Coalesce(Sum(Case(
                When(tipo__in=tipos_saida, quantidade__gt=0, then=F('valor_total')),
                default=0
            )), 0),
            
            # Contadores
            total_movimentacoes=Count('id'),
            primeira_movimentacao=Min('data'),
            ultima_movimentacao=Max('data'),
            
            # Último preço de entrada
            ultimo_preco_entrada=Coalesce(Subquery(ultimo_preco_subquery), 0),
            data_ultimo_preco_entrada=Subquery(data_ultimo_preco_subquery),
        ).annotate(
            # Cálculos derivados
            saldo_quantidade=F('quantidade_entrada') - F('quantidade_saida'),
            saldo_valor=F('valor_entrada') - F('valor_saida'),
            valor_saida_preco_entrada=F('quantidade_saida') * F('ultimo_preco_entrada'),
            diferenca_preco=F('valor_saida') - F('valor_saida_preco_entrada'),
            tem_entrada_anterior=Case(
                When(ultimo_preco_entrada__gt=0, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).order_by('-valor_saida')
        
        if limite:
            try:
                produtos_movimentados = produtos_movimentados[:int(limite)]
            except ValueError:
                pass
        
        # Converter para lista e adicionar detalhes se solicitado
        resultado = []
        for produto in produtos_movimentados:
            produto_dict = dict(produto)
            
            if incluir_detalhes:
                produto_dict['movimentacoes_detalhadas'] = self.obter_movimentacoes_detalhadas(
                    produto['produto_id'], data_inicio, data_fim
                )
            
            resultado.append(produto_dict)
        
        # Calcular resumo
        resumo = self.calcular_resumo(resultado, data_inicio, data_fim)
        
        return Response({
            'produtos_movimentados': resultado,
            'resumo': resumo,
            'parametros': {
                'data_inicio': data_inicio.isoformat(),
                'data_fim': data_fim.isoformat(),
                'incluir_detalhes': incluir_detalhes,
                'limite_aplicado': limite,
                'produto_id': produto_id
            }
        })
    
    def obter_movimentacoes_detalhadas(self, produto_id, data_inicio, data_fim):
        """Obtém movimentações detalhadas de um produto no período."""
        movimentacoes = MovimentacaoEstoque.objects.filter(
            produto_id=produto_id,
            data__range=[data_inicio, data_fim]
        ).select_related('produto', 'nota_fiscal').order_by('data')
        
        detalhes = []
        for mov in movimentacoes:
            is_entrada = mov.tipo in ['ENT', 'ENTRADA', 'COMPRA', 'AJUSTE_POSITIVO']
            
            detalhe = {
                'id': mov.id,
                'data': mov.data.isoformat(),
                'tipo': mov.get_tipo_display() if hasattr(mov, 'get_tipo_display') else mov.tipo,
                'tipo_codigo': mov.tipo,
                'quantidade': float(mov.quantidade),
                'valor_unitario': float(mov.valor_unitario),
                'valor_total': float(mov.valor_total),
                'documento': mov.documento or '',
                'operador': mov.operador or '',
                'observacoes': mov.observacoes or '',
                'is_entrada': is_entrada,
                'is_saida': not is_entrada
            }
            
            # Adicionar informações da nota fiscal se disponível
            if hasattr(mov, 'nota_fiscal') and mov.nota_fiscal:
                detalhe['nota_fiscal'] = {
                    'numero': mov.nota_fiscal.numero,
                    'tipo': mov.nota_fiscal.tipo,
                    'fornecedor': getattr(mov.nota_fiscal, 'fornecedor', ''),
                    'cliente': getattr(mov.nota_fiscal, 'cliente', '')
                }
            
            detalhes.append(detalhe)
        
        return detalhes
    
    def calcular_resumo(self, produtos, data_inicio, data_fim):
        """Calcula resumo geral das movimentações."""
        if not produtos:
            return self.resumo_vazio(data_inicio, data_fim)
        
        total_produtos = len(produtos)
        total_movimentacoes = sum(p.get('total_movimentacoes', 0) for p in produtos)
        valor_total_entradas = sum(p.get('valor_entrada', 0) for p in produtos)
        valor_total_saidas = sum(p.get('valor_saida', 0) for p in produtos)
        valor_total_saidas_preco_entrada = sum(p.get('valor_saida_preco_entrada', 0) for p in produtos)
        quantidade_total_entradas = sum(p.get('quantidade_entrada', 0) for p in produtos)
        quantidade_total_saidas = sum(p.get('quantidade_saida', 0) for p in produtos)
        produtos_com_entrada = sum(1 for p in produtos if p.get('tem_entrada_anterior', False))
        
        diferenca_total_precos = valor_total_saidas - valor_total_saidas_preco_entrada
        margem_total = 0
        if valor_total_saidas_preco_entrada > 0:
            margem_total = (diferenca_total_precos / valor_total_saidas_preco_entrada) * 100
        
        return {
            'periodo': f"{data_inicio.strftime('%Y-%m-%d')} a {data_fim.strftime('%Y-%m-%d')}",
            'total_produtos': total_produtos,
            'total_movimentacoes': total_movimentacoes,
            'valor_total_entradas': valor_total_entradas,
            'valor_total_saidas': valor_total_saidas,
            'valor_total_saidas_preco_entrada': valor_total_saidas_preco_entrada,
            'diferenca_total_precos': diferenca_total_precos,
            'margem_total': round(margem_total, 2),
            'saldo_periodo': valor_total_entradas - valor_total_saidas,
            'quantidade_total_entradas': quantidade_total_entradas,
            'quantidade_total_saidas': quantidade_total_saidas,
            'produtos_com_entrada_anterior': produtos_com_entrada,
            'produtos_sem_entrada_anterior': total_produtos - produtos_com_entrada
        }
    
    def validate_date(self, date_string):
        """Valida e converte string de data."""
        if not date_string:
            return None
        try:
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValueError:
            return None
    
    def resumo_vazio(self, data_inicio, data_fim):
        """Retorna resumo vazio quando não há dados."""
        return {
            'periodo': f"{data_inicio.strftime('%Y-%m-%d')} a {data_fim.strftime('%Y-%m-%d')}",
            'total_produtos': 0,
            'total_movimentacoes': 0,
            'valor_total_entradas': 0,
            'valor_total_saidas': 0,
            'valor_total_saidas_preco_entrada': 0,
            'diferenca_total_precos': 0,
            'margem_total': 0,
            'saldo_periodo': 0,
            'quantidade_total_entradas': 0,
            'quantidade_total_saidas': 0,
            'produtos_com_entrada_anterior': 0,
            'produtos_sem_entrada_anterior': 0
        }
```

### 8. URLs (urls.py)

```python
# urls.py
from django.urls import path
from .views import MovimentacoesPeriodoAPIView

urlpatterns = [
    path('api/estoque-controle/movimentacoes_periodo/', 
         MovimentacoesPeriodoAPIView.as_view(), 
         name='movimentacoes_periodo'),
]
```

### 9. Melhorias de Performance

#### **Índices Necessários:**
```sql
-- Índices para otimizar consultas
CREATE INDEX idx_movimentacoes_produto_data ON movimentacoes_estoque(produto_id, data);
CREATE INDEX idx_movimentacoes_tipo_data ON movimentacoes_estoque(tipo, data);
CREATE INDEX idx_movimentacoes_data_periodo ON movimentacoes_estoque(data, produto_id, tipo);
CREATE INDEX idx_movimentacoes_valor_unitario ON movimentacoes_estoque(valor_unitario) WHERE valor_unitario > 0;
```

#### **Cache Redis (opcional):**
```python
from django.core.cache import cache
import hashlib

def get_cache_key(data_inicio, data_fim, **kwargs):
    """Gera chave de cache baseada nos parâmetros."""
    params_str = f"{data_inicio}_{data_fim}_{kwargs}"
    return f"movimentacoes_periodo_{hashlib.md5(params_str.encode()).hexdigest()}"

# No método get da view:
cache_key = get_cache_key(data_inicio, data_fim, produto_id=produto_id, limite=limite)
cached_result = cache.get(cache_key)

if cached_result:
    return Response(cached_result)

# ... código normal ...

# Cache por 15 minutos
cache.set(cache_key, response_data, 900)
```

### 10. Testes Unitários

```python
# tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from datetime import date, datetime
from .models import Produto, MovimentacaoEstoque

class MovimentacoesPeriodoAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.produto = Produto.objects.create(
            nome="Produto Teste",
            referencia="TEST001"
        )
        
        # Criar movimentações de teste
        MovimentacaoEstoque.objects.create(
            produto=self.produto,
            tipo="ENT",
            quantidade=10,
            valor_unitario=100.00,
            valor_total=1000.00,
            data=date(2025, 1, 5),
            documento="NF001"
        )
        
        MovimentacaoEstoque.objects.create(
            produto=self.produto,
            tipo="SAI",
            quantidade=5,
            valor_unitario=150.00,
            valor_total=750.00,
            data=date(2025, 1, 10),
            documento="NF002"
        )
    
    def test_movimentacoes_periodo_basico(self):
        """Teste básico do endpoint."""
        url = reverse('movimentacoes_periodo')
        response = self.client.get(url, {
            'data_inicio': '2025-01-01',
            'data_fim': '2025-01-31'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('produtos_movimentados', data)
        self.assertIn('resumo', data)
        self.assertIn('parametros', data)
        
        produtos = data['produtos_movimentados']
        self.assertEqual(len(produtos), 1)
        
        produto = produtos[0]
        self.assertEqual(produto['produto_id'], self.produto.id)
        self.assertEqual(produto['quantidade_entrada'], 10)
        self.assertEqual(produto['quantidade_saida'], 5)
        self.assertEqual(produto['ultimo_preco_entrada'], 100.00)
        self.assertEqual(produto['valor_saida_preco_entrada'], 500.00)  # 5 * 100
        self.assertEqual(produto['diferenca_preco'], 250.00)  # 750 - 500
    
    def test_produto_sem_entrada_anterior(self):
        """Teste produto que só tem saída."""
        produto_novo = Produto.objects.create(
            nome="Produto Novo",
            referencia="NEW001"
        )
        
        MovimentacaoEstoque.objects.create(
            produto=produto_novo,
            tipo="SAI",
            quantidade=2,
            valor_unitario=200.00,
            valor_total=400.00,
            data=date(2025, 1, 15)
        )
        
        url = reverse('movimentacoes_periodo')
        response = self.client.get(url, {
            'data_inicio': '2025-01-01',
            'data_fim': '2025-01-31'
        })
        
        produtos = response.json()['produtos_movimentados']
        produto_novo_data = next(p for p in produtos if p['produto_id'] == produto_novo.id)
        
        self.assertEqual(produto_novo_data['ultimo_preco_entrada'], 0)
        self.assertEqual(produto_novo_data['valor_saida_preco_entrada'], 0)
        self.assertFalse(produto_novo_data['tem_entrada_anterior'])
    
    def test_incluir_detalhes(self):
        """Teste incluindo movimentações detalhadas."""
        url = reverse('movimentacoes_periodo')
        response = self.client.get(url, {
            'data_inicio': '2025-01-01',
            'data_fim': '2025-01-31',
            'incluir_detalhes': 'true'
        })
        
        produtos = response.json()['produtos_movimentados']
        produto = produtos[0]
        
        self.assertIn('movimentacoes_detalhadas', produto)
        detalhes = produto['movimentacoes_detalhadas']
        self.assertEqual(len(detalhes), 2)
        
        # Verificar entrada
        entrada = next(d for d in detalhes if d['is_entrada'])
        self.assertEqual(entrada['tipo_codigo'], 'ENT')
        self.assertEqual(entrada['quantidade'], 10)
        self.assertEqual(entrada['valor_unitario'], 100.00)
        
        # Verificar saída
        saida = next(d for d in detalhes if d['is_saida'])
        self.assertEqual(saida['tipo_codigo'], 'SAI')
        self.assertEqual(saida['quantidade'], 5)
        self.assertEqual(saida['valor_unitario'], 150.00)
    
    def test_validacao_parametros(self):
        """Teste validação de parâmetros obrigatórios."""
        url = reverse('movimentacoes_periodo')
        
        # Sem parâmetros
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        
        # Só data_inicio
        response = self.client.get(url, {'data_inicio': '2025-01-01'})
        self.assertEqual(response.status_code, 400)
        
        # Data inválida
        response = self.client.get(url, {
            'data_inicio': '2025-13-01',  # Mês inválido
            'data_fim': '2025-01-31'
        })
        self.assertEqual(response.status_code, 400)
```

### 11. Documentação da API

#### **Endpoint:** `GET /api/estoque-controle/movimentacoes_periodo/`

#### **Descrição:**
Retorna movimentações de estoque por período com cálculos de valor baseados no último preço de entrada.

#### **Parâmetros:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `data_inicio` | string (YYYY-MM-DD) | Sim | Data de início do período |
| `data_fim` | string (YYYY-MM-DD) | Sim | Data de fim do período |
| `incluir_detalhes` | boolean | Não | Incluir movimentações detalhadas (default: false) |
| `produto_id` | integer | Não | Filtrar por produto específico |
| `limite` | integer | Não | Limitar número de produtos retornados |

#### **Códigos de Resposta:**
- `200`: Sucesso
- `400`: Parâmetros inválidos
- `500`: Erro interno do servidor

#### **Exemplo de Uso:**
```bash
# Buscar movimentações de janeiro 2025 com detalhes
GET /api/estoque-controle/movimentacoes_periodo/?data_inicio=2025-01-01&data_fim=2025-01-31&incluir_detalhes=true

# Buscar apenas um produto
GET /api/estoque-controle/movimentacoes_periodo/?data_inicio=2025-01-01&data_fim=2025-01-31&produto_id=6440

# Limitar a 50 produtos
GET /api/estoque-controle/movimentacoes_periodo/?data_inicio=2025-01-01&data_fim=2025-01-31&limite=50
```

### 12. Cronograma de Implementação

#### **Fase 1 - Backend Básico (2-3 dias):**
- [ ] Implementar query principal
- [ ] Adicionar cálculo de último preço de entrada
- [ ] Criar campos derivados (valor_saida_preco_entrada, diferenca_preco)
- [ ] Testes básicos

#### **Fase 2 - Movimentações Detalhadas (1-2 dias):**
- [ ] Implementar parâmetro incluir_detalhes
- [ ] Estruturar resposta das movimentações detalhadas
- [ ] Adicionar informações de nota fiscal

#### **Fase 3 - Otimizações (1 dia):**
- [ ] Adicionar índices de performance
- [ ] Implementar cache (opcional)
- [ ] Validações e tratamento de erros

#### **Fase 4 - Testes e Documentação (1 dia):**
- [ ] Testes unitários completos
- [ ] Documentação da API
- [ ] Validação com dados reais

### 13. Checklist de Validação

#### **Funcionalidades Obrigatórias:**
- [ ] Retorna último preço de entrada mesmo fora do período
- [ ] Calcula valor_saida_preco_entrada corretamente
- [ ] Identifica produtos sem entrada anterior
- [ ] Movimentações detalhadas funcionando
- [ ] Resumo com todos os campos obrigatórios
- [ ] Performance adequada (< 2 segundos para 1000 produtos)

#### **Testes de Validação:**
- [ ] Produto com entrada no período
- [ ] Produto com entrada anterior ao período
- [ ] Produto sem entrada anterior (preço zero)
- [ ] Produto só com saídas
- [ ] Cálculo correto de margens
- [ ] Período sem movimentações
- [ ] Grandes volumes de dados

### 14. Notas Importantes

1. **Tipos de Movimentação:** Confirmar quais códigos são usados para entrada/saída no sistema
2. **Moeda:** Todos os valores devem manter precisão decimal adequada
3. **Timezone:** Considerar fuso horário nas consultas de data
4. **Backup:** Testar em ambiente de desenvolvimento primeiro
5. **Logs:** Adicionar logs para debugar performance

### 15. Contato e Suporte

Para dúvidas sobre implementação:
- Revisar este documento
- Consultar exemplos de código fornecidos
- Testar incrementalmente cada funcionalidade

---

**Documento gerado em:** 06/09/2025
**Versão:** 1.0
**Última atualização:** 06/09/2025
