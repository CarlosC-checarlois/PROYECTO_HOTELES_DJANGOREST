# reserva_rest.py
import requests
from typing import Optional, Dict, Any


class ReservaRest:
    """
    Cliente REST para consultar una reserva.
    Equivalente al ReservaController en C#.
    """

    BASE_URL = "https://reca.azurewebsites.net/api/v1/hoteles/reserva"

    def __init__(self):
        self.headers = {
            "Accept": "application/json"
        }

    def buscar_reserva(self, id_reserva: int) -> Dict[str, Any]:
        """
        Consulta la información completa de una reserva existente.
        Parámetro:
            id_reserva: ID entero de la reserva (obligatorio)
        Retorna:
            Un diccionario con todos los datos de la reserva
        """

        if not id_reserva or id_reserva <= 0:
            raise ValueError("Debe indicar un id_reserva válido (> 0).")

        params = {"idReserva": id_reserva}

        try:
            response = requests.get(self.BASE_URL, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al conectar con el servicio de reservas: {e}")
