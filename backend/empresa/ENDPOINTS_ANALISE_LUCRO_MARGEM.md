# 💹 Endpoints de Análise de Lucro e Margem

## 🎯 **RESPOSTA DIRETA**

Os endpoints que mostram o **lucro obtido pelas notas fiscais de venda diminuído do valor dos produtos com preço de entrada** são:

### **📊 1. Endpoint Principal - Movimentações de Estoque**
```
GET /contas/estoque-controle/movimentacoes_periodo/
```

### **📈 2. Endpoint Alternativo - Relatório de Faturamento** 
```
GET /contas/relatorios/faturamento/
```

---

## 💰 **ENDPOINT PRINCIPAL: MOVIMENTAÇÕES DE ESTOQUE**

### **📍 URL:**
```
GET /contas/estoque-controle/movimentacoes_periodo/
```

### **🔄 Funcionalidade:**
Calcula o **lucro bruto** das vendas usando o último preço de entrada dos produtos como custo.

### **📋 Parâmetros:**
| Parâmetro | Obrigatório | Formato | Descrição |
|-----------|-------------|---------|-----------|
| `data_inicio` | ✅ **SIM** | YYYY-MM-DD | Data inicial |
| `data_fim` | ✅ **SIM** | YYYY-MM-DD | Data final |
| `produto_id` | ❌ Não | number | Filtrar produto específico |
| `limite` | ❌ Não | number | Limitar resultados |

### **📤 Exemplo de Requisição:**
```bash
GET /contas/estoque-controle/movimentacoes_periodo/?data_inicio=2024-01-01&data_fim=2024-12-31
```

### **📥 Resposta com Cálculo de Lucro:**
```json
{
    "produtos_movimentados": [
        {
            "produto_id": 5013,
            "nome": "MULTIFUNCIONAL COPIADORA DIGITAL...",
            "quantidade_saida": 13.0,
            "valor_saida": 68409.9,
            "ultimo_preco_entrada": 3938.18,
            "valor_saida_preco_entrada": 51196.34,
            "diferenca_preco": 17213.56,
            "margem_percentual": 33.6
        }
    ],
    "resumo": {
        "total_produtos": 299,
        "valor_total_saidas": 909212.3,
        "valor_total_saidas_preco_entrada": 719628.57,
        "margem_total": 26.34,
        "lucro_bruto": 189583.73
    }
}
```

---

## 📊 **DADOS REAIS DO SISTEMA (2024)**

### **💹 Resumo Geral:**
- **💰 Faturamento Total:** R$ 909.212,30
- **🛒 Custo dos Produtos:** R$ 719.628,57
- **💹 LUCRO BRUTO:** R$ 189.583,73
- **📈 Margem de Lucro:** 26,34%
- **📦 Produtos Analisados:** 299

### **🏆 Exemplos de Produtos:**

#### **📈 Alto Lucro:**
- **SISTEMA MULTIFUNCIONAL:** 73,3% de margem
- **MULTIFUNCIONAL COPIADORA:** 33,6% de margem

#### **📉 Prejuízo:**
- **SISTEMA MONOCROMATICO:** -26,3% de margem (prejuízo)

---

## 🧮 **COMO O CÁLCULO É FEITO**

### **📝 Fórmula do Lucro:**
```
LUCRO BRUTO = Valor de Venda - (Quantidade × Último Preço de Entrada)
```

### **📊 Fórmula da Margem:**
```
MARGEM % = (Lucro Bruto ÷ Valor de Venda) × 100
```

### **🔍 Processo Detalhado:**

1. **📦 Identifica produtos vendidos** no período
2. **🛒 Busca último preço de entrada** de cada produto
3. **💰 Calcula valor de venda** (quantidade × preço de venda)
4. **🧮 Calcula custo** (quantidade × último preço de entrada)
5. **💹 Calcula lucro** (valor de venda - custo)
6. **📈 Calcula margem percentual**

---

## 📈 **ENDPOINT ALTERNATIVO: RELATÓRIO DE FATURAMENTO**

### **📍 URL:**
```
GET /contas/relatorios/faturamento/
```

### **🔄 Funcionalidade:**
Análise consolidada de faturamento com cálculo de margem bruta das vendas.

### **📊 Foco:**
- **Notas fiscais de saída** (vendas)
- **Cálculo de margem bruta** usando preços de entrada
- **Comparação com compras e serviços**

### **📥 Estrutura da Resposta:**
```json
{
    "resumo_por_tipo": [
        {
            "tipo": "Vendas (NF Saída)",
            "quantidade_notas": 150,
            "valor_total": 500000.0,
            "valor_preco_entrada": 380000.0,
            "margem_bruta": 120000.0,
            "detalhes": {
                "itens_calculados": 1250,
                "produtos_sem_preco_entrada": 25
            }
        }
    ]
}
```

---

## 🎯 **CASOS DE USO PRÁTICOS**

### **💼 1. Análise Anual de Lucratividade**
```bash
GET /contas/estoque-controle/movimentacoes_periodo/?data_inicio=2024-01-01&data_fim=2024-12-31
```
**Para:** Ver lucro total do ano e margem por produto

### **📅 2. Controle Mensal**
```bash
GET /contas/estoque-controle/movimentacoes_periodo/?data_inicio=2024-12-01&data_fim=2024-12-31
```
**Para:** Acompanhar performance do mês

### **🔍 3. Análise de Produto Específico**
```bash
GET /contas/estoque-controle/movimentacoes_periodo/?data_inicio=2024-01-01&data_fim=2024-12-31&produto_id=5013
```
**Para:** Ver lucro detalhado de um produto

### **📊 4. Top Produtos Mais Lucrativos**
```bash
GET /contas/estoque-controle/movimentacoes_periodo/?data_inicio=2024-01-01&data_fim=2024-12-31&limite=10
```
**Para:** Ranking dos produtos mais vendidos

---

## ⚙️ **IMPLEMENTAÇÃO TÉCNICA**

### **🔧 Método Principal:**
```python
def _obter_ultimo_preco_entrada(self, produto_id, data_limite):
    """Busca o último preço de entrada do produto"""
    # Busca a última movimentação de entrada do produto
    # Retorna preço unitário e data da movimentação
```

```python
def _calcular_valores_preco_entrada(self, movimentacoes_saida):
    """Calcula valores usando preços de entrada"""
    # Para cada saída:
    # 1. Busca último preço de entrada
    # 2. Calcula: quantidade × preço_entrada
    # 3. Calcula diferença: valor_venda - custo_entrada
```

### **📊 Campos Retornados:**
- `valor_saida` - Valor total da venda
- `ultimo_preco_entrada` - Último custo unitário
- `valor_saida_preco_entrada` - Custo total calculado
- `diferenca_preco` - **LUCRO BRUTO**
- `margem_total` - **MARGEM PERCENTUAL**

---

## 🎉 **CONCLUSÃO**

✅ **Endpoint funcionando:** `/contas/estoque-controle/movimentacoes_periodo/`  
✅ **Cálculo automático** de lucro usando preços de entrada  
✅ **Dados reais:** R$ 189.583,73 de lucro em 2024  
✅ **Análise por produto** com margem individual  
✅ **Margem geral:** 26,34% no período analisado  

**Status:** ✅ **IMPLEMENTADO E FUNCIONANDO** - Calcula exatamente o lucro das vendas diminuído dos custos com preços de entrada!
