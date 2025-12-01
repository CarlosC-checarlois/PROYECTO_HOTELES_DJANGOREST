# confirmar_reserva_rest.py
import requests
from datetime import datetime

class ConfirmarReservaRest:
    """
    Clase cliente REST para confirmar una reserva en el servicio remoto.
    Equivalente a ConfirmarReservaController en C#.
    """

    BASE_URL = "https://reca.azurewebsites.net/api/v1/hoteles/book"

    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    def confirmar_reserva(
        self,
        id_habitacion: str,
        id_hold: str,
        nombre: str,
        apellido: str,
        correo: str,
        tipo_documento: str,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        numero_huespedes: int,
    ):
        """
        Envía una solicitud POST para confirmar la reserva.
        Retorna la respuesta en formato JSON o lanza una excepción en caso de error.
        """

        # Validaciones previas (similares a las del controlador C#)
        if not id_habitacion:
            raise ValueError("El campo 'id_habitacion' es obligatorio.")
        if not id_hold:
            raise ValueError("El campo 'id_hold' es obligatorio.")
        if not nombre:
            raise ValueError("El campo 'nombre' es obligatorio.")
        if not apellido:
            raise ValueError("El campo 'apellido' es obligatorio.")
        if not correo:
            raise ValueError("El campo 'correo' es obligatorio.")
        if not tipo_documento:
            raise ValueError("El campo 'tipo_documento' es obligatorio.")
        if fecha_fin <= fecha_inicio:
            raise ValueError("fecha_fin debe ser mayor que fecha_inicio.")
        if numero_huespedes <= 0:
            raise ValueError("numero_huespedes debe ser mayor que 0.")

        payload = {
            "idHabitacion": id_habitacion,
            "idHold": id_hold,
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo,
            "tipoDocumento": tipo_documento,
            "fechaInicio": fecha_inicio.isoformat(),
            "fechaFin": fecha_fin.isoformat(),
            "numeroHuespedes": numero_huespedes,
        }

        # Petición al servicio remoto
        try:
            response = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            response.raise_for_status()  # Lanza error si la respuesta no es 2xx
            return response.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al conectar con el servicio REST: {e}")
