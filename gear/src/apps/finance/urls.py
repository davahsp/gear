from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('operational/', views.operational_list, name='operational_list'),
    path('operational/expense/add/', views.operational_add, name='operational_add'),
    path('operational/income/add/', views.operational_income_add, name='operational_income_add'),
    path('ajax/get-categories/', views.get_categories_ajax, name='get_categories_ajax'),
]
