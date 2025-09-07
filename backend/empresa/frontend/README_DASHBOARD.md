# Dashboard de Fluxo de Caixa Realizado

## 📊 Visão Geral

Este é um dashboard moderno em React + TypeScript para visualizar dados de fluxo de caixa realizado da sua empresa. O dashboard se conecta aos endpoints Django REST que foram criados anteriormente.

## 🚀 Como Usar

### 1. Iniciar o Frontend
```bash
cd frontend
npm run dev
```

O dashboard estará disponível em: `http://localhost:5173/`

### 2. Funcionalidades Disponíveis

#### 📈 Dashboard Principal
- **Métricas Principais**: Total de receitas e despesas realizadas
- **Gráficos Interativos**: Visualização temporal do fluxo de caixa
- **Filtros Avançados**: Por período, categoria e status
- **Resumo Executivo**: Insights automáticos dos dados

#### 💰 Análises Incluídas
- Fluxo de caixa realizado vs projetado
- Contas em atraso e vencimento próximo
- Análise por categoria de despesas/receitas
- Tendências mensais e anuais

### 3. Endpoints Integrados

O dashboard consome os seguintes endpoints do backend:

#### FluxoCaixaRealizado
- `GET /api/fluxo-caixa/realizado/` - Dados principais
- `GET /api/fluxo-caixa/realizado/resumo/` - Resumo executivo
- `GET /api/fluxo-caixa/realizado/detalhes/` - Detalhes por período
- `GET /api/fluxo-caixa/realizado/categorias/` - Análise por categoria

#### AnaliseFluxoCaixa
- `GET /api/analise-fluxo-caixa/comparativo/` - Realizado vs Projetado
- `GET /api/analise-fluxo-caixa/atraso/` - Contas em atraso
- `GET /api/analise-fluxo-caixa/vencimento-proximo/` - Vencimentos próximos

## 🛠️ Tecnologias Utilizadas

- **React 18** - Framework principal
- **TypeScript** - Tipagem estática
- **Vite** - Bundler e servidor de desenvolvimento
- **Tailwind CSS** - Estilização utilitária
- **Lucide React** - Ícones modernos
- **Axios** - Cliente HTTP para APIs

## 🎨 Características do Design

- **Interface Moderna**: Design clean com paleta de cores profissional
- **Responsivo**: Funciona em desktop, tablet e mobile
- **Acessível**: Seguindo padrões de acessibilidade web
- **Performance**: Carregamento rápido e interações fluidas

## 📱 Layout Responsivo

O dashboard se adapta automaticamente a diferentes tamanhos de tela:

- **Desktop**: Layout com sidebar e múltiplas colunas
- **Tablet**: Layout adaptado com elementos empilhados
- **Mobile**: Interface otimizada para toque

## 🔧 Configuração de API

O dashboard está configurado para se conectar ao backend Django em:
`http://localhost:8000/api/`

Para alterar a URL base da API, edite o arquivo:
`src/services/api.ts`

## 📊 Dados Mockados

Durante o desenvolvimento, o dashboard inclui dados mockados que simulam:
- 12 meses de dados financeiros
- Múltiplas categorias de receitas e despesas
- Status variados de contas (pagas, pendentes, atrasadas)
- Projeções vs realizações

## 🚀 Próximos Passos

1. **Conectar ao Backend Real**: Substituir dados mockados pelos endpoints Django
2. **Autenticação**: Implementar login/logout de usuários
3. **Filtros Avançados**: Adicionar mais opções de filtro
4. **Exportação**: Funcionalidade para exportar relatórios em PDF/Excel
5. **Notificações**: Alertas para contas vencendo ou em atraso

## 🤝 Suporte

Para dúvidas ou problemas:
1. Verifique se o backend Django está rodando
2. Confirme se os endpoints estão respondendo corretamente
3. Abra o console do navegador para verificar erros JavaScript

---

**Desenvolvido com ❤️ usando React + TypeScript + Tailwind CSS**
