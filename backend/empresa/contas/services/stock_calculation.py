"""
Stock Calculation Service

This service handles historical stock calculations, properly managing stock resets
(documento_referencia "000000") and regular stock movements.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Tuple, Dict, Any
from django.db.models import QuerySet
from django.utils import timezone
import logging

from ..models.access import MovimentacoesEstoque, Produtos, TiposMovimentacaoEstoque

logger = logging.getLogger(__name__)


class StockCalculationService:
    """
    Service for calculating historical stock levels for products.
    
    Handles the special logic for documento_referencia "000000" which represents
    stock resets rather than regular movements.
    """
    
    @staticmethod
    def calculate_stock_at_date(produto_id: int, target_date: date) -> Decimal:
        """
        Calculate stock for a product at a specific date.
        
        Algorithm:
        1. Find the most recent "000000" reset before or on target_date
        2. If found, use that quantity as base stock and ignore earlier movements
        3. If not found, start with 0 stock
        4. Apply all non-"000000" movements chronologically after the reset date
        
        Args:
            produto_id: ID of the product
            target_date: Date to calculate stock for
            
        Returns:
            Decimal: Stock quantity at the target date
            
        Raises:
            ValueError: If produto_id is invalid
        """
        try:
            # Validate product exists
            if not Produtos.objects.filter(id=produto_id).exists():
                raise ValueError(f"Product with ID {produto_id} does not exist")
            
            # Convert date to datetime for comparison if needed
            if isinstance(target_date, date) and not isinstance(target_date, datetime):
                target_datetime = datetime.combine(target_date, datetime.max.time())
                target_datetime = timezone.make_aware(target_datetime)
            else:
                target_datetime = target_date
            
            # Step 1: Find the most recent stock reset before target date
            base_stock, reset_date = StockCalculationService.get_base_stock_reset(
                produto_id, target_datetime
            )
            
            # Step 2: Apply movements after reset date up to target date
            final_stock = StockCalculationService.apply_movements_after_reset(
                produto_id, reset_date, target_datetime, base_stock
            )
            
            logger.info(
                f"Stock calculation for product {produto_id} on {target_date}: "
                f"base={base_stock}, final={final_stock}"
            )
            
            return final_stock
            
        except Exception as e:
            logger.error(f"Error calculating stock for product {produto_id} on {target_date}: {str(e)}")
            raise
    
    @staticmethod
    def get_base_stock_reset(produto_id: int, target_date: datetime) -> Tuple[Decimal, Optional[datetime]]:
        """
        Find the most recent '000000' reset before target date.
        
        Args:
            produto_id: ID of the product
            target_date: Target date to search before
            
        Returns:
            Tuple[Decimal, Optional[datetime]]: (base_stock_quantity, reset_date)
            If no reset found, returns (Decimal('0'), None)
        """
        try:
            # Query for the most recent "000000" movement before target date
            reset_movement = MovimentacoesEstoque.objects.filter(
                produto_id=produto_id,
                documento_referencia='000000',
                data_movimentacao__lte=target_date
            ).order_by('-data_movimentacao').first()
            
            if reset_movement:
                logger.debug(
                    f"Found stock reset for product {produto_id}: "
                    f"quantity={reset_movement.quantidade}, date={reset_movement.data_movimentacao}"
                )
                return reset_movement.quantidade, reset_movement.data_movimentacao
            else:
                logger.debug(f"No stock reset found for product {produto_id} before {target_date}")
                return Decimal('0'), None
                
        except Exception as e:
            logger.error(f"Error finding stock reset for product {produto_id}: {str(e)}")
            raise
    
    @staticmethod
    def apply_movements_after_reset(
        produto_id: int, 
        reset_date: Optional[datetime], 
        target_date: datetime, 
        base_stock: Decimal
    ) -> Decimal:
        """
        Apply all movements between reset date and target date.
        
        Args:
            produto_id: ID of the product
            reset_date: Date of the stock reset (None if no reset)
            target_date: Target date to calculate up to
            base_stock: Starting stock quantity
            
        Returns:
            Decimal: Final stock after applying movements
        """
        try:
            current_stock = base_stock
            
            # Build query for movements after reset date
            movements_query = MovimentacoesEstoque.objects.filter(
                produto_id=produto_id,
                documento_referencia__isnull=False
            ).exclude(
                documento_referencia='000000'
            ).filter(
                data_movimentacao__lte=target_date
            ).select_related('tipo_movimentacao')
            
            # If we have a reset date, only include movements after it
            if reset_date:
                movements_query = movements_query.filter(data_movimentacao__gt=reset_date)
            
            # Order chronologically
            movements = movements_query.order_by('data_movimentacao')
            
            # Apply each movement
            for movement in movements:
                if movement.tipo_movimentacao:
                    if movement.tipo_movimentacao.tipo == 'E':  # Entrada (Entry)
                        current_stock += movement.quantidade
                        logger.debug(
                            f"Applied entrada: +{movement.quantidade} "
                            f"(new stock: {current_stock}) on {movement.data_movimentacao}"
                        )
                    elif movement.tipo_movimentacao.tipo == 'S':  # Saída (Exit)
                        current_stock -= movement.quantidade
                        logger.debug(
                            f"Applied saída: -{movement.quantidade} "
                            f"(new stock: {current_stock}) on {movement.data_movimentacao}"
                        )
                    else:
                        logger.warning(
                            f"Unknown movement type '{movement.tipo_movimentacao.tipo}' "
                            f"for movement {movement.id}"
                        )
                else:
                    logger.warning(f"Movement {movement.id} has no tipo_movimentacao")
            
            return current_stock
            
        except Exception as e:
            logger.error(
                f"Error applying movements for product {produto_id} "
                f"between {reset_date} and {target_date}: {str(e)}"
            )
            raise
    
    @staticmethod
    def get_current_stock_from_table(produto_id: int) -> Decimal:
        """
        Get the current stock value from produtos.estoque_atual field.
        
        Args:
            produto_id: ID of the product
            
        Returns:
            Decimal: Current stock from produtos table
            
        Raises:
            ValueError: If product not found
        """
        try:
            produto = Produtos.objects.get(id=produto_id)
            return Decimal(str(produto.estoque_atual or 0))
        except Produtos.DoesNotExist:
            raise ValueError(f"Product with ID {produto_id} does not exist")
    
    @staticmethod
    def calculate_current_stock(produto_id: int) -> Decimal:
        """
        Calculate current stock using today's date.
        
        Args:
            produto_id: ID of the product
            
        Returns:
            Decimal: Calculated current stock
        """
        today = timezone.now().date()
        return StockCalculationService.calculate_stock_at_date(produto_id, today)
    
    @staticmethod
    def get_stock_movements_summary(produto_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Get a summary of stock movements for a product in a date range.
        
        Args:
            produto_id: ID of the product
            start_date: Start date for the range
            end_date: End date for the range
            
        Returns:
            Dict containing movement summary
        """
        try:
            # Convert dates to datetime
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)
            
            # Get movements in range
            movements = MovimentacoesEstoque.objects.filter(
                produto_id=produto_id,
                data_movimentacao__gte=start_datetime,
                data_movimentacao__lte=end_datetime
            ).select_related('tipo_movimentacao').order_by('data_movimentacao')
            
            # Separate resets from regular movements
            resets = []
            regular_movements = []
            total_entrada = Decimal('0')
            total_saida = Decimal('0')
            
            for movement in movements:
                if movement.documento_referencia == '000000':
                    resets.append({
                        'date': movement.data_movimentacao,
                        'quantity': movement.quantidade,
                        'document': movement.documento_referencia
                    })
                else:
                    movement_data = {
                        'date': movement.data_movimentacao,
                        'quantity': movement.quantidade,
                        'document': movement.documento_referencia,
                        'type': movement.tipo_movimentacao.tipo if movement.tipo_movimentacao else None
                    }
                    regular_movements.append(movement_data)
                    
                    if movement.tipo_movimentacao:
                        if movement.tipo_movimentacao.tipo == 'E':
                            total_entrada += movement.quantidade
                        elif movement.tipo_movimentacao.tipo == 'S':
                            total_saida += movement.quantidade
            
            return {
                'produto_id': produto_id,
                'period': {
                    'start': start_date,
                    'end': end_date
                },
                'stock_resets': resets,
                'regular_movements': regular_movements,
                'totals': {
                    'entrada': total_entrada,
                    'saida': total_saida,
                    'net_movement': total_entrada - total_saida
                },
                'stock_at_start': StockCalculationService.calculate_stock_at_date(produto_id, start_date),
                'stock_at_end': StockCalculationService.calculate_stock_at_date(produto_id, end_date)
            }
            
        except Exception as e:
            logger.error(f"Error getting stock movements summary for product {produto_id}: {str(e)}")
            raise