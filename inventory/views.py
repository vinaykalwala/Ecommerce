from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from catalog.models import ProductVariant, Product
from .models import InventoryLog
from .forms import StockAdjustForm, InventoryLogForm

# ==================== INVENTORY MANAGEMENT VIEWS ====================

@staff_member_required
def inventory_dashboard(request):
    """Inventory dashboard with overview statistics"""
    total_variants = ProductVariant.objects.filter(is_active=True).count()
    total_stock = ProductVariant.objects.filter(is_active=True).aggregate(Sum('current_stock'))['current_stock__sum'] or 0
    
    # Stock status counts
    well_stocked = ProductVariant.objects.filter(current_stock__gt=50, is_active=True).count()
    low_stock = ProductVariant.objects.filter(current_stock__lte=10, current_stock__gt=0, is_active=True).count()
    out_of_stock = ProductVariant.objects.filter(current_stock=0, is_active=True).count()
    critical_stock = ProductVariant.objects.filter(current_stock__lte=5, current_stock__gt=0, is_active=True).count()
    
    # Recent inventory activities
    recent_activities = InventoryLog.objects.all().select_related('variant', 'variant__product')[:20]
    
    # Stock value calculation
    stock_value = 0
    for variant in ProductVariant.objects.filter(is_active=True):
        stock_value += variant.current_stock * variant.price
    
    # Low stock items
    low_stock_items = ProductVariant.objects.filter(
        current_stock__lte=10, 
        is_active=True
    ).select_related('product')[:10]
    
    # Top selling variants (based on inventory logs of order_placed)
    top_selling = InventoryLog.objects.filter(
        action='order_placed'
    ).values('variant__sku', 'variant__product__name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]
    
    context = {
        'total_variants': total_variants,
        'total_stock': total_stock,
        'well_stocked': well_stocked,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'critical_stock': critical_stock,
        'stock_value': stock_value,
        'recent_activities': recent_activities,
        'low_stock_items': low_stock_items,
        'top_selling': top_selling,
    }
    return render(request, 'inventory/dashboard.html', context)

@staff_member_required
def inventory_list_view(request):
    """List all inventory items (variants)"""
    variants = ProductVariant.objects.filter(is_active=True).select_related('product', 'product__category')
    
    # Filters
    search_query = request.GET.get('search')
    stock_status = request.GET.get('stock_status')
    category_id = request.GET.get('category')
    sort_by = request.GET.get('sort', 'product__name')
    
    if search_query:
        variants = variants.filter(
            Q(sku__icontains=search_query) |
            Q(product__name__icontains=search_query) |
            Q(product__category__name__icontains=search_query)
        )
    
    if stock_status:
        if stock_status == 'in_stock':
            variants = variants.filter(current_stock__gt=0)
        elif stock_status == 'low_stock':
            variants = variants.filter(current_stock__lte=10, current_stock__gt=0)
        elif stock_status == 'out_of_stock':
            variants = variants.filter(current_stock=0)
    
    if category_id:
        variants = variants.filter(product__category_id=category_id)
    
    # Sorting options
    sort_options = {
        'product__name': 'Product Name A-Z',
        '-product__name': 'Product Name Z-A',
        'sku': 'SKU A-Z',
        '-sku': 'SKU Z-A',
        'current_stock': 'Stock Low to High',
        '-current_stock': 'Stock High to Low',
        'price': 'Price Low to High',
        '-price': 'Price High to Low',
    }
    
    variants = variants.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(variants, 25)
    page = request.GET.get('page')
    variants_page = paginator.get_page(page)
    
    # Get categories for filter
    from catalog.models import Category
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'variants': variants_page,
        'search_query': search_query,
        'stock_status': stock_status,
        'selected_category': int(category_id) if category_id else None,
        'categories': categories,
        'sort_by': sort_by,
        'sort_options': sort_options,
    }
    return render(request, 'inventory/inventory_list.html', context)

@staff_member_required
def inventory_detail_view(request, variant_id):
    """View detailed inventory information for a specific variant"""
    variant = get_object_or_404(ProductVariant, id=variant_id, is_active=True)
    
    # Get inventory logs
    logs = variant.inventory_logs.all()[:50]
    
    # Get stock movement statistics
    last_7_days = timezone.now() - timedelta(days=7)
    last_30_days = timezone.now() - timedelta(days=30)
    
    stats = {
        'total_added': variant.inventory_logs.filter(action__in=['stock_added', 'stock_adjusted']).aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'total_removed': variant.inventory_logs.filter(action__in=['stock_removed', 'order_placed']).aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'sold_last_7_days': variant.inventory_logs.filter(action='order_placed', created_at__gte=last_7_days).aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'sold_last_30_days': variant.inventory_logs.filter(action='order_placed', created_at__gte=last_30_days).aggregate(Sum('quantity'))['quantity__sum'] or 0,
    }
    
    # Monthly sales chart data
    monthly_sales = []
    for i in range(6):
        month_start = timezone.now() - timedelta(days=30 * i)
        month_end = month_start + timedelta(days=30)
        sales = variant.inventory_logs.filter(
            action='order_placed',
            created_at__gte=month_start,
            created_at__lte=month_end
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0
        monthly_sales.append({
            'month': month_start.strftime('%B'),
            'sales': sales
        })
    
    context = {
        'variant': variant,
        'logs': logs,
        'stats': stats,
        'monthly_sales': monthly_sales,
    }
    return render(request, 'inventory/inventory_detail.html', context)

@staff_member_required
def inventory_adjust_view(request, variant_id):
    """Adjust inventory stock"""
    variant = get_object_or_404(ProductVariant, id=variant_id, is_active=True)
    
    if request.method == 'POST':
        form = StockAdjustForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            action_type = form.cleaned_data['action']
            remarks = form.cleaned_data['remarks']
            
            previous_stock = variant.current_stock
            
            with transaction.atomic():
                if action_type == 'add':
                    variant.current_stock += quantity
                    inventory_action = 'stock_added'
                    success_message = f'Successfully added {quantity} units. New stock: {variant.current_stock}'
                else:
                    if variant.current_stock >= quantity:
                        variant.current_stock -= quantity
                        inventory_action = 'stock_removed'
                        success_message = f'Successfully removed {quantity} units. New stock: {variant.current_stock}'
                    else:
                        messages.error(request, f'Cannot remove {quantity} units. Current stock: {variant.current_stock}')
                        return redirect('inventory:inventory_adjust', variant_id=variant_id)
                
                variant.save()
                
                InventoryLog.objects.create(
                    variant=variant,
                    quantity=quantity,
                    action=inventory_action,
                    remarks=remarks,
                    previous_stock=previous_stock,
                    new_stock=variant.current_stock
                )
            
            messages.success(request, success_message)
            
            # Redirect back to the referring page or inventory list
            next_url = request.POST.get('next', 'inventory:inventory_list')
            return redirect(next_url)
    else:
        form = StockAdjustForm()
    
    context = {
        'variant': variant,
        'form': form,
    }
    return render(request, 'inventory/inventory_adjust.html', context)

@staff_member_required
def bulk_inventory_update_view(request):
    """Bulk update inventory for multiple variants"""
    if request.method == 'POST':
        variant_ids = request.POST.getlist('variant_ids')
        action = request.POST.get('action')
        quantity = int(request.POST.get('quantity', 0))
        remarks = request.POST.get('remarks', '')
        
        if not variant_ids:
            messages.error(request, 'No variants selected.')
            return redirect('inventory:inventory_list')
        
        if quantity <= 0:
            messages.error(request, 'Quantity must be greater than 0.')
            return redirect('inventory:inventory_list')
        
        variants = ProductVariant.objects.filter(id__in=variant_ids, is_active=True)
        updated_count = 0
        
        with transaction.atomic():
            for variant in variants:
                previous_stock = variant.current_stock
                
                if action == 'add':
                    variant.current_stock += quantity
                    inventory_action = 'stock_added'
                elif action == 'remove':
                    if variant.current_stock >= quantity:
                        variant.current_stock -= quantity
                        inventory_action = 'stock_removed'
                    else:
                        continue
                else:
                    continue
                
                variant.save()
                
                InventoryLog.objects.create(
                    variant=variant,
                    quantity=quantity,
                    action=inventory_action,
                    remarks=f'Bulk update: {remarks}',
                    previous_stock=previous_stock,
                    new_stock=variant.current_stock
                )
                updated_count += 1
        
        messages.success(request, f'Successfully updated {updated_count} variants.')
        return redirect('inventory:inventory_list')
    
    return redirect('inventory:inventory_list')

@staff_member_required
def low_stock_report_view(request):
    """View all low stock items"""
    variants = ProductVariant.objects.filter(
        current_stock__lte=10, 
        is_active=True
    ).select_related('product', 'product__category')
    
    # Apply filters
    search_query = request.GET.get('search')
    threshold = request.GET.get('threshold', 10)
    
    if search_query:
        variants = variants.filter(
            Q(sku__icontains=search_query) |
            Q(product__name__icontains=search_query)
        )
    
    variants = variants.filter(current_stock__lte=threshold)
    
    # Sort by stock level
    variants = variants.order_by('current_stock')
    
    # Pagination
    paginator = Paginator(variants, 25)
    page = request.GET.get('page')
    variants_page = paginator.get_page(page)
    
    # Statistics
    total_low_stock = variants.count()
    critical_stock = variants.filter(current_stock__lte=5).count()
    out_of_stock = ProductVariant.objects.filter(current_stock=0, is_active=True).count()
    
    context = {
        'variants': variants_page,
        'total_low_stock': total_low_stock,
        'critical_stock': critical_stock,
        'out_of_stock': out_of_stock,
        'search_query': search_query,
        'threshold': threshold,
    }
    return render(request, 'inventory/low_stock_report.html', context)

@staff_member_required
def inventory_logs_view(request):
    """View all inventory logs"""
    logs = InventoryLog.objects.all().select_related('variant', 'variant__product')
    
    # Filters
    action_filter = request.GET.get('action')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search_query = request.GET.get('search')
    
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if date_from:
        logs = logs.filter(created_at__gte=date_from)
    
    if date_to:
        logs = logs.filter(created_at__lte=date_to)
    
    if search_query:
        logs = logs.filter(
            Q(variant__sku__icontains=search_query) |
            Q(variant__product__name__icontains=search_query) |
            Q(remarks__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(logs, 50)
    page = request.GET.get('page')
    logs_page = paginator.get_page(page)
    
    context = {
        'logs': logs_page,
        'action_filter': action_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
        'actions': InventoryLog.ACTIONS,
    }
    return render(request, 'inventory/inventory_logs.html', context)

@staff_member_required
def stock_movement_report_view(request):
    """Generate stock movement report"""
    # Get date range
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    date_from = request.GET.get('date_from', start_date.strftime('%Y-%m-%d'))
    date_to = request.GET.get('date_to', end_date.strftime('%Y-%m-%d'))
    
    # Get movements
    movements = InventoryLog.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to
    ).select_related('variant', 'variant__product')
    
    # Group by product
    product_movements = {}
    for movement in movements:
        product_name = movement.variant.product.name
        if product_name not in product_movements:
            product_movements[product_name] = {
                'added': 0,
                'removed': 0,
                'ordered': 0,
                'adjusted': 0,
            }
        
        if movement.action in ['stock_added', 'stock_adjusted']:
            product_movements[product_name]['added'] += movement.quantity
        elif movement.action == 'order_placed':
            product_movements[product_name]['ordered'] += movement.quantity
        elif movement.action == 'stock_removed':
            product_movements[product_name]['removed'] += movement.quantity
    
    # Summary statistics
    summary = {
        'total_added': movements.filter(action__in=['stock_added', 'stock_adjusted']).aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'total_removed': movements.filter(action='stock_removed').aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'total_ordered': movements.filter(action='order_placed').aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'total_cancelled': movements.filter(action='order_cancelled').aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'total_returned': movements.filter(action='return_received').aggregate(Sum('quantity'))['quantity__sum'] or 0,
    }
    
    context = {
        'movements': product_movements,
        'summary': summary,
        'date_from': date_from,
        'date_to': date_to,
        'total_movements': movements.count(),
    }
    return render(request, 'inventory/stock_movement_report.html', context)

@staff_member_required
def export_inventory_csv(request):
    """Export inventory data to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['SKU', 'Product Name', 'Category', 'Price', 'Sale Price', 'Current Stock', 'Stock Status', 'Last Updated'])
    
    variants = ProductVariant.objects.filter(is_active=True).select_related('product', 'product__category')
    
    for variant in variants:
        writer.writerow([
            variant.sku,
            variant.product.name,
            variant.product.category.name,
            variant.price,
            variant.sale_price or '',
            variant.current_stock,
            variant.stock_status,
            variant.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    
    return response

@staff_member_required
def api_get_variant_stock(request, variant_id):
    """API endpoint to get variant stock information"""
    variant = get_object_or_404(ProductVariant, id=variant_id)
    
    data = {
        'id': variant.id,
        'sku': variant.sku,
        'current_stock': variant.current_stock,
        'in_stock': variant.in_stock,
        'stock_status': variant.stock_status,
        'product_name': variant.product.name,
        'price': str(variant.price),
        'sale_price': str(variant.sale_price) if variant.sale_price else None,
    }
    return JsonResponse(data)

@staff_member_required
def api_bulk_stock_check(request):
    """API endpoint to check stock for multiple variants"""
    skus = request.GET.getlist('skus')
    
    if not skus:
        return JsonResponse({'error': 'No SKUs provided'}, status=400)
    
    variants = ProductVariant.objects.filter(sku__in=skus, is_active=True)
    
    data = {}
    for variant in variants:
        data[variant.sku] = {
            'in_stock': variant.in_stock,
            'current_stock': variant.current_stock,
            'stock_status': variant.stock_status,
        }
    
    return JsonResponse(data)