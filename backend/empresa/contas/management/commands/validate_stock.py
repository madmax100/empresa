from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import date, datetime
from decimal import Decimal
import csv
import json
from pathlib import Path

from contas.models.access import Produtos
from contas.services.stock_validation import StockValidationService


class Command(BaseCommand):
    help = 'Validate all product stock levels by comparing calculated vs stored values'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--product-ids',
            type=str,
            help='Comma-separated list of product IDs to validate (validates all if not specified)'
        )
        
        parser.add_argument(
            '--output-format',
            type=str,
            choices=['console', 'csv', 'json'],
            default='console',
            help='Output format for validation results'
        )
        
        parser.add_argument(
            '--output-file',
            type=str,
            help='Output file path (required for csv/json formats)'
        )
        
        parser.add_argument(
            '--threshold',
            type=float,
            default=0.01,
            help='Minimum difference threshold to report as discrepancy (default: 0.01)'
        )
        
        parser.add_argument(
            '--show-correct',
            action='store_true',
            help='Include products with correct stock in detailed output'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            help='Maximum number of products to validate'
        )
        
        parser.add_argument(
            '--detailed-report',
            action='store_true',
            help='Generate detailed validation report with analysis and recommendations'
        )
    
    def handle(self, *args, **options):
        try:
            self.stdout.write(
                self.style.SUCCESS('Starting stock validation process...')
            )
            
            # Parse product IDs if provided
            product_ids = self.get_product_ids(options)
            
            # Apply limit if specified
            if product_ids and options.get('limit'):
                product_ids = product_ids[:options['limit']]
            elif options.get('limit') and not product_ids:
                # Get limited set of all products
                produtos = Produtos.objects.filter(ativo=True)[:options['limit']]
                product_ids = [p.id for p in produtos]
            
            # Run validation
            if options['detailed_report']:
                results = StockValidationService.generate_validation_report(product_ids)
                self.stdout.write('Generated detailed validation report')
            else:
                results = StockValidationService.validate_current_stock(product_ids)
                self.stdout.write('Generated basic validation results')
            
            # Output results
            self.output_results(results, options)
            
            # Print summary to console
            self.print_summary(results)
            
        except Exception as e:
            raise CommandError(f'Error during stock validation: {str(e)}')
    
    def get_product_ids(self, options):
        """Parse product IDs from command line options"""
        product_ids_str = options.get('product_ids')
        if product_ids_str:
            try:
                product_ids = [int(pid.strip()) for pid in product_ids_str.split(',')]
                self.stdout.write(f'Validating {len(product_ids)} specific products')
                return product_ids
            except ValueError:
                raise CommandError('Invalid product IDs format. Use comma-separated integers')
        return None
    
    def output_results(self, results, options):
        """Output results in the specified format"""
        output_format = options['output_format']
        
        if output_format == 'console':
            self.output_console(results, options)
        elif output_format in ['csv', 'json']:
            if not options.get('output_file'):
                raise CommandError(f'{output_format.upper()} format requires --output-file parameter')
            
            if output_format == 'csv':
                self.output_csv(results, options['output_file'], options)
            else:
                self.output_json(results, options['output_file'])
    
    def output_console(self, results, options):
        """Output results to console"""
        threshold = Decimal(str(options['threshold']))
        show_correct = options['show_correct']
        
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('STOCK VALIDATION RESULTS'))
        self.stdout.write('='*80)
        
        # Show discrepancies
        if results['discrepancies']:
            self.stdout.write('\n' + self.style.WARNING('PRODUCTS WITH STOCK DISCREPANCIES:'))
            self.stdout.write('-'*80)
            
            for discrepancy in results['discrepancies']:
                if discrepancy.get('error'):
                    self.stdout.write(
                        self.style.ERROR(
                            f"Product {discrepancy['produto_codigo']}: ERROR - {discrepancy['error']}"
                        )
                    )
                else:
                    diff = discrepancy.get('difference', 0)
                    if abs(diff) >= float(threshold):
                        style = self.style.ERROR if abs(diff) > 1 else self.style.WARNING
                        self.stdout.write(
                            style(
                                f"Product {discrepancy['produto_codigo']} ({discrepancy['produto_nome']}): "
                                f"Stored={discrepancy['stored_stock']:.2f}, "
                                f"Calculated={discrepancy['calculated_stock']:.2f}, "
                                f"Difference={diff:+.2f}"
                            )
                        )
        
        # Show correct products if requested
        if show_correct and results['correct_stock'] > 0:
            self.stdout.write('\n' + self.style.SUCCESS('PRODUCTS WITH CORRECT STOCK:'))
            self.stdout.write('-'*80)
            
            # We need to get the correct products separately since they're not in discrepancies
            product_ids = self.get_product_ids({'product_ids': options.get('product_ids')})
            if product_ids:
                produtos = Produtos.objects.filter(id__in=product_ids, ativo=True)
            else:
                produtos = Produtos.objects.filter(ativo=True)
            
            correct_count = 0
            for produto in produtos:
                if correct_count >= results['correct_stock']:
                    break
                    
                # Check if this product is in discrepancies
                is_discrepancy = any(
                    d['produto_id'] == produto.id for d in results['discrepancies']
                )
                
                if not is_discrepancy:
                    try:
                        calculated_stock = StockValidationService.validate_single_product(produto.id)
                        if calculated_stock['is_correct']:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Product {produto.codigo} ({produto.nome}): "
                                    f"Stock={calculated_stock['stored_stock']:.2f} ✓"
                                )
                            )
                            correct_count += 1
                    except Exception:
                        continue  # Skip products with validation errors
        
        # Show detailed analysis if available
        if 'analysis' in results:
            self.stdout.write('\n' + self.style.SUCCESS('DETAILED ANALYSIS:'))
            self.stdout.write('-'*80)
            analysis = results['analysis']
            
            self.stdout.write(f"Products with zero calculated stock: {analysis['products_with_zero_calculated']}")
            self.stdout.write(f"Products with zero stored stock: {analysis['products_with_zero_stored']}")
            self.stdout.write(f"Products with negative calculated stock: {analysis['products_with_negative_calculated']}")
            self.stdout.write(f"Products with negative stored stock: {analysis['products_with_negative_stored']}")
            self.stdout.write(f"Average difference: {analysis['average_difference']:.3f}")
            self.stdout.write(f"Median difference: {analysis['median_difference']:.3f}")
            
            if results.get('recommendations'):
                self.stdout.write('\n' + self.style.WARNING('RECOMMENDATIONS:'))
                for i, recommendation in enumerate(results['recommendations'], 1):
                    self.stdout.write(f"{i}. {recommendation}")
    
    def output_csv(self, results, filename, options):
        """Output results to CSV file"""
        filepath = Path(filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'produto_id', 'produto_codigo', 'produto_nome',
                'calculated_stock', 'stored_stock', 'difference',
                'abs_difference', 'percentage_diff', 'status'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write discrepancies
            for discrepancy in results['discrepancies']:
                row = {
                    'produto_id': discrepancy['produto_id'],
                    'produto_codigo': discrepancy['produto_codigo'],
                    'produto_nome': discrepancy['produto_nome'],
                    'calculated_stock': discrepancy.get('calculated_stock'),
                    'stored_stock': discrepancy.get('stored_stock'),
                    'difference': discrepancy.get('difference'),
                    'abs_difference': abs(discrepancy.get('difference', 0)) if discrepancy.get('difference') is not None else None,
                    'percentage_diff': discrepancy.get('percentage_diff'),
                    'status': 'ERROR' if discrepancy.get('error') else 'DISCREPANCY'
                }
                writer.writerow(row)
            
            # Write correct products if requested
            if options['show_correct']:
                product_ids = self.get_product_ids(options)
                if product_ids:
                    produtos = Produtos.objects.filter(id__in=product_ids, ativo=True)
                else:
                    produtos = Produtos.objects.filter(ativo=True)
                
                for produto in produtos:
                    # Check if this product is in discrepancies
                    is_discrepancy = any(
                        d['produto_id'] == produto.id for d in results['discrepancies']
                    )
                    
                    if not is_discrepancy:
                        try:
                            validation = StockValidationService.validate_single_product(produto.id)
                            if validation['is_correct']:
                                row = {
                                    'produto_id': produto.id,
                                    'produto_codigo': produto.codigo,
                                    'produto_nome': produto.nome,
                                    'calculated_stock': validation['calculated_stock'],
                                    'stored_stock': validation['stored_stock'],
                                    'difference': 0,
                                    'abs_difference': 0,
                                    'percentage_diff': 0,
                                    'status': 'CORRECT'
                                }
                                writer.writerow(row)
                        except Exception:
                            continue  # Skip products with validation errors
        
        self.stdout.write(f'Results saved to {filepath}')
    
    def output_json(self, results, filename):
        """Output results to JSON file"""
        filepath = Path(filename)
        
        # Add metadata
        output_data = {
            'validation_metadata': {
                'generated_at': timezone.now().isoformat(),
                'command': 'validate_stock',
                'total_products_validated': results['total_products']
            },
            'validation_results': results
        }
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(output_data, jsonfile, indent=2, ensure_ascii=False)
        
        self.stdout.write(f'Results saved to {filepath}')
    
    def print_summary(self, results):
        """Print validation summary to console"""
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('VALIDATION SUMMARY'))
        self.stdout.write('='*80)
        
        total = results['total_products']
        correct = results['correct_stock']
        incorrect = results['incorrect_stock']
        accuracy = results['summary']['accuracy_percentage']
        
        self.stdout.write(f'Total products validated: {total}')
        self.stdout.write(
            self.style.SUCCESS(f'Products with correct stock: {correct}')
        )
        self.stdout.write(
            self.style.WARNING(f'Products with incorrect stock: {incorrect}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Stock accuracy: {accuracy:.2f}%')
        )
        
        if results['summary']['total_discrepancies'] > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Total discrepancies found: {results['summary']['total_discrepancies']}"
                )
            )
            self.stdout.write(
                f"Largest positive difference: {results['summary']['largest_positive_diff']:.3f}"
            )
            self.stdout.write(
                f"Largest negative difference: {results['summary']['largest_negative_diff']:.3f}"
            )
        
        # Performance info
        validation_time = results.get('validation_date', timezone.now().isoformat())
        self.stdout.write(f'Validation completed at: {validation_time}')
        
        self.stdout.write('\n' + '='*80)