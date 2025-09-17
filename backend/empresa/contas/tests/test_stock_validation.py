"""
Unit tests for Stock Validation Service
Tests validation of calculated stock against stored stock values.
"""
from datetime import date, datetime
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch, MagicMock

from ..models.access import Produtos, MovimentacoesEstoque, TiposMovimentacaoEstoque
from ..services.stock_validation import StockValidationService
from ..services.stock_calculation import StockCalculationService


class StockValidationServiceTest(TestCase):
    """Test cases for StockValidationService"""
    
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
        
        # Create test products
        self.produto1 = Produtos.objects.create(
            codigo='TEST001',
            nome='Produto Correto',
            estoque_atual=100,  # This will match calculated stock
            ativo=True
        )
        
        self.produto2 = Produtos.objects.create(
            codigo='TEST002',
            nome='Produto Incorreto',
            estoque_atual=50,   # This will NOT match calculated stock
            ativo=True
        )
        
        self.produto3 = Produtos.objects.create(
            codigo='TEST003',
            nome='Produto Inativo',
            estoque_atual=25,
            ativo=False  # Inactive product
        )
    
    def _create_movement(self, produto, data_movimentacao, quantidade, tipo_movimentacao, documento_referencia='DOC001'):
        """Helper method to create stock movements"""
        if isinstance(data_movimentacao, date):
            data_movimentacao = timezone.make_aware(
                datetime.combine(data_movimentacao, datetime.min.time())
            )
        
        return MovimentacoesEstoque.objects.create(
            produto=produto,
            data_movimentacao=data_movimentacao,
            quantidade=Decimal(str(quantidade)),
            tipo_movimentacao=tipo_movimentacao,
            documento_referencia=documento_referencia
        )
    
    def _setup_test_movements(self):
        """Set up movements for test products"""
        # Product 1: Movements that result in stock = 100 (matches stored)
        self._create_movement(
            self.produto1, date(2024, 1, 1), 80, self.tipo_entrada, '000000'
        )
        self._create_movement(
            self.produto1, date(2024, 1, 15), 20, self.tipo_entrada
        )
        # Final calculated stock: 80 + 20 = 100 ✓
        
        # Product 2: Movements that result in stock = 75 (doesn't match stored 50)
        self._create_movement(
            self.produto2, date(2024, 1, 1), 60, self.tipo_entrada, '000000'
        )
        self._create_movement(
            self.produto2, date(2024, 1, 15), 15, self.tipo_entrada
        )
        # Final calculated stock: 60 + 15 = 75 ≠ 50 ✗
        
        # Product 3: Inactive, should be ignored in validation
        self._create_movement(
            self.produto3, date(2024, 1, 1), 25, self.tipo_entrada, '000000'
        )
    
    @patch('django.utils.timezone.now')
    def test_validate_current_stock_all_products(self, mock_now):
        """Test validating all active products"""
        mock_now.return_value = timezone.make_aware(datetime(2024, 1, 25, 15, 30))
        self._setup_test_movements()
        
        result = StockValidationService.validate_current_stock()
        
        # Should validate only active products (2 products)
        self.assertEqual(result['total_products'], 2)
        self.assertEqual(result['correct_stock'], 1)  # produto1
        self.assertEqual(result['incorrect_stock'], 1)  # produto2
        self.assertEqual(len(result['discrepancies']), 1)
        
        # Check discrepancy details
        discrepancy = result['discrepancies'][0]
        self.assertEqual(discrepancy['produto_codigo'], 'TEST002')
        self.assertEqual(discrepancy['calculated_stock'], 75.0)
        self.assertEqual(discrepancy['stored_stock'], 50.0)
        self.assertEqual(discrepancy['difference'], 25.0)
        
        # Check summary
        self.assertEqual(result['summary']['accuracy_percentage'], 50.0)  # 1/2 * 100
        self.assertEqual(result['summary']['total_discrepancies'], 1)
    
    @patch('django.utils.timezone.now')
    def test_validate_current_stock_specific_products(self, mock_now):
        """Test validating specific products"""
        mock_now.return_value = timezone.make_aware(datetime(2024, 1, 25, 15, 30))
        self._setup_test_movements()
        
        # Validate only produto1
        result = StockValidationService.validate_current_stock([self.produto1.id])
        
        self.assertEqual(result['total_products'], 1)
        self.assertEqual(result['correct_stock'], 1)
        self.assertEqual(result['incorrect_stock'], 0)
        self.assertEqual(len(result['discrepancies']), 0)
        self.assertEqual(result['summary']['accuracy_percentage'], 100.0)
    
    @patch('django.utils.timezone.now')
    def test_find_stock_discrepancies(self, mock_now):
        """Test finding stock discrepancies with threshold"""
        mock_now.return_value = timezone.make_aware(datetime(2024, 1, 25, 15, 30))
        self._setup_test_movements()
        
        # Find discrepancies with threshold of 10
        discrepancies = StockValidationService.find_stock_discrepancies(Decimal('10'))
        
        # Should find produto2 (difference = 25, above threshold)
        self.assertEqual(len(discrepancies), 1)
        self.assertEqual(discrepancies[0]['produto_codigo'], 'TEST002')
        self.assertEqual(discrepancies[0]['abs_difference'], 25.0)
        
        # Test with higher threshold
        discrepancies_high = StockValidationService.find_stock_discrepancies(Decimal('30'))
        self.assertEqual(len(discrepancies_high), 0)  # No discrepancies above 30
    
    @patch('django.utils.timezone.now')
    def test_generate_validation_report(self, mock_now):
        """Test generating comprehensive validation report"""
        mock_now.return_value = timezone.make_aware(datetime(2024, 1, 25, 15, 30))
        self._setup_test_movements()
        
        report = StockValidationService.generate_validation_report()
        
        # Check basic validation data
        self.assertEqual(report['total_products'], 2)
        self.assertEqual(report['correct_stock'], 1)
        self.assertEqual(report['incorrect_stock'], 1)
        
        # Check analysis section
        self.assertIn('analysis', report)
        self.assertEqual(report['analysis']['average_difference'], 25.0)
        self.assertEqual(report['analysis']['median_difference'], 25.0)
        
        # Check recommendations
        self.assertIn('recommendations', report)
        self.assertGreater(len(report['recommendations']), 0)
        
        # Should recommend stock correction since accuracy < 95%
        accuracy_rec = any('95%' in rec for rec in report['recommendations'])
        self.assertTrue(accuracy_rec)
    
    @patch('django.utils.timezone.now')
    def test_validate_single_product(self, mock_now):
        """Test validating a single product with detailed info"""
        mock_now.return_value = timezone.make_aware(datetime(2024, 1, 25, 15, 30))
        self._setup_test_movements()
        
        result = StockValidationService.validate_single_product(self.produto1.id)
        
        self.assertEqual(result['produto_id'], self.produto1.id)
        self.assertEqual(result['produto_codigo'], 'TEST001')
        self.assertEqual(result['calculated_stock'], 100.0)
        self.assertEqual(result['stored_stock'], 100.0)
        self.assertEqual(result['difference'], 0.0)
        self.assertTrue(result['is_correct'])
        
        # Check stock reset info
        self.assertTrue(result['stock_reset_info']['has_reset'])
        self.assertEqual(result['stock_reset_info']['reset_quantity'], 80.0)
        self.assertEqual(result['stock_reset_info']['total_resets'], 1)
        
        # Check movement info
        self.assertEqual(result['movement_info']['total_movements'], 2)
        self.assertEqual(result['movement_info']['regular_movements'], 1)
    
    def test_validate_single_product_invalid_id(self):
        """Test error handling for invalid product ID"""
        with self.assertRaises(ValueError):
            StockValidationService.validate_single_product(99999)
    
    @patch('django.utils.timezone.now')
    def test_validation_with_negative_stock(self, mock_now):
        """Test validation when calculated stock is negative"""
        mock_now.return_value = timezone.make_aware(datetime(2024, 1, 25, 15, 30))
        
        # Create movements that result in negative stock
        self._create_movement(
            self.produto1, date(2024, 1, 1), 50, self.tipo_entrada, '000000'
        )
        self._create_movement(
            self.produto1, date(2024, 1, 15), 80, self.tipo_saida  # More than available
        )
        # Calculated stock: 50 - 80 = -30
        
        report = StockValidationService.generate_validation_report([self.produto1.id])
        
        # Should detect negative calculated stock
        self.assertEqual(report['analysis']['products_with_negative_calculated'], 1)
        
        # Should recommend reviewing movement data
        negative_rec = any('negative calculated stock' in rec for rec in report['recommendations'])
        self.assertTrue(negative_rec)
    
    @patch('django.utils.timezone.now')
    def test_validation_with_zero_stocks(self, mock_now):
        """Test validation with zero stock scenarios"""
        mock_now.return_value = timezone.make_aware(datetime(2024, 1, 25, 15, 30))
        
        # Product with zero calculated stock
        # No movements = calculated stock 0, stored stock 100
        
        report = StockValidationService.generate_validation_report([self.produto1.id])
        
        # Should detect zero calculated stock
        self.assertEqual(report['analysis']['products_with_zero_calculated'], 1)
    
    @patch.object(StockCalculationService, 'calculate_current_stock')
    def test_validation_handles_calculation_errors(self, mock_calculate):
        """Test that validation handles calculation errors gracefully"""
        # Mock calculation to raise an error
        mock_calculate.side_effect = Exception("Calculation error")
        
        result = StockValidationService.validate_current_stock([self.produto1.id])
        
        # Should handle error gracefully
        self.assertEqual(result['total_products'], 1)
        self.assertEqual(result['correct_stock'], 0)
        self.assertEqual(result['incorrect_stock'], 1)
        self.assertEqual(len(result['discrepancies']), 1)
        
        # Error should be recorded in discrepancy
        discrepancy = result['discrepancies'][0]
        self.assertIn('error', discrepancy)
        self.assertEqual(discrepancy['error'], "Calculation error")
        self.assertIsNone(discrepancy['calculated_stock'])
    
    @patch('django.utils.timezone.now')
    def test_validation_report_sorting(self, mock_now):
        """Test that discrepancies are sorted by absolute difference"""
        mock_now.return_value = timezone.make_aware(datetime(2024, 1, 25, 15, 30))
        
        # Create another product with smaller discrepancy
        produto4 = Produtos.objects.create(
            codigo='TEST004',
            nome='Produto Pequena Diferença',
            estoque_atual=95,  # Small difference
            ativo=True
        )
        
        # Setup movements
        self._setup_test_movements()  # produto2 has difference of 25
        
        # produto4 has difference of 5
        self._create_movement(
            produto4, date(2024, 1, 1), 100, self.tipo_entrada, '000000'
        )
        # Calculated: 100, Stored: 95, Difference: 5
        
        discrepancies = StockValidationService.find_stock_discrepancies(Decimal('1'))
        
        # Should be sorted by absolute difference (largest first)
        self.assertEqual(len(discrepancies), 2)
        self.assertEqual(discrepancies[0]['produto_codigo'], 'TEST002')  # Difference: 25
        self.assertEqual(discrepancies[1]['produto_codigo'], 'TEST004')  # Difference: 5
        self.assertGreater(discrepancies[0]['abs_difference'], discrepancies[1]['abs_difference'])
    
    @patch('django.utils.timezone.now')
    def test_validation_percentage_calculations(self, mock_now):
        """Test percentage difference calculations"""
        mock_now.return_value = timezone.make_aware(datetime(2024, 1, 25, 15, 30))
        self._setup_test_movements()
        
        result = StockValidationService.validate_current_stock([self.produto2.id])
        
        discrepancy = result['discrepancies'][0]
        # Calculated: 75, Stored: 50, Difference: 25
        # Percentage: (25 / 50) * 100 = 50%
        self.assertEqual(discrepancy['percentage_diff'], 50.0)
    
    @patch('django.utils.timezone.now')
    def test_validation_with_empty_database(self, mock_now):
        """Test validation when no products exist"""
        mock_now.return_value = timezone.make_aware(datetime(2024, 1, 25, 15, 30))
        
        # Mark all products as inactive instead of deleting
        Produtos.objects.all().update(ativo=False)
        
        result = StockValidationService.validate_current_stock()
        
        self.assertEqual(result['total_products'], 0)
        self.assertEqual(result['correct_stock'], 0)
        self.assertEqual(result['incorrect_stock'], 0)
        self.assertEqual(len(result['discrepancies']), 0)
        self.assertEqual(result['summary']['accuracy_percentage'], 0)