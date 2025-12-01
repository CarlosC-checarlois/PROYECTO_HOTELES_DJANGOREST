# pre_reserva_rest.py
import requests
from datetime import datetime
from typing import Optional, Dict, Any


class PreReservaRest:
    """
    Cliente REST para crear una pre-reserva (hold).
    Equivalente al PreReservaController en C#.
    """

    BASE_URL = "https://reca.azurewebsites.net/api/v1/hoteles/hold"

    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def crear_prereserva(
        self,
        id_habitacion: str,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        numero_huespedes: int,
        nombre: str,
        apellido: str,
        correo: str,
        tipo_documento: str,
        documento: str,
        duracion_hold_seg: Optional[int] = None,
        precio_actual: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Crea una pre-reserva enviando los datos al servicio REST.
        """

        # Validaciones básicas
        if not id_habitacion:
            raise ValueError("Debe indicar idHabitacion.")
        if fecha_fin <= fecha_inicio:
            raise ValueError("fechaFin debe ser mayor a fechaInicio.")
        if numero_huespedes <= 0:
            raise ValueError("numeroHuespedes debe ser mayor que 0.")

        payload = {
            "idHabitacion": id_habitacion,
            "fechaInicio": fecha_inicio.isoformat(),
            "fechaFin": fecha_fin.isoformat(),
            "numeroHuespedes": numero_huespedes,
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo,
            "tipoDocumento": tipo_documento,
            "documento": documento,
            "duracionHoldSeg": duracion_hold_seg,
            "precioActual": precio_actual
        }

        try:
            response = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al conectar con el servicio PreReserva: {e}")
