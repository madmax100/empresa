import "./styles.css";

const sections = [
  {
    title: "Estoque",
    description: "Monitoramento de saldo, inventário e movimentações.",
    badge: "API /api/estoque",
    items: [
      "Resumo de estoque",
      "Cadastro de produtos",
      "Movimentações por período"
    ]
  },
  {
    title: "Contas",
    description: "Acompanhamento financeiro de contas a pagar e receber.",
    badge: "API /api/contas",
    items: [
      "Resumo de contas a pagar",
      "Resumo de contas a receber",
      "Fluxo de caixa realizado"
    ]
  },
  {
    title: "Faturamento",
    description: "Indicadores de receita e contratos com cálculo proporcional.",
    badge: "API /api/faturamento",
    items: [
      "Faturamento bruto e líquido",
      "Contratos ativos",
      "Custos fixos e variáveis"
    ]
  },
  {
    title: "Locação e Suprimentos",
    description: "Gestão de contratos de locação e consumo de suprimentos.",
    badge: "API /api/contratos_locacao",
    items: [
      "Contratos vigentes",
      "Suprimentos por contrato",
      "Valores contratuais mensais"
    ]
  },
  {
    title: "Integrações InterMax",
    description: "Sincronização com bases de dados do legado.",
    badge: "Roadmap",
    items: [
      "Mapeamento de dados InterMax.03.02.2026",
      "Importação de cadastros e movimentos",
      "Tratamento de inconsistências"
    ]
  }
];

const root = document.getElementById("root");

root.innerHTML = `
  <main>
    <header>
      <div>
        <h1>InterMax SaaS</h1>
        <p>Nova plataforma integrada com Django e frontend estático.</p>
      </div>
      <span class="badge">MVP em construção</span>
    </header>
    <div class="grid">
      ${sections
        .map(
          (section) => `
        <section class="card">
          <div>
            <h2>${section.title}</h2>
            <p>${section.description}</p>
          </div>
          <span class="badge">${section.badge}</span>
          <ul>
            ${section.items.map((item) => `<li>${item}</li>`).join("")}
          </ul>
        </section>
      `
        )
        .join("")}
    </div>
    <footer>
      <p>
        Backend disponível em <span class="code">/api/core/health</span> e roadmap
        em <span class="code">/api/core/roadmap</span>.
      </p>
    </footer>
  </main>
`;
