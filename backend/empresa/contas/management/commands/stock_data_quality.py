"""
Django management command for stock data quality analysis.

This command analyzes the quality of stock movement data, identifies
potential issues, and provides recommendations for data improvement.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Q, Min, Max
from datetime import date, datetime, timedelta
from decimal import Decimal
import csv
import json

from contas.models.access import (
    Produtos, MovimentacoesEstoque, TiposMovimentacaoEstoque
)


class Command(BaseCommand):
    help = 'Analyze stock data quality and identify potential issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['overview', 'movements', 'resets', 'orphaned', 'duplicates', 'report'],
            required=True,
            help='Type of data quality analysis to perform'
        )
        
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date for analysis (YYYY-MM-DD)'
        )
        
        parser.add_argument(
            '--end-date',
            type=str,
            help='End date for analysis (YYYY-MM-DD)'
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
            help='Maximum number of records to analyze'
        )

    def handle(self, *args, **options):
        try:
            action = options['action']
            
            if action == 'overview':
                self.handle_overview(options)
            elif action == 'movements':
                self.handle_movements(options)
            elif action == 'resets':
                self.handle_resets(options)
            elif action == 'orphaned':
                self.handle_orphaned(options)
            elif action == 'duplicates':
                self.handle_duplicates(options)
            elif action == 'report':
                self.handle_report(options)
                
        except Exception as e:
            raise CommandError(f'Error during data quality analysis: {str(e)}')

    def handle_overview(self, options):
        """Provide overview of stock data quality"""
        self.stdout.write("\nStock Data Quality Overview")
        self.stdout.write("=" * 50)
        
        # Basic statistics
        total_products = Produtos.objects.filter(ativo=True).count()
        total_movements = MovimentacoesEstoque.objects.count()
        total_resets = MovimentacoesEstoque.objects.filter(documento_referencia='000000').count()
        
        # Movement types
        movement_types = TiposMovimentacaoEstoque.objects.filter(ativo=True).count()
        
        # Date ranges
        movement_dates = MovimentacoesEstoque.objects.aggregate(
            min_date=Min('data_movimentacao'),
            max_date=Max('data_movimentacao')
        )
        
        # Products with movements
        products_with_movements = MovimentacoesEstoque.objects.values('produto').distinct().count()
        products_without_movements = total_products - products_with_movements
        
        # Products with resets
        products_with_resets = MovimentacoesEstoque.objects.filter(
            documento_referencia='000000'
        ).values('produto').distinct().count()
        
        overview_data = {
            'total_active_products': total_products,
            'total_movements': total_movements,
            'total_stock_resets': total_resets,
            'regular_movements': total_movements - total_resets,
            'movement_types_available': movement_types,
            'products_with_movements': products_with_movements,
            'products_without_movements': products_without_movements,
            'products_with_resets': products_with_resets,
            'movement_date_range': {
                'earliest': movement_dates['min_date'].date() if movement_dates['min_date'] else None,
                'latest': movement_dates['max_date'].date() if movement_dates['max_date'] else None
            }
        }
        
        if options['output_format'] == 'console':
            self.stdout.write(f"Total Active Products: {total_products:,}")
            self.stdout.write(f"Total Stock Movements: {total_movements:,}")
            self.stdout.write(f"  - Stock Resets (000000): {total_resets:,}")
            self.stdout.write(f"  - Regular Movements: {total_movements - total_resets:,}")
            self.stdout.write(f"Movement Types Available: {movement_types}")
            self.stdout.write(f"Products with Movements: {products_with_movements:,}")
            self.stdout.write(f"Products without Movements: {products_without_movements:,}")
            self.stdout.write(f"Products with Stock Resets: {products_with_resets:,}")
            
            if movement_dates['min_date'] and movement_dates['max_date']:
                self.stdout.write(f"Movement Date Range: {movement_dates['min_date'].date()} to {movement_dates['max_date'].date()}")
        
        self.output_results(overview_data, options, 'data_quality_overview')

    def handle_movements(self, options):
        """Analyze movement data quality issues"""
        self.stdout.write("\nMovement Data Quality Analysis")
        self.stdout.write("=" * 40)
        
        start_date = self.parse_date(options.get('start_date'))
        end_date = self.parse_date(options.get('end_date'))
        
        # Build base query
        movements_query = MovimentacoesEstoque.objects.all()
        
        if start_date:
            movements_query = movements_query.filter(data_movimentacao__date__gte=start_date)
        if end_date:
            movements_query = movements_query.filter(data_movimentacao__date__lte=end_date)
        
        # Analyze various data quality issues
        issues = []
        
        # 1. Movements without tipo_movimentacao
        movements_without_type = movements_query.filter(tipo_movimentacao__isnull=True).count()
        if movements_without_type > 0:
            issues.append({
                'issue_type': 'missing_movement_type',
                'count': movements_without_type,
                'description': 'Movements without tipo_movimentacao',
                'severity': 'high'
            })
        
        # 2. Movements with zero quantity
        zero_quantity_movements = movements_query.filter(quantidade=0).count()
        if zero_quantity_movements > 0:
            issues.append({
                'issue_type': 'zero_quantity',
                'count': zero_quantity_movements,
                'description': 'Movements with zero quantity',
                'severity': 'medium'
            })
        
        # 3. Movements with negative quantity
        negative_quantity_movements = movements_query.filter(quantidade__lt=0).count()
        if negative_quantity_movements > 0:
            issues.append({
                'issue_type': 'negative_quantity',
                'count': negative_quantity_movements,
                'description': 'Movements with negative quantity',
                'severity': 'high'
            })
        
        # 4. Movements without document reference
        no_document_movements = movements_query.filter(
            Q(documento_referencia__isnull=True) | Q(documento_referencia='')
        ).count()
        if no_document_movements > 0:
            issues.append({
                'issue_type': 'missing_document',
                'count': no_document_movements,
                'description': 'Movements without document reference',
                'severity': 'low'
            })
        
        # 5. Future dated movements
        future_movements = movements_query.filter(data_movimentacao__date__gt=date.today()).count()
        if future_movements > 0:
            issues.append({
                'issue_type': 'future_dated',
                'count': future_movements,
                'description': 'Movements dated in the future',
                'severity': 'high'
            })
        
        # 6. Movements with inconsistent value calculations
        inconsistent_value_movements = movements_query.filter(
            ~Q(valor_total=0),
            ~Q(custo_unitario=0)
        ).exclude(
            valor_total=models.F('quantidade') * models.F('custo_unitario')
        ).count()
        
        if inconsistent_value_movements > 0:
            issues.append({
                'issue_type': 'inconsistent_values',
                'count': inconsistent_value_movements,
                'description': 'Movements where valor_total ≠ quantidade × custo_unitario',
                'severity': 'medium'
            })
        
        analysis_result = {
            'analysis_period': {
                'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                'end_date': end_date.strftime('%Y-%m-%d') if end_date else None
            },
            'total_movements_analyzed': movements_query.count(),
            'issues_found': len(issues),
            'issues': issues
        }
        
        if options['output_format'] == 'console':
            self.stdout.write(f"Total movements analyzed: {movements_query.count():,}")
            self.stdout.write(f"Issues found: {len(issues)}")
            self.stdout.write("")
            
            for issue in issues:
                severity_icon = "🔴" if issue['severity'] == 'high' else "🟡" if issue['severity'] == 'medium' else "🟢"
                self.stdout.write(f"{severity_icon} {issue['description']}: {issue['count']:,}")
        
        self.output_results(analysis_result, options, 'movement_quality_analysis')

    def handle_resets(self, options):
        """Analyze stock reset data quality"""
        self.stdout.write("\nStock Reset Data Quality Analysis")
        self.stdout.write("=" * 40)
        
        start_date = self.parse_date(options.get('start_date'))
        end_date = self.parse_date(options.get('end_date'))
        
        # Build query for resets
        resets_query = MovimentacoesEstoque.objects.filter(documento_referencia='000000')
        
        if start_date:
            resets_query = resets_query.filter(data_movimentacao__date__gte=start_date)
        if end_date:
            resets_query = resets_query.filter(data_movimentacao__date__lte=end_date)
        
        # Analyze reset patterns
        total_resets = resets_query.count()
        
        # Products with multiple resets
        products_with_multiple_resets = resets_query.values('produto').annotate(
            reset_count=Count('id')
        ).filter(reset_count__gt=1)
        
        # Resets with zero quantity
        zero_quantity_resets = resets_query.filter(quantidade=0).count()
        
        # Resets with negative quantity
        negative_quantity_resets = resets_query.filter(quantidade__lt=0).count()
        
        # Recent resets (last 30 days)
        recent_resets = resets_query.filter(
            data_movimentacao__date__gte=date.today() - timedelta(days=30)
        ).count()
        
        reset_analysis = {
            'analysis_period': {
                'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                'end_date': end_date.strftime('%Y-%m-%d') if end_date else None
            },
            'total_resets': total_resets,
            'products_with_multiple_resets': products_with_multiple_resets.count(),
            'zero_quantity_resets': zero_quantity_resets,
            'negative_quantity_resets': negative_quantity_resets,
            'recent_resets': recent_resets,
            'multiple_reset_details': list(products_with_multiple_resets.values(
                'produto__codigo', 'produto__nome', 'reset_count'
            ))
        }
        
        if options['output_format'] == 'console':
            self.stdout.write(f"Total stock resets: {total_resets:,}")
            self.stdout.write(f"Products with multiple resets: {products_with_multiple_resets.count()}")
            self.stdout.write(f"Zero quantity resets: {zero_quantity_resets}")
            self.stdout.write(f"Negative quantity resets: {negative_quantity_resets}")
            self.stdout.write(f"Recent resets (30 days): {recent_resets}")
            
            if products_with_multiple_resets.exists():
                self.stdout.write("\nProducts with multiple resets:")
                for item in products_with_multiple_resets[:10]:  # Show first 10
                    self.stdout.write(
                        f"  {item['produto__codigo']}: {item['reset_count']} resets"
                    )
        
        self.output_results(reset_analysis, options, 'reset_quality_analysis')

    def handle_orphaned(self, options):
        """Find orphaned records and data integrity issues"""
        self.stdout.write("\nOrphaned Records Analysis")
        self.stdout.write("=" * 30)
        
        # Movements with non-existent products
        orphaned_movements = MovimentacoesEstoque.objects.filter(produto__isnull=True).count()
        
        # Movements with inactive movement types
        movements_with_inactive_types = MovimentacoesEstoque.objects.filter(
            tipo_movimentacao__ativo=False
        ).count()
        
        # Products without any movements
        products_without_movements = Produtos.objects.filter(ativo=True).exclude(
            id__in=MovimentacoesEstoque.objects.values('produto_id')
        ).count()
        
        orphaned_analysis = {
            'orphaned_movements': orphaned_movements,
            'movements_with_inactive_types': movements_with_inactive_types,
            'products_without_movements': products_without_movements
        }
        
        if options['output_format'] == 'console':
            self.stdout.write(f"Movements with missing products: {orphaned_movements}")
            self.stdout.write(f"Movements with inactive types: {movements_with_inactive_types}")
            self.stdout.write(f"Products without movements: {products_without_movements}")
        
        self.output_results(orphaned_analysis, options, 'orphaned_records_analysis')

    def handle_duplicates(self, options):
        """Find potential duplicate movements"""
        self.stdout.write("\nDuplicate Movement Analysis")
        self.stdout.write("=" * 30)
        
        # Find potential duplicates based on same product, date, quantity, and document
        duplicates = MovimentacoesEstoque.objects.values(
            'produto', 'data_movimentacao__date', 'quantidade', 'documento_referencia'
        ).annotate(
            count=Count('id')
        ).filter(count__gt=1).order_by('-count')
        
        duplicate_analysis = {
            'potential_duplicate_groups': duplicates.count(),
            'duplicate_details': list(duplicates[:20])  # Show first 20 groups
        }
        
        if options['output_format'] == 'console':
            self.stdout.write(f"Potential duplicate groups: {duplicates.count()}")
            
            if duplicates.exists():
                self.stdout.write("\nTop duplicate groups:")
                for dup in duplicates[:10]:
                    self.stdout.write(
                        f"  Product {dup['produto']}, Date {dup['data_movimentacao__date']}, "
                        f"Qty {dup['quantidade']}, Doc {dup['documento_referencia']}: "
                        f"{dup['count']} records"
                    )
        
        self.output_results(duplicate_analysis, options, 'duplicate_analysis')

    def handle_report(self, options):
        """Generate comprehensive data quality report"""
        self.stdout.write("\nComprehensive Data Quality Report")
        self.stdout.write("=" * 40)
        
        # Run all analyses
        overview = self.get_overview_data()
        movement_issues = self.get_movement_issues()
        reset_issues = self.get_reset_issues()
        orphaned_issues = self.get_orphaned_issues()
        
        # Calculate overall quality score
        total_movements = overview['total_movements']
        total_issues = sum([
            len(movement_issues),
            reset_issues.get('zero_quantity_resets', 0),
            reset_issues.get('negative_quantity_resets', 0),
            orphaned_issues.get('orphaned_movements', 0)
        ])
        
        quality_score = max(0, 100 - (total_issues / max(total_movements, 1)) * 100)
        
        comprehensive_report = {
            'report_generated_at': datetime.now().isoformat(),
            'overall_quality_score': round(quality_score, 2),
            'overview': overview,
            'movement_issues': movement_issues,
            'reset_analysis': reset_issues,
            'orphaned_records': orphaned_issues,
            'recommendations': self.generate_recommendations(
                movement_issues, reset_issues, orphaned_issues
            )
        }
        
        if options['output_format'] == 'console':
            self.stdout.write(f"Overall Data Quality Score: {quality_score:.1f}/100")
            self.stdout.write(f"Total Issues Found: {total_issues}")
            
            if comprehensive_report['recommendations']:
                self.stdout.write("\nRecommendations:")
                for i, rec in enumerate(comprehensive_report['recommendations'], 1):
                    self.stdout.write(f"{i}. {rec}")
        
        self.output_results(comprehensive_report, options, 'comprehensive_quality_report')

    def get_overview_data(self):
        """Get overview data for reporting"""
        total_products = Produtos.objects.filter(ativo=True).count()
        total_movements = MovimentacoesEstoque.objects.count()
        total_resets = MovimentacoesEstoque.objects.filter(documento_referencia='000000').count()
        
        return {
            'total_active_products': total_products,
            'total_movements': total_movements,
            'total_stock_resets': total_resets,
            'regular_movements': total_movements - total_resets
        }

    def get_movement_issues(self):
        """Get movement data quality issues"""
        issues = []
        
        movements_without_type = MovimentacoesEstoque.objects.filter(tipo_movimentacao__isnull=True).count()
        if movements_without_type > 0:
            issues.append({'type': 'missing_movement_type', 'count': movements_without_type})
        
        zero_quantity = MovimentacoesEstoque.objects.filter(quantidade=0).count()
        if zero_quantity > 0:
            issues.append({'type': 'zero_quantity', 'count': zero_quantity})
        
        negative_quantity = MovimentacoesEstoque.objects.filter(quantidade__lt=0).count()
        if negative_quantity > 0:
            issues.append({'type': 'negative_quantity', 'count': negative_quantity})
        
        return issues

    def get_reset_issues(self):
        """Get stock reset issues"""
        return {
            'zero_quantity_resets': MovimentacoesEstoque.objects.filter(
                documento_referencia='000000', quantidade=0
            ).count(),
            'negative_quantity_resets': MovimentacoesEstoque.objects.filter(
                documento_referencia='000000', quantidade__lt=0
            ).count()
        }

    def get_orphaned_issues(self):
        """Get orphaned record issues"""
        return {
            'orphaned_movements': MovimentacoesEstoque.objects.filter(produto__isnull=True).count(),
            'products_without_movements': Produtos.objects.filter(ativo=True).exclude(
                id__in=MovimentacoesEstoque.objects.values('produto_id')
            ).count()
        }

    def generate_recommendations(self, movement_issues, reset_issues, orphaned_issues):
        """Generate recommendations based on found issues"""
        recommendations = []
        
        if any(issue['type'] == 'missing_movement_type' for issue in movement_issues):
            recommendations.append(
                "Fix movements without tipo_movimentacao to ensure proper stock calculations"
            )
        
        if any(issue['type'] == 'negative_quantity' for issue in movement_issues):
            recommendations.append(
                "Review movements with negative quantities for data entry errors"
            )
        
        if reset_issues.get('zero_quantity_resets', 0) > 0:
            recommendations.append(
                "Review stock resets with zero quantity - these may be data entry errors"
            )
        
        if orphaned_issues.get('orphaned_movements', 0) > 0:
            recommendations.append(
                "Fix orphaned movements that reference non-existent products"
            )
        
        if orphaned_issues.get('products_without_movements', 0) > 100:
            recommendations.append(
                "Consider if products without any movements should be marked as inactive"
            )
        
        return recommendations

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
            self.write_csv(results, output_file)
            self.stdout.write(f"Results written to {output_file}")
            
        elif output_format == 'json':
            if not output_file:
                raise CommandError('--output-file is required for JSON format')
            self.write_json(results, output_file)
            self.stdout.write(f"Results written to {output_file}")

    def write_csv(self, results, output_file):
        """Write results to CSV file"""
        if isinstance(results, dict) and 'issues' in results:
            # Write issues to CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['issue_type', 'count', 'description', 'severity']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results['issues'])
        elif isinstance(results, list) and results:
            # Write list data to CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = results[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)

    def write_json(self, results, output_file):
        """Write results to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(results, jsonfile, indent=2, ensure_ascii=False, default=str)