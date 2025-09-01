# Proposta de Endpoint Backend para Suprimentos por Contrato

## Endpoint Proposto

```
GET /contas/contratos_locacao/suprimentos/
```

### Parâmetros Query
- `data_inicial`: Data inicial (YYYY-MM-DD)
- `data_final`: Data final (YYYY-MM-DD)
- `contrato_id`: ID específico do contrato (opcional)
- `cliente_id`: ID específico do cliente (opcional)

### Resposta JSON
```json
{
  "periodo": {
    "data_inicial": "2024-01-01",
    "data_final": "2024-12-31"
  },
  "resumo": {
    "total_contratos": 150,
    "total_suprimentos": 45780.50,
    "total_notas": 342
  },
  "resultados": [
    {
      "contrato_id": 1529,
      "contrato_numero": "C1529",
      "cliente": {
        "id": 6218,
        "nome": "LOCKTON CE CONS."
      },
      "suprimentos": {
        "total_valor": 1250.75,
        "quantidade_notas": 8,
        "notas_amostra": [
          {
            "id": 801,
            "numero_nota": "41440",
            "data": "2024-06-10",
            "operacao": "SIMPLES REMESSA",
            "cfop": "5949",
            "valor_total_nota": 116.36,
            "obs": "Cobertura de contrato..."
          }
        ]
      }
    }
  ]
}
```

## Implementação Backend (Django)

### View
```python
from django.db.models import Q, Sum, Count
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def suprimentos_por_contrato(request):
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')
    contrato_id = request.GET.get('contrato_id')
    
    # Query otimizada para detectar "simples remessa"
    filtro_remessa = Q(
        Q(operacao__icontains='SIMPLES REMESSA') |
        Q(cfop__regex=r'^[56]9\d{2}$') |
        Q(obs__icontains='suprimento') |
        Q(obs__icontains='toner') |
        Q(finalidade__icontains='remessa')
    )
    
    # Base query
    notas_query = NotaFiscalVenda.objects.filter(
        filtro_remessa,
        data__range=[data_inicial, data_final]
    )
    
    if contrato_id:
        notas_query = notas_query.filter(contrato=contrato_id)
    
    # Agregação por contrato
    resultados = notas_query.values(
        'contrato',
        'cliente__id',
        'cliente__nome'
    ).annotate(
        total_valor=Sum('valor_total_nota'),
        quantidade_notas=Count('id')
    ).order_by('contrato')
    
    # Buscar amostras (máximo 5 por contrato)
    for resultado in resultados:
        amostras = notas_query.filter(
            contrato=resultado['contrato']
        ).values(
            'id', 'numero_nota', 'data', 'operacao', 
            'cfop', 'valor_total_nota', 'obs'
        )[:5]
        resultado['notas_amostra'] = list(amostras)
    
    return Response({
        'periodo': {
            'data_inicial': data_inicial,
            'data_final': data_final
        },
        'resumo': {
            'total_contratos': len(resultados),
            'total_suprimentos': sum(r['total_valor'] or 0 for r in resultados),
            'total_notas': sum(r['quantidade_notas'] or 0 for r in resultados)
        },
        'resultados': resultados
    })
```

### URL
```python
# urls.py
urlpatterns = [
    path('contratos_locacao/suprimentos/', suprimentos_por_contrato),
]
```

## Frontend Simplificado

Com o endpoint dedicado, o frontend fica muito mais simples:

```typescript
// Novo serviço
const getSuprimentosPorContrato = async (filtros: {
  data_inicial: string;
  data_final: string;
  contrato_id?: string;
}) => {
  const params = new URLSearchParams(filtros);
  return await api.get(`/contratos_locacao/suprimentos/?${params}`);
};

// No componente
const loadSuprimentos = async () => {
  const response = await getSuprimentosPorContrato({
    data_inicial: toYmd(dateRange.from),
    data_final: toYmd(dateRange.to)
  });
  
  // Mapear diretamente para os contratos
  const suprimentosMap = new Map();
  response.data.resultados.forEach(r => {
    suprimentosMap.set(r.contrato_numero, r.suprimentos.total_valor);
  });
  
  // Aplicar aos contratos processados
  processedData = processedData.map(contrato => ({
    ...contrato,
    suprimentos: suprimentosMap.get(contrato.contratoNumero) || 0
  }));
};
```

## Vantagens da Abordagem Backend

1. **Performance**: 1 requisição vs 50+ requisições
2. **Precisão**: Lógica centralizada, sem inconsistências
3. **Cache**: Possibilidade de implementar cache no backend
4. **Índices**: Otimizações de banco de dados específicas
5. **Manutenibilidade**: Regras de negócio em um lugar só
6. **Escalabilidade**: Suporta milhares de contratos sem degradação

## Recomendação

Implemente o endpoint `/contratos_locacao/suprimentos/` no backend Django e substitua toda a lógica atual do frontend por uma única chamada otimizada.
