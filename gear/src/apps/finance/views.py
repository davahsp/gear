from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import FinanceEntry, EntryCategory, EntryType
from .forms import FinanceEntryForm
import json


# @login_required  # Temporarily disabled for testing
def operational_list(request):
    """View to display list of operational cash transactions"""
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    jenis_filter = request.GET.get('jenis', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Base queryset
    entries = FinanceEntry.objects.select_related('category', 'who_inputs').all()
    
    # Apply filters
    if search_query:
        entries = entries.filter(
            Q(category__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if jenis_filter:
        entries = entries.filter(category__type=jenis_filter)
    
    if start_date:
        entries = entries.filter(transaction_date__gte=start_date)
    
    if end_date:
        entries = entries.filter(transaction_date__lte=end_date)
    
    # Sort by newest first
    entries = entries.order_by('-transaction_date', '-id')
    
    # Separate expense and income entries for table (already filtered by search/jenis/date)
    expense_entries = entries.filter(category__type=EntryType.EXPENSE)
    income_entries = entries.filter(category__type=EntryType.INCOME)
    
    # Use the same filtered entries for summary cards and chart
    # This ensures consistency between table and summary
    expense_queryset = expense_entries
    income_queryset = income_entries
    
    # HARDCODED RESET: If no data after filtering, force everything to 0
    if expense_queryset.count() == 0 and income_queryset.count() == 0:
        total_expense = 0
        total_income = 0
        profit = 0
        profit_percentage = 0
        chart_data = []
    else:
        # Calculate totals for summary cards
        total_expense = expense_queryset.aggregate(total=Sum('nominal'))['total'] or 0
        total_income = income_queryset.aggregate(total=Sum('nominal'))['total'] or 0
        profit = total_income - total_expense
        
        # Calculate profit percentage (profit/expense * 100)
        if total_expense > 0:
            profit_percentage = (profit / total_expense) * 100
        else:
            profit_percentage = 100 if total_income > 0 else 0
        
        # Get expense breakdown for pie chart
        expense_stats = (
            expense_queryset
            .values('category__name')
            .annotate(total=Sum('nominal'), count=Count('id'))
            .order_by('-total')
        )
        
        # Calculate percentages for pie chart
        chart_data = []
        for item in expense_stats:
            percentage = (item['total'] / total_expense * 100) if total_expense > 0 else 0
            chart_data.append({
                'category': item['category__name'],
                'total': item['total'],
                'percentage': round(percentage, 2)
            })
    
    # Pagination for expense
    expense_paginator = Paginator(expense_entries, 10)
    expense_page_number = request.GET.get('expense_page', 1)
    expense_page_obj = expense_paginator.get_page(expense_page_number)
    
    # Pagination for income
    income_paginator = Paginator(income_entries, 10)
    income_page_number = request.GET.get('income_page', 1)
    income_page_obj = income_paginator.get_page(income_page_number)
    
    context = {
        'expense_page_obj': expense_page_obj,
        'income_page_obj': income_page_obj,
        'search_query': search_query,
        'jenis_filter': jenis_filter,
        'start_date': start_date,
        'end_date': end_date,
        'chart_data': json.dumps(chart_data),
        'total_expense': total_expense,
        'total_income': total_income,
        'profit': profit,
        'profit_percentage': round(profit_percentage, 2),
    }
    
    return render(request, 'finance/operational_list.html', context)


# @login_required  # Temporarily disabled for testing
def operational_add(request):
    """View to add operational cash transaction with PRG pattern"""
    
    if request.method == 'POST':
        # Get category name from form
        category_name = request.POST.get('category_name')
        
        if category_name:
            try:
                # Get or create category
                category, created = EntryCategory.objects.get_or_create(
                    name=category_name,
                    type=EntryType.EXPENSE
                )
                
                # Get user
                User = get_user_model()
                user = User.objects.first()
                
                if not user:
                    messages.error(request, 'Tidak ada user yang tersedia. Silakan buat user terlebih dahulu.')
                    return redirect('finance:operational_list')
                
                # Create a mutable copy of POST data
                post_data = request.POST.copy()
                post_data['category'] = category.id
                
                form = FinanceEntryForm(post_data)
                if form.is_valid():
                    entry = form.save(commit=False)
                    entry.who_inputs = user
                    entry.save()
                    
                    messages.success(request, 'Transaksi berhasil disimpan!')
                    return redirect('finance:operational_list')  # PRG pattern
                else:
                    messages.error(request, f'Terdapat kesalahan pada form: {form.errors}')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Kategori harus dipilih!')
    else:
        form = FinanceEntryForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'finance/operational_add.html', context)


# @login_required  # Temporarily disabled for testing
def operational_income_add(request):
    """View to add operational income transaction with PRG pattern"""
    
    if request.method == 'POST':
        # Get category name from form
        category_name = request.POST.get('category_name')
        
        if category_name:
            # Get or create category
            category, created = EntryCategory.objects.get_or_create(
                name=category_name,
                type=EntryType.INCOME
            )
            
            # Create a mutable copy of POST data
            post_data = request.POST.copy()
            post_data['category'] = category.id
            post_data['jenis'] = EntryType.INCOME
            
            form = FinanceEntryForm(post_data)
            if form.is_valid():
                entry = form.save(commit=False)
                # Temporarily assign to first user
                User = get_user_model()
                entry.who_inputs = User.objects.first()
                if not entry.who_inputs:
                    messages.error(request, 'Tidak ada user yang tersedia. Silakan buat user terlebih dahulu.')
                    return redirect('finance:operational_list')
                entry.save()
                
                messages.success(request, 'Transaksi pemasukan berhasil disimpan!')
                return redirect('finance:operational_list')  # PRG pattern
            else:
                messages.error(request, 'Terdapat kesalahan pada form. Silakan periksa kembali.')
        else:
            messages.error(request, 'Kategori harus dipilih!')
    else:
        form = FinanceEntryForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'finance/operational_income_add.html', context)


# @login_required  # Temporarily disabled for testing
def get_categories_ajax(request):
    """AJAX endpoint to get categories based on entry type"""
    jenis = request.GET.get('jenis', '')
    
    if jenis:
        categories = EntryCategory.objects.filter(type=jenis).values('id', 'name').order_by('name')
        return JsonResponse({'categories': list(categories)})
    
    return JsonResponse({'categories': []})
