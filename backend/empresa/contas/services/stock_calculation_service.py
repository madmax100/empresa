# backend/empresa/contas/services/stock_calculation_service.py
from datetime import datetime, date, time
from django.db.models import Sum, Q
from decimal import Decimal

from ..models.access import MovimentacoesEstoque, Produtos

class StockCalculationService:
    """
    Serviço para calcular o estoque de um produto em uma data específica.
    
    LÓGICA CORRETA:
    - O campo 'estoque_atual' da tabela produtos contém o estoque real atual (importado do Access)
    - Para datas passadas: estoque_atual - movimentações posteriores à data alvo
    - Para data atual: usar diretamente o estoque_atual
    """

    @staticmethod
    def calculate_stock_at_date(produto_id: int, target_date: date) -> Decimal:
        """
        Calcula o estoque de um produto em uma data específica.

        A lógica é:
        1. Obter o estoque_atual do produto (que representa o estoque real atual)
        2. Para data atual: retornar o estoque_atual diretamente
        3. Para datas passadas: estoque_atual - movimentações posteriores à data alvo
        """
        
        # Obter o produto e seu estoque atual
        try:
            produto = Produtos.objects.get(id=produto_id)
            estoque_atual = produto.estoque_atual or Decimal('0')
        except Produtos.DoesNotExist:
            return Decimal('0')

        # Para data atual, retornar o estoque_atual diretamente
        hoje = date.today()
        if target_date >= hoje:
            return estoque_atual

        # Para datas passadas, calcular retroativamente
        # Garante que a data alvo inclua o dia inteiro
        target_datetime_end = datetime.combine(target_date, time.max)

        # Calcular movimentações posteriores à data alvo
        movements_after_target = MovimentacoesEstoque.objects.filter(
            produto_id=produto_id,
            data_movimentacao__gt=target_datetime_end
        ).exclude(documento_referencia='000000')  # Excluir resets

        # Agregar as movimentações posteriores
        aggregation = movements_after_target.aggregate(
            total_entradas=Sum('quantidade', filter=Q(tipo_movimentacao__id__in=[1, 3])), # 1: Entrada, 3: Inicial
            total_saidas=Sum('quantidade', filter=Q(tipo_movimentacao__id=2)) # 2: Saída
        )

        entradas_posteriores = aggregation.get('total_entradas') or Decimal('0')
        saidas_posteriores = aggregation.get('total_saidas') or Decimal('0')

        # Cálculo retroativo: estoque_atual - entradas_posteriores + saidas_posteriores
        estoque_na_data = estoque_atual - entradas_posteriores + saidas_posteriores
            
        # Garante que o estoque final não seja negativo
        estoque_na_data = max(Decimal('0'), estoque_na_data)
            
        return estoque_na_data