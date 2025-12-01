# disponibilidad_rest.py
import requests
from datetime import datetime


class DisponibilidadRest:
    """
    Cliente REST para verificar disponibilidad de habitaciones.
    Equivalente a DisponibilidadController en C#.
    """

    BASE_URL = "https://reca.azurewebsites.net/api/v1/hoteles/availability"

    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    def validar_disponibilidad(self, id_habitacion: str, fecha_inicio: datetime, fecha_fin: datetime):
        """
        Envía una solicitud POST para validar si una habitación está disponible
        entre las fechas indicadas.
        """

        # ===== VALIDACIONES PREVIAS =====
        if not id_habitacion:
            raise ValueError("El campo 'id_habitacion' es obligatorio.")
        if fecha_fin <= fecha_inicio:
            raise ValueError("fecha_fin debe ser mayor que fecha_inicio.")

        # ===== CUERPO DEL REQUEST =====
        payload = {
            "idHabitacion": id_habitacion,
            "fechaInicio": fecha_inicio.isoformat(),
            "fechaFin": fecha_fin.isoformat(),
        }

        # ===== SOLICITUD =====
        try:
            response = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al conectar con el servicio de disponibilidad: {e}")
