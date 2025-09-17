"""
Django management command for historical stock analysis and reporting.

This command provides comprehensive historical stock analysis capabilities
including stock calculations at specific dates, movement analysis, and
reporting for audit and business intelligence purposes.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from datetime import date, datetime, timedelta
from decimal import Decimal
import csv
import json
import os

from contas.models.access import Produtos, MovimentacoesEstoque
from contas.services.stock_calculation import StockCalculationService


class Command(BaseCommand):
    help = 'Analyze historical stock levels and generate reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['calculate', 'timeline', 'movements', 'resets', 'report'],
            required=True,
            help='Type of analysis to perform'
        )
        
        parser.add_argument(
            '--produto-id',
            type=int,
            help='Specific product ID to analyze'
        )
        
        parser.add_argument(
            '--produto-codes',
            type=str,
            help='Comma-separated list of product codes to analyze'
        )
        
        parser.add_argument(
            '--date',
            type=str,
            help='Target date for stock calculation (YYYY-MM-DD)'
        )
        
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date for period analysis (YYYY-MM-DD)'
        )
        
        parser.add_argument(
            '--end-date',
            type=str,
            help='End date for period analysis (YYYY-MM-DD)'
        )
        
        parser.add_argument(
            '--output-format',
            type=str,
            choices=['console', 'csv', 'json'],
            default='console',
            help='Output format for results'
        )
        
        parser.add_argument(
            '--output-file',
            type=str,
            help='Output file path (required for csv/json formats)'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of products to analyze'
        )
        
        parser.add_argument(
            '--interval',
            type=str,
            choices=['daily', 'weekly', 'monthly'],
            default='daily',
            help='Interval for timeline analysis'
        )

    def handle(self, *args, **options):
        try:
            action = options['action']
            
            if action == 'calculate':
                self.handle_calculate(options)
            elif action == 'timeline':
                self.handle_timeline(options)
            elif action == 'movements':
                self.handle_movements(options)
            elif action == 'resets':
                self.handle_resets(options)
            elif action == 'report':
                self.handle_report(options)
                
        except Exception as e:
            raise CommandError(f'Error during analysis: {str(e)}')

    def handle_calculate(self, options):
        """Calculate historical stock for specific products and date"""
        target_date = self.parse_date(options.get('date'))
        if not target_date:
            raise CommandError('--date is required for calculate action')
        
        if target_date > date.today():
            raise CommandError('Cannot calculate stock for future dates')
        
        produtos = self.get_products(options)
        if not produtos:
            raise CommandError('No products found to analyze')
        
        self.stdout.write(f"\nCalculating historical stock for {target_date}")
        self.stdout.write("=" * 60)
        
        results = []
        for produto in produtos:
            try:
                historical_stock = StockCalculationService.calculate_stock_at_date(
                    produto.id, target_date
                )
                
                # Get stock reset info
                base_stock, reset_date = StockCalculationService.get_base_stock_reset(
                    produto.id, datetime.combine(target_date, datetime.max.time())
                )
                
                result = {
                    'produto_id': produto.id,
                    'produto_code': produto.codigo,
                    'produto_name': produto.nome,
                    'target_date': target_date.strftime('%Y-%m-%d'),
                    'historical_stock': float(historical_stock),
                    'current_stock': float(produto.estoque_atual or 0),
                    'has_reset': reset_date is not None,
                    'reset_date': reset_date.isoformat() if reset_date else None,
                    'reset_quantity': float(base_stock) if reset_date else None
                }
                
                results.append(result)
                
                if options['output_format'] == 'console':
                    self.stdout.write(
                        f"{produto.codigo:15} {produto.nome[:40]:40} "
                        f"{historical_stock:>10} {produto.estoque_atual or 0:>10} "
                        f"{'✓' if reset_date else '✗':>5}"
                    )
                    
            except Exception as e:
                self.stderr.write(f"Error calculating stock for {produto.codigo}: {str(e)}")
        
        self.output_results(results, options, 'historical_stock_calculation')

    def handle_timeline(self, options):
        """Generate stock timeline for a product"""
        produto_id = options.get('produto_id')
        if not produto_id:
            raise CommandError('--produto-id is required for timeline action')
        
        start_date = self.parse_date(options.get('start_date'))
        end_date = self.parse_date(options.get('end_date'))
        
        if not start_date or not end_date:
            raise CommandError('--start-date and --end-date are required for timeline action')
        
        if start_date > end_date:
            raise CommandError('start-date must be before end-date')
        
        try:
            produto = Produtos.objects.get(id=produto_id)
        except Produtos.DoesNotExist:
            raise CommandError(f'Product with ID {produto_id} not found')
        
        interval = options.get('interval', 'daily')
        
        self.stdout.write(f"\nGenerating stock timeline for {produto.codigo} - {produto.nome}")
        self.stdout.write(f"Period: {start_date} to {end_date} ({interval})")
        self.stdout.write("=" * 60)
        
        # Generate timeline points
        timeline_points = []
        current_date = start_date
        
        if interval == 'daily':
            delta = timedelta(days=1)
        elif interval == 'weekly':
            delta = timedelta(weeks=1)
        else:  # monthly
            delta = timedelta(days=30)
        
        while current_date <= end_date:
            try:
                stock_level = StockCalculationService.calculate_stock_at_date(produto_id, current_date)
                timeline_points.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'stock_level': float(stock_level)
                })
                
                if options['output_format'] == 'console':
                    self.stdout.write(f"{current_date.strftime('%Y-%m-%d'):12} {stock_level:>10}")
                    
            except Exception as e:
                self.stderr.write(f"Error calculating stock for {current_date}: {str(e)}")
            
            current_date += delta
        
        self.output_results(timeline_points, options, 'stock_timeline')

    def handle_movements(self, options):
        """Analyze stock movements over a period"""
        start_date = self.parse_date(options.get('start_date'))
        end_date = self.parse_date(options.get('end_date'))
        
        if not start_date or not end_date:
            raise CommandError('--start-date and --end-date are required for movements action')
        
        produtos = self.get_products(options)
        if not produtos:
            raise CommandError('No products found to analyze')
        
        self.stdout.write(f"\nAnalyzing stock movements from {start_date} to {end_date}")
        self.stdout.write("=" * 80)
        
        results = []
        for produto in produtos:
            try:
                movement_summary = StockCalculationService.get_stock_movements_summary(
                    produto.id, start_date, end_date
                )
                
                stock_at_start = StockCalculationService.calculate_stock_at_date(produto.id, start_date)
                stock_at_end = StockCalculationService.calculate_stock_at_date(produto.id, end_date)
                
                result = {
                    'produto_id': produto.id,
                    'produto_code': produto.codigo,
                    'produto_name': produto.nome,
                    'period_start': start_date.strftime('%Y-%m-%d'),
                    'period_end': end_date.strftime('%Y-%m-%d'),
                    'stock_at_start': float(stock_at_start),
                    'stock_at_end': float(stock_at_end),
                    'net_change': float(stock_at_end - stock_at_start),
                    'total_movements': len(movement_summary['stock_resets']) + len(movement_summary['regular_movements']),
                    'regular_movements': len(movement_summary['regular_movements']),
                    'stock_resets': len(movement_summary['stock_resets']),
                    'entrada_total': float(movement_summary['totals']['entrada']),
                    'saida_total': float(movement_summary['totals']['saida']),
                    'net_movement': float(movement_summary['totals']['net_movement'])
                }
                
                results.append(result)
                
                if options['output_format'] == 'console':
                    self.stdout.write(
                        f"{produto.codigo:15} {stock_at_start:>8} {stock_at_end:>8} "
                        f"{stock_at_end - stock_at_start:>8} {len(movement_summary['regular_movements']):>6} "
                        f"{movement_summary['totals']['entrada']:>8} {movement_summary['totals']['saida']:>8}"
                    )
                    
            except Exception as e:
                self.stderr.write(f"Error analyzing movements for {produto.codigo}: {str(e)}")
        
        self.output_results(results, options, 'movement_analysis')

    def handle_resets(self, options):
        """Analyze stock resets (000000 movements)"""
        start_date = self.parse_date(options.get('start_date'))
        end_date = self.parse_date(options.get('end_date'))
        
        self.stdout.write("\nAnalyzing stock resets (000000 movements)")
        if start_date and end_date:
            self.stdout.write(f"Period: {start_date} to {end_date}")
        self.stdout.write("=" * 60)
        
        # Build query for resets
        reset_query = MovimentacoesEstoque.objects.filter(
            documento_referencia='000000'
        ).select_related('produto', 'tipo_movimentacao')
        
        if start_date:
            reset_query = reset_query.filter(data_movimentacao__date__gte=start_date)
        if end_date:
            reset_query = reset_query.filter(data_movimentacao__date__lte=end_date)
        
        # Get specific products if requested
        produtos = self.get_products(options)
        if produtos:
            produto_ids = [p.id for p in produtos]
            reset_query = reset_query.filter(produto_id__in=produto_ids)
        
        resets = reset_query.order_by('-data_movimentacao')
        
        results = []
        for reset in resets:
            result = {
                'produto_id': reset.produto.id,
                'produto_code': reset.produto.codigo,
                'produto_name': reset.produto.nome,
                'reset_date': reset.data_movimentacao.date().strftime('%Y-%m-%d'),
                'reset_quantity': float(reset.quantidade),
                'movement_type': reset.tipo_movimentacao.descricao if reset.tipo_movimentacao else 'N/A'
            }
            
            results.append(result)
            
            if options['output_format'] == 'console':
                self.stdout.write(
                    f"{reset.produto.codigo:15} {reset.data_movimentacao.date().strftime('%Y-%m-%d'):12} "
                    f"{reset.quantidade:>10} {reset.tipo_movimentacao.descricao if reset.tipo_movimentacao else 'N/A'}"
                )
        
        if options['output_format'] == 'console':
            self.stdout.write(f"\nTotal resets found: {len(results)}")
        
        self.output_results(results, options, 'stock_resets')

    def handle_report(self, options):
        """Generate comprehensive historical stock report"""
        produtos = self.get_products(options)
        if not produtos:
            raise CommandError('No products found to analyze')
        
        target_date = self.parse_date(options.get('date', date.today().strftime('%Y-%m-%d')))
        
        self.stdout.write(f"\nGenerating comprehensive stock report for {target_date}")
        self.stdout.write("=" * 80)
        
        report_data = {
            'report_date': target_date.strftime('%Y-%m-%d'),
            'generated_at': datetime.now().isoformat(),
            'products_analyzed': len(produtos),
            'products': []
        }
        
        for produto in produtos:
            try:
                # Calculate historical stock
                historical_stock = StockCalculationService.calculate_stock_at_date(produto.id, target_date)
                
                # Get stock reset info
                base_stock, reset_date = StockCalculationService.get_base_stock_reset(
                    produto.id, datetime.combine(target_date, datetime.max.time())
                )
                
                # Get recent movements (last 30 days)
                movement_summary = StockCalculationService.get_stock_movements_summary(
                    produto.id, target_date - timedelta(days=30), target_date
                )
                
                product_data = {
                    'produto_id': produto.id,
                    'codigo': produto.codigo,
                    'nome': produto.nome,
                    'current_stock': float(produto.estoque_atual or 0),
                    'historical_stock': float(historical_stock),
                    'stock_reset_info': {
                        'has_reset': reset_date is not None,
                        'reset_date': reset_date.isoformat() if reset_date else None,
                        'reset_quantity': float(base_stock) if reset_date else None
                    },
                    'recent_activity': {
                        'total_movements': len(movement_summary['stock_resets']) + len(movement_summary['regular_movements']),
                        'entrada_total': float(movement_summary['totals']['entrada']),
                        'saida_total': float(movement_summary['totals']['saida']),
                        'net_movement': float(movement_summary['totals']['net_movement'])
                    }
                }
                
                report_data['products'].append(product_data)
                
                if options['output_format'] == 'console':
                    self.stdout.write(
                        f"{produto.codigo:15} {produto.nome[:30]:30} "
                        f"{historical_stock:>10} {produto.estoque_atual or 0:>10} "
                        f"{len(movement_summary['regular_movements']):>6}"
                    )
                    
            except Exception as e:
                self.stderr.write(f"Error generating report for {produto.codigo}: {str(e)}")
        
        self.output_results(report_data, options, 'comprehensive_report')

    def get_products(self, options):
        """Get products based on command options"""
        produto_id = options.get('produto_id')
        produto_codes = options.get('produto_codes')
        limit = options.get('limit', 100)
        
        if produto_id:
            try:
                return [Produtos.objects.get(id=produto_id)]
            except Produtos.DoesNotExist:
                raise CommandError(f'Product with ID {produto_id} not found')
        
        elif produto_codes:
            codes = [code.strip() for code in produto_codes.split(',')]
            produtos = Produtos.objects.filter(codigo__in=codes, ativo=True)
            if not produtos.exists():
                raise CommandError(f'No products found with codes: {produto_codes}')
            return list(produtos)
        
        else:
            # Return sample of active products
            return list(Produtos.objects.filter(ativo=True)[:limit])

    def parse_date(self, date_str):
        """Parse date string to date object"""
        if not date_str:
            return None
        
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise CommandError(f'Invalid date format: {date_str}. Use YYYY-MM-DD')

    def output_results(self, results, options, report_type):
        """Output results in the specified format"""
        output_format = options.get('output_format', 'console')
        output_file = options.get('output_file')
        
        if output_format == 'csv':
            if not output_file:
                raise CommandError('--output-file is required for CSV format')
            self.write_csv(results, output_file, report_type)
            self.stdout.write(f"Results written to {output_file}")
            
        elif output_format == 'json':
            if not output_file:
                raise CommandError('--output-file is required for JSON format')
            self.write_json(results, output_file)
            self.stdout.write(f"Results written to {output_file}")
            
        # Console output is handled in individual methods

    def write_csv(self, results, output_file, report_type):
        """Write results to CSV file"""
        if not results:
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            if isinstance(results[0], dict):
                fieldnames = results[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)

    def write_json(self, results, output_file):
        """Write results to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(results, jsonfile, indent=2, ensure_ascii=False, default=str)