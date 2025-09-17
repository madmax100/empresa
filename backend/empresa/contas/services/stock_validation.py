"""
Stock Validation Service
This service validates current stock levels by comparing calculated stock
against the stored estoque_atual values in the produtos table.
"""
from datetime import date
from decimal import Decimal
from typing import Dict, List, Any, Optional
from django.utils import timezone
from django.db.models import Q
import logging

from ..models.access import Produtos
from .stock_calculation import StockCalculationService

logger = logging.getLogger(__name__)


class StockValidationService:
    """Service for validating stock calculations against stored values"""
    
    @staticmethod
    def validate_current_stock(produto_ids: List[int] = None) -> Dict[str, Any]:
        """
        Compare calculated current stock vs produtos.estoque_atual for products.
        Args:
            produto_ids: List of specific product IDs to validate. If None, validates all products.
        Returns:
            Dict containing validation results:
            {
                'total_products': int,
                'correct_stock': int,
                'incorrect_stock': int,
                'discrepancies': List[Dict],
                'validation_date': str,
                'summary': Dict
            }
        """
        try:
            logger.info("Starting stock validation process")
            
            # Get products to validate
            if produto_ids:
                produtos = Produtos.objects.filter(id__in=produto_ids, ativo=True)
                logger.info(f"Validating {len(produto_ids)} specific products")
            else:
                produtos = Produtos.objects.filter(ativo=True)
                logger.info(f"Validating all {produtos.count()} active products")

            validation_results = {
                'total_products': produtos.count(),
                'correct_stock': 0,
                'incorrect_stock': 0,
                'discrepancies': [],
                'validation_date': timezone.now().isoformat(),
                'summary': {}
            }

            # Validate each product
            for produto in produtos:
                try:
                    # Calculate current stock
                    calculated_stock = StockCalculationService.calculate_current_stock(produto.id)
                    stored_stock = Decimal(str(produto.estoque_atual))
                    
                    # Check for discrepancy
                    if calculated_stock == stored_stock:
                        validation_results['correct_stock'] += 1
                        logger.debug(f"Product {produto.codigo}: Stock correct ({calculated_stock})")
                    else:
                        validation_results['incorrect_stock'] += 1
                        discrepancy = {
                            'produto_id': produto.id,
                            'produto_codigo': produto.codigo,
                            'produto_nome': produto.nome,
                            'calculated_stock': float(calculated_stock),
                            'stored_stock': float(stored_stock),
                            'difference': float(calculated_stock - stored_stock),
                            'percentage_diff': float(
                                ((calculated_stock - stored_stock) / max(stored_stock, Decimal('1'))) * 100
                            )
                        }
                        validation_results['discrepancies'].append(discrepancy)
                        logger.warning(
                            f"Large stock discrepancy for product {produto.codigo}: "
                            f"stored={stored_stock}, calculated={calculated_stock:.3f}, "
                            f"difference={calculated_stock - stored_stock:.3f}"
                        )
                except Exception as e:
                    logger.error(f"Error validating product {produto.codigo}: {str(e)}")
                    validation_results['incorrect_stock'] += 1
                    validation_results['discrepancies'].append({
                        'produto_id': produto.id,
                        'produto_codigo': produto.codigo,
                        'produto_nome': produto.nome,
                        'error': str(e),
                        'calculated_stock': None,
                        'stored_stock': float(produto.estoque_atual),
                        'difference': None
                    })

            # Generate summary
            validation_results['summary'] = {
                'accuracy_percentage': (
                    (validation_results['correct_stock'] / validation_results['total_products']) * 100
                    if validation_results['total_products'] > 0 else 0
                ),
                'total_discrepancies': len(validation_results['discrepancies']),
                'largest_positive_diff': max(
                    [d.get('difference', 0) for d in validation_results['discrepancies'] 
                     if d.get('difference') is not None], default=0
                ),
                'largest_negative_diff': min(
                    [d.get('difference', 0) for d in validation_results['discrepancies'] 
                     if d.get('difference') is not None], default=0
                )
            }

            logger.info(
                f"Stock validation completed. Accuracy: "
                f"{validation_results['summary']['accuracy_percentage']:.2f}% "
                f"({validation_results['correct_stock']}/{validation_results['total_products']})"
            )
            return validation_results
        except Exception as e:
            logger.error(f"Error during stock validation: {str(e)}")
            raise

    @staticmethod
    def find_stock_discrepancies(threshold: Decimal = Decimal('0.01')) -> List[Dict[str, Any]]:
        """
        Find products with stock discrepancies above a threshold.
        Args:
            threshold: Minimum difference to consider as discrepancy
        Returns:
            List of products with discrepancies
        """
        try:
            logger.info(f"Finding stock discrepancies with threshold: {threshold}")
            discrepancies = []
            produtos = Produtos.objects.filter(ativo=True)
            
            for produto in produtos:
                try:
                    calculated_stock = StockCalculationService.calculate_current_stock(produto.id)
                    stored_stock = Decimal(str(produto.estoque_atual))
                    difference = abs(calculated_stock - stored_stock)
                    
                    if difference >= threshold:
                        discrepancies.append({
                            'produto_id': produto.id,
                            'produto_codigo': produto.codigo,
                            'produto_nome': produto.nome,
                            'calculated_stock': float(calculated_stock),
                            'stored_stock': float(stored_stock),
                            'difference': float(calculated_stock - stored_stock),
                            'abs_difference': float(difference)
                        })
                        logger.info(
                            f"Large stock discrepancy for product {produto.codigo}: "
                            f"stored={stored_stock}, calculated={calculated_stock:.3f}, "
                            f"difference={calculated_stock - stored_stock:.3f}"
                        )
                except Exception as e:
                    logger.error(f"Error checking discrepancy for product {produto.codigo}: {str(e)}")
                    discrepancies.append({
                        'produto_id': produto.id,
                        'produto_codigo': produto.codigo,
                        'produto_nome': produto.nome,
                        'error': str(e),
                        'calculated_stock': None,
                        'stored_stock': float(produto.estoque_atual),
                        'difference': None,
                        'abs_difference': None
                    })

            # Sort by absolute difference (largest first)
            discrepancies.sort(key=lambda x: x.get('abs_difference', 0) or 0, reverse=True)
            
            logger.info(f"Found {len(discrepancies)} products with stock discrepancies")
            return discrepancies
        except Exception as e:
            logger.error(f"Error finding stock discrepancies: {str(e)}")
            raise

    @staticmethod
    def generate_validation_report(produto_ids: List[int] = None) -> Dict[str, Any]:
        """
        Generate comprehensive validation report.
        Args:
            produto_ids: List of specific product IDs to validate
        Returns:
            Dict containing comprehensive validation report
        """
        try:
            logger.info("Generating comprehensive validation report")
            
            # Get basic validation results
            validation_results = StockValidationService.validate_current_stock(produto_ids)
            
            # Add additional analysis
            report = {
                **validation_results,
                'analysis': {
                    'products_with_zero_calculated': 0,
                    'products_with_zero_stored': 0,
                    'products_with_negative_calculated': 0,
                    'products_with_negative_stored': 0,
                    'average_difference': 0,
                    'median_difference': 0
                },
                'recommendations': []
            }

            # Analyze discrepancies
            if validation_results['discrepancies']:
                differences = [
                    d['difference'] for d in validation_results['discrepancies'] 
                    if d.get('difference') is not None
                ]
                if differences:
                    report['analysis']['average_difference'] = sum(differences) / len(differences)
                    sorted_diffs = sorted(differences)
                    mid = len(sorted_diffs) // 2
                    report['analysis']['median_difference'] = (
                        sorted_diffs[mid] if len(sorted_diffs) % 2 == 1
                        else (sorted_diffs[mid - 1] + sorted_diffs[mid]) / 2
                    )

                # Count special cases
                for discrepancy in validation_results['discrepancies']:
                    calc_stock = discrepancy.get('calculated_stock')
                    stored_stock = discrepancy.get('stored_stock')
                    if calc_stock == 0:
                        report['analysis']['products_with_zero_calculated'] += 1
                    if stored_stock == 0:
                        report['analysis']['products_with_zero_stored'] += 1
                    if calc_stock and calc_stock < 0:
                        report['analysis']['products_with_negative_calculated'] += 1
                    if stored_stock and stored_stock < 0:
                        report['analysis']['products_with_negative_stored'] += 1

            # Generate recommendations
            if report['analysis']['products_with_negative_calculated'] > 0:
                report['recommendations'].append(
                    "Some products have negative calculated stock. "
                    "Review movement data for data quality issues."
                )
            if validation_results['summary']['accuracy_percentage'] < 95:
                report['recommendations'].append(
                    "Stock accuracy is below 95%. Consider running stock correction process."
                )
            if len(validation_results['discrepancies']) > 0:
                report['recommendations'].append(
                    f"Found {len(validation_results['discrepancies'])} products with stock discrepancies. "
                    "Review individual products for correction."
                )

            logger.info("Validation report generated successfully")
            return report
        except Exception as e:
            logger.error(f"Error generating validation report: {str(e)}")
            raise

    @staticmethod
    def validate_single_product(produto_id: int) -> Dict[str, Any]:
        """
        Validate stock for a single product with detailed information.
        Args:
            produto_id: ID of the product to validate
        Returns:
            Dict containing detailed validation information for the product
        """
        try:
            produto = Produtos.objects.get(id=produto_id)
            
            # Calculate current stock
            calculated_stock = StockCalculationService.calculate_current_stock(produto_id)
            stored_stock = Decimal(str(produto.estoque_atual))
            
            # Get stock reset information
            today = timezone.now()
            base_stock, reset_date = StockCalculationService.get_base_stock_reset(produto_id, today)
            
            # Count movements
            from ..models.access import MovimentacoesEstoque
            total_movements = MovimentacoesEstoque.objects.filter(produto_id=produto_id).count()
            reset_movements = MovimentacoesEstoque.objects.filter(
                produto_id=produto_id, documento_referencia='000000'
            ).count()

            result = {
                'produto_id': produto_id,
                'produto_codigo': produto.codigo,
                'produto_nome': produto.nome,
                'calculated_stock': float(calculated_stock),
                'stored_stock': float(stored_stock),
                'difference': float(calculated_stock - stored_stock),
                'is_correct': calculated_stock == stored_stock,
                'stock_reset_info': {
                    'has_reset': reset_date is not None,
                    'reset_date': reset_date.isoformat() if reset_date else None,
                    'reset_quantity': float(base_stock) if reset_date else None,
                    'total_resets': reset_movements
                },
                'movement_info': {
                    'total_movements': total_movements,
                    'regular_movements': total_movements - reset_movements
                },
                'validation_date': timezone.now().isoformat()
            }

            logger.info(f"Single product validation completed for {produto.codigo}")
            return result
        except Produtos.DoesNotExist:
            raise ValueError(f"Product with ID {produto_id} does not exist")
        except Exception as e:
            logger.error(f"Error validating single product {produto_id}: {str(e)}")
            raise