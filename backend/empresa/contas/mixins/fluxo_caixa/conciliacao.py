# empresa/contas/mixins/fluxo_caixa/conciliacao.py
from typing import Dict, Any
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, Q
from contas.models import (FluxoCaixaLancamento, ContasPagar, ContasReceber, 
                          ContratosLocacao)

class FluxoCaixaConciliacaoMixin:
    """
    Mixin para conciliação bancária e ajustes
    """
    def _conciliar_lancamento(self, lancamento: FluxoCaixaLancamento) -> Dict[str, Any]:
        """Concilia um lançamento com seu documento de origem"""
        resultado = {
            'lancamento': self.get_serializer(lancamento).data,
            'documento': None,
            'status': 'pendente',
            'divergencias': []
        }

        if lancamento.fonte_tipo == 'conta_receber':
            documento = ContasReceber.objects.filter(id=lancamento.fonte_id).first()
            if documento:
                resultado['documento'] = {
                    'id': documento.id,
                    'cliente': documento.cliente.nome if documento.cliente else None,
                    'valor': float(documento.valor),
                    'vencimento': documento.vencimento,
                    'status': documento.status
                }
                
                if documento.valor != lancamento.valor:
                    resultado['divergencias'].append('valor_diferente')
                if documento.vencimento != lancamento.data:
                    resultado['divergencias'].append('data_diferente')
                if documento.status != 'P':
                    resultado['divergencias'].append('status_diferente')

        # Similar para conta_pagar e contrato...

        if not resultado['divergencias']:
            resultado['status'] = 'conciliado'
        else:
            resultado['status'] = 'divergente'

        return resultado