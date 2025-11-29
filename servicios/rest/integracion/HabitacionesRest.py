# habitaciones_rest.py
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any


class HabitacionesRest:
    """
    Cliente REST para consultar habitaciones disponibles.
    Equivalente al HabitacionesController en C#.
    """

    BASE_URL = "https://reca.azurewebsites.net/api/v1/hoteles/search"

    def __init__(self):
        self.headers = {"Accept": "application/json"}

    def buscar_habitaciones(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        tipo_habitacion: Optional[str] = None,
        capacidad: Optional[int] = None,
        precio_min: Optional[float] = None,
        precio_max: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Realiza una solicitud GET al servicio de búsqueda de habitaciones.
        Todos los parámetros son opcionales.
        """

        params = {}

        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        if tipo_habitacion:
            params["tipo_habitacion"] = tipo_habitacion
        if capacidad is not None:
            params["capacidad"] = capacidad
        if precio_min is not None:
            params["precio_min"] = precio_min
        if precio_max is not None:
            params["precio_max"] = precio_max

        try:
            response = requests.get(self.BASE_URL, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al conectar con el servicio de búsqueda: {e}")

if __name__ == "__main__":
    # Instancia del cliente REST
    cliente = HabitacionesRest()

    # Llamada sin parámetros
    try:
        resultados = cliente.buscar_habitaciones()
        print("Habitaciones encontradas:")
        for i, habitacion in enumerate(resultados, start=1):
            print(f"{i}. {habitacion}")
    except Exception as e:
        print("Error:", e)
