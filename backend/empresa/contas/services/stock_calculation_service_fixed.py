# backend/empresa/contas/services/stock_calculation_service.py
from datetime import datetime, date, time
from django.db.models import Sum, Q
from decimal import Decimal

from ..models.access import MovimentacoesEstoque, Produtos

class StockCalculationService:
    """
    Serviço para calcular o estoque de um produto em uma data específica,
    usando a nova metodologia baseada em 'estoque_atual' e 'resets'.
    """

    @staticmethod
    def calculate_stock_at_date(produto_id: int, target_date: date) -> Decimal:
        """
        Calcula o estoque de um produto em uma data específica.

        A lógica é:
        1. Encontrar o 'reset' de estoque mais recente (doc '000000') em ou antes da data alvo.
        2. Se um reset for encontrado, usa-o como base e aplica as movimentações até a data alvo.
        3. Se nenhum reset for encontrado, usa o 'estoque_atual' do produto e reverte as
           movimentações desde a data alvo até hoje.
        """
        
        # Garante que a data alvo inclua o dia inteiro
        target_datetime_end = datetime.combine(target_date, time.max)

        # 1. Tenta encontrar o reset de estoque mais recente
        latest_reset = MovimentacoesEstoque.objects.filter(
            produto_id=produto_id,
            documento_referencia='000000',
            data_movimentacao__lte=target_datetime_end
        ).order_by('-data_movimentacao').first()

        if latest_reset:
            # 2. Se um reset foi encontrado, calcula a partir dele
            base_quantity = latest_reset.quantidade
            base_date = latest_reset.data_movimentacao

            # Calcula a soma das movimentações entre a data do reset e a data alvo
            movements = MovimentacoesEstoque.objects.filter(
                produto_id=produto_id,
                data_movimentacao__gt=base_date,
                data_movimentacao__lte=target_datetime_end
            ).exclude(documento_referencia='000000')
            
        else:
            # 3. Se nenhum reset foi encontrado, calcula retroativamente a partir do estoque atual
            try:
                produto = Produtos.objects.get(id=produto_id)
                base_quantity = produto.estoque_atual or Decimal('0')
            except Produtos.DoesNotExist:
                # Se o produto não existe, o estoque é zero
                return Decimal('0')

            # As movimentações a serem revertidas são as que ocorreram DEPOIS da data alvo
            movements = MovimentacoesEstoque.objects.filter(
                produto_id=produto_id,
                data_movimentacao__gt=target_datetime_end
            ).exclude(documento_referencia='000000')

        # Agrega as movimentações
        aggregation = movements.aggregate(
            total_entradas=Sum('quantidade', filter=Q(tipo_movimentacao__id__in=[1, 3])), # 1: Entrada, 3: Inicial
            total_saidas=Sum('quantidade', filter=Q(tipo_movimentacao__id=2)) # 2: Saída
        )

        entradas = aggregation.get('total_entradas') or Decimal('0')
        saidas = aggregation.get('total_saidas') or Decimal('0')

        if latest_reset:
            # Cálculo progressivo: base + entradas - saídas
            final_stock = base_quantity + entradas - saidas
        else:
            # Cálculo retroativo: base - entradas + saídas
            final_stock = base_quantity - entradas + saidas
            
        # Garante que o estoque final não seja negativo
        final_stock = max(Decimal('0'), final_stock)
            
        return final_stock