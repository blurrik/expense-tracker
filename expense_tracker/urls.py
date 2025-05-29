from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from expenses import views
from expenses.views import signup
from expenses.views import export_to_excel
from django.views.decorators.http import require_POST

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('add-category/', views.add_category, name='add_category'),
    path('login/', auth_views.LoginView.as_view(template_name='expenses/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'), 
    path('accounts/logout/', require_POST(auth_views.LogoutView.as_view()), name='logout'),
    path('accounts/signup/', signup, name='signup'),
    path('export-excel/', export_to_excel, name='export_excel'),
]