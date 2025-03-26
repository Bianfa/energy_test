import json
from datetime import datetime, timedelta

from rest_framework.response import Response
from rest_framework.decorators import api_view
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException
import logging
import pandas as pd
from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

from miapp.energia.models import RegistroEnergia

# Configuración de conexión Modbus
MODBUS_HOST = "multimetersolin.dyndns.org"
MODBUS_PORT = 502
MODBUS_SLAVE_ID = 5

# Configuración del logger
logger = logging.getLogger(__name__)

def dashboard(request):
    """Renderiza la página principal del monitor de energía."""
    return render(request, 'dashboard.html')

def read_register(address, count=2, scale=1):
    """Función para leer registros Modbus con manejo de errores y logs."""
    client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)
    client.connect()
    try:
        result = client.read_holding_registers(address=address, count=count, slave=MODBUS_SLAVE_ID)
        if result and not result.isError() and result.registers:
            raw_value = (result.registers[0] << 16) | result.registers[1]  # Convertir a 32 bits
            value = raw_value / scale
            logger.info(f"Lectura exitosa: {address} -> {value}")
            return value
        else:
            logger.warning(f"Error al leer dirección {address}")
            return "Error"
    except Exception as e:
        logger.error(f"Excepción en la lectura Modbus: {e}")
        return "Error"
    finally:
        client.close()

@api_view(['GET'])
def obtener_datos_modbus(request):
    """ Endpoint para obtener datos y guardarlos en la BD """
    datos = {
        "Voltaje Fase 1 (V)": read_register(4096, 2, 1000),
        "Voltaje Fase 2 (V)": read_register(4098, 2, 1000),
        "Voltaje Fase 3 (V)": read_register(4100, 2, 1000),
        "Corriente Fase 1 (A)": read_register(4102, 2, 1000),
        "Corriente Fase 2 (A)": read_register(4104, 2, 1000),
        "Corriente Fase 3 (A)": read_register(4106, 2, 1000),
        "Potencia Activa Total (kW)": read_register(4112, 2, 1000),
        "Potencia Reactiva Total (kVAR)": read_register(4114, 2, 1000),
        "Potencia Aparente Total (kVA)": read_register(4116, 2, 1000),
        "Energía Activa Total (kWh)": read_register(4688, 2, 10),
        "Energía Reactiva Total (kVARh)": read_register(4690, 2, 100),
    }

    # Guardar en la base de datos
    # Solo guardar si todos los datos requeridos son válidos (no "Error")
    if all(isinstance(v, (int, float)) for v in datos.values()):
        RegistroEnergia.objects.create(
            voltaje_fase_1=datos["Voltaje Fase 1 (V)"],
            voltaje_fase_2=datos["Voltaje Fase 2 (V)"],
            voltaje_fase_3=datos["Voltaje Fase 3 (V)"],
            corriente_fase_1=datos["Corriente Fase 1 (A)"],
            corriente_fase_2=datos["Corriente Fase 2 (A)"],
            corriente_fase_3=datos["Corriente Fase 3 (A)"],
            potencia_activa=datos["Potencia Activa Total (kW)"],
            potencia_reactiva=datos["Potencia Reactiva Total (kVAR)"],
            potencia_aparente=datos["Potencia Aparente Total (kVA)"],
            energia_activa=datos["Energía Activa Total (kWh)"],
            energia_reactiva=datos["Energía Reactiva Total (kVARh)"],
        )
    else:
        logger.warning("No se guardó el registro por valores inválidos.")

    return Response(datos)

def historico(request):
    return render(request, 'historico.html')

def obtener_historico(request):
    rango = request.GET.get('rango', 'diario')
    fecha_hoy = datetime.now()

    if rango == "diario":
        fecha_inicio = fecha_hoy - timedelta(days=1)
    elif rango == "semanal":
        fecha_inicio = fecha_hoy - timedelta(weeks=1)
    elif rango == "mensual":
        fecha_inicio = fecha_hoy - timedelta(days=30)
    else:
        fecha_inicio = fecha_hoy - timedelta(days=1)

    registros = RegistroEnergia.objects.filter(timestamp__gte=fecha_inicio).order_by('timestamp')
    data = [
        {
            "fecha": reg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "voltaje_fase1": reg.voltaje_fase_1,
            "voltaje_fase2": reg.voltaje_fase_2,
            "voltaje_fase3": reg.voltaje_fase_3,
            "corriente_fase1": reg.corriente_fase_1,
            "corriente_fase2": reg.corriente_fase_2,
            "corriente_fase3": reg.corriente_fase_3,
            "potencia_activa": reg.potencia_activa,
            "potencia_reactiva": reg.potencia_reactiva,
            "potencia_aparente": reg.potencia_aparente,
            "energia_activa": reg.energia_activa,
            "energia_reactiva": reg.energia_reactiva,
        }
        for reg in registros
    ]
    return JsonResponse(data, safe=False)

def exportar_excel(request):
    rango = request.GET.get('rango', 'diario')
    fecha_hoy = datetime.now()

    if rango == "diario":
        fecha_inicio = fecha_hoy - timedelta(days=1)
    elif rango == "semanal":
        fecha_inicio = fecha_hoy - timedelta(weeks=1)
    elif rango == "mensual":
        fecha_inicio = fecha_hoy - timedelta(days=30)
    else:
        fecha_inicio = fecha_hoy - timedelta(days=1)

    registros = RegistroEnergia.objects.filter(timestamp__gte=fecha_inicio).order_by('timestamp')

    df = pd.DataFrame([
        {
            "Fecha": reg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Voltaje Fase 1": reg.voltaje_fase_1,
            "Voltaje Fase 2": reg.voltaje_fase_2,
            "Voltaje Fase 3": reg.voltaje_fase_3,
            "Corriente Fase 1": reg.corriente_fase_1,
            "Corriente Fase 2": reg.corriente_fase_2,
            "Corriente Fase 3": reg.corriente_fase_3,
            "Potencia Activa Total": reg.potencia_activa,
            "Potencia Reactiva Total": reg.potencia_reactiva,
            "Potencia Aparente Total": reg.potencia_aparente,
            "Energía Activa Total": reg.energia_activa,
            "Energía Reactiva Total": reg.energia_reactiva,
        }
        for reg in registros
    ])

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="historico_energia.xlsx"'
    df.to_excel(response, index=False)
    return response
