# 📊 ENDPOINTS DE ESTOQUE POR DATA ESPECÍFICA

## 🎯 **ENDPOINT PRINCIPAL RECOMENDADO**

### `/api/relatorio-valor-estoque/`

**Método:** `GET`  
**Parâmetro:** `?data=YYYY-MM-DD`  
**Descrição:** Calcula o estoque histórico em uma data específica baseado nas movimentações

#### ✅ **Como usar:**
```bash
GET /api/relatorio-valor-estoque/?data=2025-09-01
```

#### 📄 **Resposta:**
```json
{
  "data_posicao": "2025-09-01",
  "valor_total_estoque": "1039513.09",
  "total_produtos_em_estoque": 481,
  "detalhes_por_produto": [
    {
      "produto_id": 4032,
      "produto_descricao": "TINTA PRETA/RC JP7 750",
      "quantidade_em_estoque": "4261.000",
      "custo_unitario": "21.79",
      "valor_total_produto": "92851.02"
    }
  ]
}
```

#### 🔧 **Características:**
- ✅ Calcula estoque baseado nas movimentações até a data informada
- ✅ Considera entradas (ENT) como positivas e saídas (SAI) como negativas  
- ✅ Retorna apenas produtos com saldo positivo
- ✅ Inclui valor total e detalhes por produto
- ✅ Se data não informada, usa data atual

---

## 🔄 **ENDPOINTS COMPLEMENTARES**

### 1. `/api/saldos_estoque/`

**Método:** `GET`  
**Descrição:** Saldos atuais cadastrados na tabela (tempo real)

```bash
# Apenas saldos positivos
GET /api/saldos_estoque/?quantidade__gt=0

# Por produto específico
GET /api/saldos_estoque/?produto_id__codigo=4032
```

### 2. `/api/movimentacoes_estoque/`

**Método:** `GET`  
**Descrição:** Movimentações históricas com filtros de data

```bash
# Movimentações de um dia específico
GET /api/movimentacoes_estoque/?data_movimentacao__date=2025-09-01

# Movimentações em um período
GET /api/movimentacoes_estoque/?data_movimentacao__gte=2025-08-01&data_movimentacao__lte=2025-09-01

# Por produto
GET /api/movimentacoes_estoque/?produto__codigo=4032
```

### 3. `/api/produtos/`

**Método:** `GET`  
**Descrição:** Lista de produtos cadastrados

```bash
GET /api/produtos/?disponivel_locacao=true
```

---

## 📈 **EXEMPLOS PRÁTICOS**

### 💼 **Cenário 1: Estoque hoje**
```bash
GET /api/relatorio-valor-estoque/?data=2025-09-02
```

### 💼 **Cenário 2: Estoque no final de agosto**
```bash
GET /api/relatorio-valor-estoque/?data=2025-08-31
```

### 💼 **Cenário 3: Estoque no início do ano**
```bash
GET /api/relatorio-valor-estoque/?data=2025-01-01
```

### 💼 **Cenário 4: Movimentações de ontem**
```bash
GET /api/movimentacoes_estoque/?data_movimentacao__date=2025-09-01
```

---

## 🛠️ **IMPLEMENTAÇÃO TÉCNICA**

### Como o endpoint calcula o estoque por data:

1. **Busca movimentações** até a data especificada:
   ```sql
   WHERE data_movimentacao__date <= '2025-09-01'
   ```

2. **Agrupa por produto** e soma as quantidades:
   - Entradas (tipo='E'): `+quantidade`
   - Saídas (tipo='S'): `-quantidade`

3. **Filtra saldos positivos** e calcula valores:
   ```python
   saldo_final = Sum(Case(
       When(tipo_movimentacao__tipo='E', then=F('quantidade')),
       When(tipo_movimentacao__tipo='S', then=-F('quantidade')),
       default=0
   ))
   ```

4. **Retorna resultado** com detalhes por produto

---

## 🎯 **CASOS DE USO**

| Necessidade | Endpoint Recomendado | Exemplo |
|-------------|---------------------|---------|
| **Estoque em data específica** | `/relatorio-valor-estoque/` | `?data=2025-08-31` |
| **Estoque atual** | `/saldos_estoque/` | `?quantidade__gt=0` |
| **Movimentações do dia** | `/movimentacoes_estoque/` | `?data_movimentacao__date=hoje` |
| **Histórico de produto** | `/movimentacoes_estoque/` | `?produto__codigo=4032` |
| **Período específico** | `/movimentacoes_estoque/` | `?data_movimentacao__gte=X&lte=Y` |

---

## ⚡ **PERFORMANCE E DICAS**

### 🚀 **Otimizações:**
- Use datas específicas para evitar consultas muito amplas
- O endpoint `/relatorio-valor-estoque/` é otimizado com agregações SQL
- Para consultas frequentes, considere cache

### 💡 **Dicas:**
- **Data obrigatória:** Sempre informe a data no formato `YYYY-MM-DD`
- **Timezone:** O sistema considera o fuso horário configurado no Django
- **Saldos negativos:** São filtrados automaticamente
- **Produtos sem custo:** Aparecem com valor zero no relatório

---

## 🔗 **RESUMO RÁPIDO**

```bash
# 🎯 PRINCIPAL: Estoque em data específica
GET /api/relatorio-valor-estoque/?data=2025-09-01

# 🔄 ATUAL: Saldos atuais
GET /api/saldos_estoque/?quantidade__gt=0

# 📊 MOVIMENTAÇÕES: Por data
GET /api/movimentacoes_estoque/?data_movimentacao__date=2025-09-01
```

**💡 Use o primeiro endpoint para consultas de estoque histórico por data específica!**
