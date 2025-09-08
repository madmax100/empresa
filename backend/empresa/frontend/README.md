# Dashboard Financeiro - C3M Cópias

Sistema de dashboard financeiro desenvolvido em React + TypeScript com Vite para análise de contratos de locação e resultados do período.

## 🚀 Funcionalidades

### 📊 Dashboard de Contratos
- **Análise agrupada por cliente** com métricas financeiras
- **Filtros de período** com botões preset (Mês Atual, Último Mês, Ano Atual)
- **Visualizações interativas** com gráficos e tabelas expansíveis
- **Exportação para CSV** dos dados dos contratos
- **Métricas detalhadas**: receita total, valor médio, margem de lucro

### 📈 Dashboard de Resultados do Período
- **Variação de estoque** (valor anterior vs atual)
- **Lucro operacional** (diferença entre saída e entrada)
- **Contratos recebidos** (valores de locação recebidos)
- **Resultado líquido consolidado** com margens
- **Detalhamento completo** de cada componente
- **Exportação de relatórios** em CSV

### 🎨 Design System
- **Shadcn UI**: Componentes modernos e acessíveis
- **Tailwind CSS**: Estilização utilitária responsiva
- **Lucide React**: Ícones consistentes e elegantes
- **Cards coloridos**: Bordas identificadoras por categoria
- **Layout responsivo**: Mobile-first design

## 🛠️ Tecnologias

- **React 18** + **TypeScript**
- **Vite** (build tool e dev server)
- **Shadcn UI** (componentes)
- **Tailwind CSS** (estilização)
- **Recharts** (visualizações)
- **Lucide React** (ícones)

## 📁 Estrutura do Projeto

```
src/
├── components/
│   ├── dashboard/              # Dashboards principais
│   │   ├── ResultadosPeriodoDashboard.tsx
│   │   └── ...
│   ├── financial/             # Componentes financeiros
│   │   └── contracts/
│   │       └── ContractsDashboardGrouped.tsx
│   ├── ui/                    # Componentes base (Shadcn)
│   └── common/                # Componentes reutilizáveis
├── pages/                     # Páginas da aplicação
│   ├── ContratosPage.tsx
│   └── ResultadosPage.tsx
├── services/                  # Services para APIs
│   ├── contratosService.ts
│   └── resultados-service.ts
├── hooks/                     # Hooks customizados
│   ├── useContratosFixed.ts
│   └── useResultados.ts
└── types/                     # Definições TypeScript
    ├── contratos.ts
    └── fluxo-caixa.ts
```

## 🚀 Como Executar

1. **Instalar dependências**:
```bash
npm install
```

2. **Executar em desenvolvimento**:
```bash
npm run dev
```

3. **Build para produção**:
```bash
npm run build
```

4. **Preview da build**:
```bash
npm run preview
```

## 📊 APIs Backend

### Contratos de Locação
```bash
GET /api/contratos_locacao/     # Lista contratos
GET /api/contratos_locacao/{id}/ # Detalhes do contrato
```

### Resultados do Período
```bash
GET /api/estoque/variacao/      # Variação de estoque
GET /api/operacoes/lucro/       # Lucro operacional
GET /api/contratos_locacao/recebimentos/ # Recebimentos
GET /api/resultados/historico/  # Histórico de resultados
```

**Nota**: Quando as APIs não estão disponíveis, o sistema utiliza dados mockados para demonstração.

## 🔧 Configurações

### ESLint + TypeScript
Configuração com regras type-aware para produção:

```js
export default tseslint.config([
  {
    files: ['**/*.{ts,tsx}'],
    extends: [...tseslint.configs.recommendedTypeChecked],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
