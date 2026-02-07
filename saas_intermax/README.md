# InterMax SaaS (Django + Frontend)

Este diretório contém um novo SaaS baseado na estrutura existente do repositório, com módulos de estoque, contas e faturamento prontos para integrar a base InterMax.

## Estrutura

- `backend/`: API em Django (DRF) com módulos para estoque, contas e faturamento.
- `frontend/`: Frontend estático para consumir a API.

## Como iniciar (local)

### Backend

```bash
cd saas_intermax/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python intermax/manage.py migrate
python intermax/manage.py runserver
```

### Frontend

```bash
cd saas_intermax/frontend
npm install
npm run dev
```

## Endpoints principais

- `GET /api/estoque/resumo/`
- `GET /api/estoque/relatorio-valor-estoque/`
- `GET /api/contas/resumo/pagar/`
- `GET /api/contas/resumo/receber/`
- `GET /api/contas/resumo/fluxo-caixa/`
- `GET /api/contas/relatorios/custos-fixos/?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD`
- `GET /api/contas/relatorios/custos-variaveis/?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD`
- `GET /api/faturamento/resumo/`
- `GET /api/faturamento/contratos/resumo/`
- `GET /api/faturamento/relatorios/faturamento/?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD`
- `GET /api/contratos_locacao/suprimentos/?data_inicial=YYYY-MM-DD&data_final=YYYY-MM-DD`

## Observações

Os endpoints iniciais são baseados nos documentos existentes no repositório e em referências ao diretório `InterMax.03.02.2026`, que não está presente no container. As respostas atuais usam dados persistidos no banco local para permitir o alinhamento com a base quando estiver disponível.
