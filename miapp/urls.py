from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('miapp.energia.urls')),  # ✅ Incluye las URLs de la app `energia`
]