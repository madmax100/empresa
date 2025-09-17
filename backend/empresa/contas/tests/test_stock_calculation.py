"""
Unit tests for StockCalculationService

Tests the stock calculation logic including handling of "000000" resets
and chronological processing of stock movements.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch, MagicMock

from ..models.access import Produtos, MovimentacoesEstoque, TiposMovimentacaoEstoque
from ..services.stock_calculation import StockCalculationService


class StockCalculationServiceTest(TestCase):
    """Test cases for StockCalculationService"""
    
    def setUp(self):
        """Set up test data"""
        # Create movement types
        self.tipo_entrada = TiposMovimentacaoEstoque.objects.create(
            codigo='ENT',
            descricao='Entrada de Estoque',
            tipo='E',
            ativo=True
        )
        
        self.tipo_saida = TiposMovimentacaoEstoque.objects.create(
            codigo='SAI',
            descricao='Saída de Estoque',
            tipo='S',
            ativo=True
        )
        
        # Create test product
        self.produto = Produtos.objects.create(
            codigo='TEST001',
            nome='Produto Teste',
            estoque_atual=50,
            ativo=True
        )
        
        # Base dates for testing
        self.base_date = date(2024, 1, 1)
        self.target_date = date(2024, 1, 25)
    
    def _create_movement(self, data_movimentacao, quantidade, tipo_movimentacao, documento_referencia='DOC001'):
        """Helper method to create stock movements"""
        if isinstance(data_movimentacao, date):
            data_movimentacao = timezone.make_aware(
                datetime.combine(data_movimentacao, datetime.min.time())
            )
        
        return MovimentacoesEstoque.objects.create(
            produto=self.produto,
            data_movimentacao=data_movimentacao,
            quantidade=Decimal(str(quantidade)),
            tipo_movimentacao=tipo_movimentacao,
            documento_referencia=documento_referencia
        )
    
    def test_calculate_stock_with_reset_and_movements(self):
        """Test Case 1: Product with stock reset and subsequent movements"""
        # Reset on 2024-01-01: quantity = 100
        self._create_movement(
            date(2024, 1, 1), 100, self.tipo_entrada, '000000'
        )
        
        # Movement on 2024-01-15: entrada +50
        self._create_movement(
            date(2024, 1, 15), 50, self.tipo_entrada
        )
        
        # Movement on 2024-01-20: saída -30
        self._create_movement(
            date(2024, 1, 20), 30, self.tipo_saida
        )
        
        # Expected stock on 2024-01-25: 100 + 50 - 30 = 120
        result = StockCalculationService.calculate_stock_at_date(
            self.produto.id, date(2024, 1, 25)
        )
        
        self.assertEqual(result, Decimal('120'))
    
    def test_calculate_stock_with_multiple_resets(self):
        """Test Case 2: Product with multiple resets"""
        # Reset on 2024-01-01: quantity = 100
        self._create_movement(
            date(2024, 1, 1), 100, self.tipo_entrada, '000000'
        )
        
        # Reset on 2024-02-01: quantity = 200 (should override previous)
        self._create_movement(
            date(2024, 2, 1), 200, self.tipo_entrada, '000000'
        )
        
        # Movement on 2024-02-15: entrada +25
        self._create_movement(
            date(2024, 2, 15), 25, self.tipo_entrada
        )
        
        # Expected stock on 2024-02-20: 200 + 25 = 225
        result = StockCalculationService.calculate_stock_at_date(
            self.produto.id, date(2024, 2, 20)
        )
        
        self.assertEqual(result, Decimal('225'))
    
    def test_calculate_stock_with_no_reset(self):
        """Test Case 3: Product with no reset (starts from 0)"""
        # Movement on 2024-01-10: entrada +75
        self._create_movement(
            date(2024, 1, 10), 75, self.tipo_entrada
        )
        
        # Movement on 2024-01-20: saída -25
        self._create_movement(
            date(2024, 1, 20), 25, self.tipo_saida
        )
        
        # Expected stock on 2024-01-25: 0 + 75 - 25 = 50
        result = StockCalculationService.calculate_stock_at_date(
            self.produto.id, date(2024, 1, 25)
        )
        
        self.assertEqual(result, Decimal('50'))
    
    def test_calculate_stock_no_movements(self):
        """Test Case 4: Product with no movements"""
        result = StockCalculationService.calculate_stock_at_date(
            self.produto.id, date(2024, 1, 25)
        )
        
        self.assertEqual(result, Decimal('0'))
    
    def test_calculate_stock_only_reset(self):
        """Test Case 5: Product with only reset, no other movements"""
        # Reset on 2024-01-01: quantity = 150
        self._create_movement(
            date(2024, 1, 1), 150, self.tipo_entrada, '000000'
        )
        
        # Expected stock on 2024-01-25: 150
        result = StockCalculationService.calculate_stock_at_date(
            self.produto.id, date(2024, 1, 25)
        )
        
        self.assertEqual(result, Decimal('150'))
    
    def test_calculate_stock_movements_before_reset_ignored(self):
        """Test Case 6: Movements before reset should be ignored"""
        # Movement on 2023-12-15: entrada +1000 (should be ignored)
        self._create_movement(
            date(2023, 12, 15), 1000, self.tipo_entrada
        )
        
        # Reset on 2024-01-01: quantity = 100
        self._create_movement(
            date(2024, 1, 1), 100, self.tipo_entrada, '000000'
        )
        
        # Movement on 2024-01-15: entrada +50
        self._create_movement(
            date(2024, 1, 15), 50, self.tipo_entrada
        )
        
        # Expected stock on 2024-01-25: 100 + 50 = 150 (not 1150)
        result = StockCalculationService.calculate_stock_at_date(
            self.produto.id, date(2024, 1, 25)
        )
        
        self.assertEqual(result, Decimal('150'))
    
    def test_calculate_stock_same_day_movements(self):
        """Test Case 7: Multiple movements on the same day"""
        # Reset on 2024-01-01: quantity = 100
        self._create_movement(
            date(2024, 1, 1), 100, self.tipo_entrada, '000000'
        )
        
        # Multiple movements on 2024-01-15
        self._create_movement(
            datetime(2024, 1, 15, 9, 0), 30, self.tipo_entrada, 'DOC001'
        )
        self._create_movement(
            datetime(2024, 1, 15, 14, 0), 20, self.tipo_saida, 'DOC002'
        )
        self._create_movement(
            datetime(2024, 1, 15, 16, 0), 10, self.tipo_entrada, 'DOC003'
        )
        
        # Expected stock on 2024-01-25: 100 + 30 - 20 + 10 = 120
        result = StockCalculationService.calculate_stock_at_date(
            self.produto.id, date(2024, 1, 25)
        )
        
        self.assertEqual(result, Decimal('120'))
    
    def test_calculate_stock_negative_result(self):
        """Test Case 8: Calculation resulting in negative stock"""
        # Reset on 2024-01-01: quantity = 50
        self._create_movement(
            date(2024, 1, 1), 50, self.tipo_entrada, '000000'
        )
        
        # Large saída on 2024-01-15: saída -80
        self._create_movement(
            date(2024, 1, 15), 80, self.tipo_saida
        )
        
        # Expected stock on 2024-01-25: 50 - 80 = -30
        result = StockCalculationService.calculate_stock_at_date(
            self.produto.id, date(2024, 1, 25)
        )
        
        self.assertEqual(result, Decimal('-30'))
    
    def test_get_base_stock_reset_found(self):
        """Test finding stock reset"""
        # Create reset movement
        reset_date = date(2024, 1, 1)
        self._create_movement(
            reset_date, 100, self.tipo_entrada, '000000'
        )
        
        target_date = timezone.make_aware(datetime(2024, 1, 25, 23, 59))
        base_stock, found_reset_date = StockCalculationService.get_base_stock_reset(
            self.produto.id, target_date
        )
        
        self.assertEqual(base_stock, Decimal('100'))
        self.assertIsNotNone(found_reset_date)
    
    def test_get_base_stock_reset_not_found(self):
        """Test when no stock reset is found"""
        target_date = timezone.make_aware(datetime(2024, 1, 25, 23, 59))
        base_stock, found_reset_date = StockCalculationService.get_base_stock_reset(
            self.produto.id, target_date
        )
        
        self.assertEqual(base_stock, Decimal('0'))
        self.assertIsNone(found_reset_date)
    
    def test_get_base_stock_reset_multiple_resets(self):
        """Test finding most recent reset when multiple exist"""
        # First reset
        reset_date1 = date(2024, 1, 1)
        self._create_movement(
            reset_date1, 100, self.tipo_entrada, '000000'
        )
        
        # Second reset (more recent)
        reset_date2 = date(2024, 1, 15)
        self._create_movement(
            reset_date2, 200, self.tipo_entrada, '000000'
        )
        
        target_date = timezone.make_aware(datetime(2024, 1, 25, 23, 59))
        base_stock, found_reset_date = StockCalculationService.get_base_stock_reset(
            self.produto.id, target_date
        )
        
        self.assertEqual(base_stock, Decimal('200'))
        self.assertIsNotNone(found_reset_date)
        # Check that it's the more recent reset by checking the date is after the first reset
        self.assertGreater(found_reset_date.date(), reset_date1)
    
    def test_apply_movements_after_reset(self):
        """Test applying movements after reset date"""
        reset_date = timezone.make_aware(datetime(2024, 1, 1, 10, 0))
        target_date = timezone.make_aware(datetime(2024, 1, 25, 23, 59))
        
        # Create movements after reset
        self._create_movement(
            datetime(2024, 1, 5, 10, 0), 30, self.tipo_entrada
        )
        self._create_movement(
            datetime(2024, 1, 10, 10, 0), 20, self.tipo_saida
        )
        
        result = StockCalculationService.apply_movements_after_reset(
            self.produto.id, reset_date, target_date, Decimal('100')
        )
        
        self.assertEqual(result, Decimal('110'))  # 100 + 30 - 20
    
    def test_calculate_stock_invalid_product(self):
        """Test error handling for invalid product ID"""
        with self.assertRaises(ValueError):
            StockCalculationService.calculate_stock_at_date(99999, date(2024, 1, 25))
    
    def test_get_current_stock_from_table(self):
        """Test getting current stock from produtos table"""
        result = StockCalculationService.get_current_stock_from_table(self.produto.id)
        self.assertEqual(result, Decimal('50'))
    
    def test_get_current_stock_from_table_invalid_product(self):
        """Test error handling for invalid product in get_current_stock_from_table"""
        with self.assertRaises(ValueError):
            StockCalculationService.get_current_stock_from_table(99999)
    
    @patch('django.utils.timezone.now')
    def test_calculate_current_stock(self, mock_now):
        """Test calculating current stock using today's date"""
        mock_now.return_value = timezone.make_aware(datetime(2024, 1, 25, 15, 30))
        
        # Create test data
        self._create_movement(
            date(2024, 1, 1), 100, self.tipo_entrada, '000000'
        )
        self._create_movement(
            date(2024, 1, 15), 25, self.tipo_entrada
        )
        
        result = StockCalculationService.calculate_current_stock(self.produto.id)
        self.assertEqual(result, Decimal('125'))
    
    def test_get_stock_movements_summary(self):
        """Test getting stock movements summary for a date range"""
        # Create test movements
        self._create_movement(
            date(2024, 1, 1), 100, self.tipo_entrada, '000000'
        )
        self._create_movement(
            date(2024, 1, 15), 30, self.tipo_entrada, 'DOC001'
        )
        self._create_movement(
            date(2024, 1, 20), 20, self.tipo_saida, 'DOC002'
        )
        
        summary = StockCalculationService.get_stock_movements_summary(
            self.produto.id, date(2024, 1, 1), date(2024, 1, 31)
        )
        
        self.assertEqual(summary['produto_id'], self.produto.id)
        self.assertEqual(len(summary['stock_resets']), 1)
        self.assertEqual(len(summary['regular_movements']), 2)
        self.assertEqual(summary['totals']['entrada'], Decimal('30'))
        self.assertEqual(summary['totals']['saida'], Decimal('20'))
        self.assertEqual(summary['totals']['net_movement'], Decimal('10'))
    
    def test_movements_without_tipo_movimentacao_ignored(self):
        """Test that movements without tipo_movimentacao are ignored"""
        # Reset
        self._create_movement(
            date(2024, 1, 1), 100, self.tipo_entrada, '000000'
        )
        
        # Valid movement
        self._create_movement(
            date(2024, 1, 15), 30, self.tipo_entrada
        )
        
        # Invalid movement (no tipo_movimentacao)
        MovimentacoesEstoque.objects.create(
            produto=self.produto,
            data_movimentacao=timezone.make_aware(datetime(2024, 1, 20, 10, 0)),
            quantidade=Decimal('50'),
            tipo_movimentacao=None,  # No movement type
            documento_referencia='DOC003'
        )
        
        # Expected stock: 100 + 30 = 130 (invalid movement ignored)
        result = StockCalculationService.calculate_stock_at_date(
            self.produto.id, date(2024, 1, 25)
        )
        
        self.assertEqual(result, Decimal('130'))