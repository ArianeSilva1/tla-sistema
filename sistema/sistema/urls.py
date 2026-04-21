from django.contrib import admin
from django.urls import path
from core.views import fatura_pdf, relatorio_excel

urlpatterns = [
    path('admin/', admin.site.urls),

    # Fatura em PDF
    path('fatura/<int:processo_id>/', fatura_pdf),

    # Relatório financeiro em Excel
    path('relatorio-excel/', relatorio_excel),
]