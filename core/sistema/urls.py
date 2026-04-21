from django.contrib import admin
from django.urls import path
from core.views import home, fatura_pdf, relatorio_excel, dashboard

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('dashboard/', dashboard, name='dashboard'),
    path('fatura/<int:processo_id>/', fatura_pdf, name='fatura_pdf'),
    path('relatorio-excel/', relatorio_excel, name='relatorio_excel'),
]