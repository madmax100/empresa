# 📦 GUIA: ONDE VERIFICAR O ESTOQUE ATUAL

## 📋 Resumo do Sistema de Estoque

O sistema de estoque está implementado no Django com as seguintes tabelas principais:

### 🏗️ Estrutura de Tabelas

1. **`SaldosEstoque`** - Contém os saldos atuais de cada produto
   - `produto_id` - Referência ao produto
   - `quantidade` - Quantidade em estoque
   - `custo_medio` - Custo médio do produto
   - `ultima_movimentacao` - Data da última movimentação

2. **`MovimentacoesEstoque`** - Registra todas as movimentações
   - `data_movimentacao` - Data/hora da movimentação
   - `tipo_movimentacao` - ENT (Entrada) ou SAI (Saída)
   - `produto` - Produto movimentado
   - `quantidade` - Quantidade movimentada
   - `custo_unitario` - Custo unitário

3. **`TiposMovimentacaoEstoque`** - Tipos de movimentação
   - ENT - Entrada de Estoque
   - SAI - Saída de Estoque

## 🔍 Como Verificar o Estoque

### 1. **Através do Script de Consulta**
```bash
cd empresa
python scripts/consulta_estoque.py
```

**O que mostra:**
- ✅ Total de produtos cadastrados
- ✅ Produtos com estoque positivo
- ✅ Valor total do estoque
- ✅ Saldos detalhados por produto
- ✅ Produtos sem estoque
- ✅ Movimentações recentes
- ✅ Alertas de estoque (baixo, parado, sem custo)

### 2. **Diretamente no Django Admin**
- Acesse: `/admin/contas/saldosestoque/`
- Filtre por produtos com quantidade > 0

### 3. **Através da API REST**
- Endpoint: `/api/saldos-estoque/`
- Filtros disponíveis:
  - `?quantidade__gt=0` - Apenas saldos positivos
  - `?produto__codigo=XXX` - Por código do produto

### 4. **Consultas SQL Diretas**
```sql
-- Produtos com estoque
SELECT p.codigo, p.nome, s.quantidade, s.custo_medio
FROM produtos p
INNER JOIN saldos_estoque s ON p.id = s.produto_id_id
WHERE s.quantidade > 0
ORDER BY s.quantidade DESC;

-- Valor total do estoque
SELECT SUM(s.quantidade * s.custo_medio) as valor_total_estoque
FROM saldos_estoque s
WHERE s.custo_medio IS NOT NULL;
```

## 📊 Status Atual do Estoque

**Dados atualizados em: 02/09/2025**

- 📦 **Total de produtos cadastrados:** 5.496
- ✅ **Produtos com estoque positivo:** 481
- 💰 **Valor total estimado:** R$ 1.039.513,09
- 📈 **Última movimentação:** 02/09/2025

### 🏆 Produtos com Maior Estoque

| Código | Nome | Quantidade | Valor Unit. | Valor Total |
|--------|------|------------|-------------|-------------|
| 4032 | TINTA PRETA/RC JP7 750 | 4.261 | R$ 21,79 | R$ 92.851,02 |
| 4094 | GARRAFA TONER PRETO/RC AF | 1.170 | R$ 33,35 | R$ 39.016,11 |
| 3998 | MASTER TERMICO A4 RC JP | 828 | R$ 80,54 | R$ 66.691,18 |

## ⚠️ Alertas Identificados

- 🔸 **358 produtos** com estoque baixo (≤5 unidades)
- ⚠️ **478 produtos** sem movimentação há mais de 90 dias
- 💰 **8 produtos** sem custo médio definido

## 🔧 Manutenção do Estoque

### Recalcular Saldos (se necessário)
```bash
cd empresa
python scripts/recalcular_saldos.py
```

**Quando usar:**
- Após migração de dados
- Em caso de inconsistências
- Para sincronizar movimentações com saldos

### Verificar Integridade
- Os saldos são calculados automaticamente baseados nas movimentações
- Entradas (ENT) somam ao estoque
- Saídas (SAI) subtraem do estoque

## 📱 Integração com o Sistema

### Views/Endpoints Disponíveis
- `MovimentacoesEstoqueViewSet` - CRUD de movimentações
- `SaldosEstoqueViewSet` - Consulta de saldos
- `VendasEstoqueMixin` - Análises integradas

### Relatórios Disponíveis
- Análise de rentabilidade
- Giro de estoque
- Produtos em estoque baixo
- Produtos parados

---

🎯 **Dica:** Use o script `consulta_estoque.py` para verificações rápidas e completas do estoque atual!
