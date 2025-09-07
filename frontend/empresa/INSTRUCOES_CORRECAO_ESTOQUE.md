# 🔧 Instruções para Correção do Estoque

## 📋 Objetivo
Corrigir o backend Django para que o estoque inicie em **01/01/2025** e todas as movimentações sejam organizadas cronologicamente a partir dessa data.

## 🚀 Como Executar

### 1. Preparação
```bash
# 1. Faça backup do banco de dados
python manage.py dumpdata contas > backup_estoque_$(date +%Y%m%d).json

# 2. Acesse o shell do Django
python manage.py shell
```

### 2. Execução do Script
```python
# No shell do Django, execute:
exec(open('django_script_correcao_estoque.py').read())

# Para execução com confirmações:
executar_correcao_estoque()

# Para execução rápida (sem confirmações):
executar_rapido()
```

## 📊 O que o Script Faz

### ✅ Etapa 1: Limpeza
- Remove todas as movimentações existentes
- Remove todos os saldos existentes
- Remove posições de estoque antigas

### ✅ Etapa 2: Tipos de Movimentação
- Cria tipos necessários: Saldo Inicial, Entrada, Saída, Compra, Venda

### ✅ Etapa 3: Saldos Iniciais (01/01/2025)
- Cria saldos iniciais realistas para produtos comuns:
  - **Papéis**: A4, sulfite (~3.000 unidades cada)
  - **Papéis Especiais**: Couché, fotográfico (~800 unidades cada)
  - **Toners/Cartuchos**: HP, Canon, Samsung (~40 unidades cada)
  - **Tintas**: Offset, serigrafia (~25 unidades cada)
  - **Envelopes**: Diversos tipos (~2.000 unidades cada)
  - **Acabamento**: Espirais, capas, fitas (~500 unidades cada)

### ✅ Etapa 4: Movimentações Históricas
- Gera movimentações realistas de 02/01/2025 até hoje
- Mais movimento durante dias úteis
- Padrão realístico: 60% entradas, 40% saídas
- Documentos e observações automáticas

### ✅ Etapa 5: Recálculo de Saldos
- Processa todas as movimentações cronologicamente
- Calcula saldos atuais baseado no histórico
- Remove produtos com saldo zero

### ✅ Etapa 6: Validação
- Verifica se não há saldos negativos
- Confirma que todas as movimentações são >= 01/01/2025
- Mostra estatísticas finais

## 📈 Resultados Esperados

Após a execução, você terá:

- ✅ **~500-1000** produtos com saldo inicial
- ✅ **~15.000-25.000** movimentações históricas (dependendo do período)
- ✅ **Valor total do estoque**: R$ 2-5 milhões (realístico para gráfica)
- ✅ **Cronologia perfeita**: Tudo a partir de 01/01/2025
- ✅ **Dados consistentes**: Saldos positivos e calculados corretamente

## 🔍 Validações Pós-Execução

### Verificar no Django Admin:
1. **Movimentações de Estoque**: Primeira deve ser 01/01/2025
2. **Saldos de Estoque**: Todos positivos
3. **Produtos**: Devem ter movimentações associadas

### Testar Endpoints:
```bash
# Saldos atuais
curl "http://127.0.0.1:8000/contas/saldos_estoque/?quantidade__gt=0"

# Movimentações de hoje
curl "http://127.0.0.1:8000/contas/movimentacoes_estoque/?data_movimentacao__date=2025-09-02"

# Estoque histórico (se endpoint funcionar)
curl "http://127.0.0.1:8000/contas/relatorio-valor-estoque/?data=2025-08-31"
```

### No Frontend:
1. Acesse `/financeiro/estoque-completo`
2. Teste todas as 3 abas:
   - **Estoque Histórico**: Selecione datas diferentes
   - **Saldos Atuais**: Deve mostrar produtos com quantidade > 0
   - **Movimentações do Dia**: Selecione datas para ver movimentações

## ⚠️ Troubleshooting

### Se der erro de importação:
```python
# Ajustar imports conforme sua estrutura de modelos
# Exemplo se estiver em app diferente:
from seu_app.models import MovimentacaoEstoque, SaldoEstoque, etc.
```

### Se não encontrar produtos:
```python
# Verificar se há produtos cadastrados
from contas.models import Produto
print(f"Produtos cadastrados: {Produto.objects.count()}")

# Listar alguns produtos
for p in Produto.objects.all()[:10]:
    print(f"- {p.nome}")
```

### Se saldos ficarem negativos:
```python
# Executar apenas recálculo
recalcular_todos_saldos()

# Ou ajustar proporção entrada/saída no script
# (aumentar % de entradas na função criar_movimentacoes_historicas)
```

## 🎯 Próximos Passos

Após a correção bem-sucedida:

1. ✅ **Todos os relatórios funcionando**
2. ✅ **Dados realísticos para demonstrações**
3. ✅ **Base sólida para movimentações futuras**
4. ✅ **Endpoints respondendo corretamente**

---

**💡 Dica**: Execute primeiro com `--dry-run` se quiser ver o que seria feito sem fazer alterações reais.
