from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count  
from datetime import date, timedelta
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
import locale
from django.http import HttpResponse
import openpyxl
from datetime import datetime


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def dashboard(request):
    today = date.today()
    start_of_month = today.replace(day=1)
    end_of_month = start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timedelta(days=1)
    
    locale.setlocale(locale.LC_TIME, 'russian')

    expenses = Expense.objects.filter(
        user=request.user,
        date__range=[start_of_month, end_of_month]
    ).order_by('-date')
    
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    categories = Category.objects.filter(user=request.user)
    category_stats = expenses.values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')  
    ).order_by('-total')
    
    notifications = []
    restaurant_spending = expenses.filter(category__name__icontains='Рестораны').aggregate(Sum('amount'))['amount__sum'] or 0
    if restaurant_spending > 1000:  
        notifications.append(f"Вы потратили {restaurant_spending} на Рестораны в этом месяце. Дома еды нет?")

    taxi_spending = expenses.filter(category__name__icontains='Такси').aggregate(Sum('amount'))['amount__sum'] or 0
    if taxi_spending > 1000:  
        notifications.append(f"Вы потратили {taxi_spending} на Такси в этом месяце. Может стоит пройтись пешком?")
    
    context = {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'category_stats': category_stats,
        'notifications': notifications,
        'current_month': start_of_month.strftime('%B %Y'),
        'categories': categories,
    }
    
    return render(request, 'expenses/dashboard.html', context)

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.user, request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm(request.user) 
    
    return render(request, 'expenses/add_expense.html', {'form': form})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Категория успешно добавлена!')
            return redirect('dashboard')
    else:
        form = CategoryForm()
    
    return render(request, 'expenses/add_category.html', {'form': form})

@login_required
def export_to_excel(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
   
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="expenses_{datetime.now().strftime("%Y-%m-%d")}.xlsx"'
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Расходы"
    
    ws.append(['Дата', 'Категория', 'Сумма', 'Описание'])
    
    for expense in expenses:
        ws.append([
            expense.date.strftime("%d.%m.%Y"),
            expense.category.name,
            expense.amount,
            expense.description or "-"
        ])
    
    wb.save(response)
    return response