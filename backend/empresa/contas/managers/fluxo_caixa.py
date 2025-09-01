from django.db import models

class FluxoCaixaLancamentoManager(models.Manager):
    def criar_lancamento_conta_pagar(self, conta):
        return self.create(
            data=conta.vencimento,
            tipo='saida',
            valor=conta.valor,
            realizado=False,
            descricao=f"Pagamento {conta.fornecedor}",
            categoria='despesas_operacionais',
            fonte_tipo='conta_pagar',
            fonte_id=conta.id
        )

    def criar_lancamento_conta_receber(self, conta):
        return self.create(
            data=conta.vencimento,
            tipo='entrada',
            valor=conta.valor,
            realizado=False,
            descricao=f"Recebimento {conta.cliente}",
            categoria='vendas',
            fonte_tipo='conta_receber',
            fonte_id=conta.id,
            cliente=conta.cliente
        )