from django.urls import path
from .views import obtener_datos_modbus, dashboard, historico, obtener_historico, exportar_excel

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("api/modbus/", obtener_datos_modbus, name="modbus"),
    path('historico/', historico, name="historico"),
    path("api/historico/", obtener_historico, name="api_historico"),
    path("api/exportar_excel/", exportar_excel, name="exportar_excel"),
]

