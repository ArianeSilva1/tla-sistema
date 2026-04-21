from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("Sistema TLA no ar 🚀")

urlpatterns = [
    path('', home),  # 👈 ESSA LINHA resolve o 404
    path('admin/', admin.site.urls),
]