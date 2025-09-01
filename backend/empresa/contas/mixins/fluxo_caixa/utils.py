from typing import Any, Optional
from decimal import Decimal
from django.core.exceptions import ValidationError
from contas.models import Clientes

class FluxoCaixaUtilsMixin:
    """
    Mixin com utilidades gerais para o fluxo de caixa
    """
    def _validar_cliente(self, cliente_id: int) -> None:
        """Valida se um cliente existe"""
        if not Clientes.objects.filter(id=cliente_id).exists():
            raise ValidationError(f'Cliente {cliente_id} não encontrado')

    def _normalizar_categoria(self, descricao: str) -> str:
        """Determina a categoria baseado na descrição"""
        keywords = {
            'vendas': ['venda', 'compra', 'aquisição'],
            'aluguel': ['aluguel', 'locação', 'locacao'],
            'servicos': ['serviço', 'servico', 'manutenção', 'manutencao'],
            'suprimentos': ['suprimento', 'toner', 'papel']
        }
        
        descricao = descricao.lower()
        for categoria, palavras in keywords.items():
            if any(p in descricao for p in palavras):
                return categoria
        return 'outros'

    def _formatar_moeda(self, valor: Decimal) -> str:
        """Formata um valor monetário"""
        return f"R$ {float(valor):,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')