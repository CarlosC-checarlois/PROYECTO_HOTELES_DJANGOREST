# amexhab_gestion_rest.py

import requests
from datetime import datetime


class AmexHabGestionRest:
    """
    Cliente REST para la tabla AMEXHAB.
    Equivalente al AmexHabGestionController en C#.

    URL base:
    https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/amexhab
    """

    BASE_URL = "https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/amexhab"

    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    # ---------------------------------------------------------------
    # GET → ObtenerAmexHab
    # ---------------------------------------------------------------
    def obtener_amexhab(self):
        try:
            response = requests.get(self.BASE_URL, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener AMEXHAB: {e}")

    # ---------------------------------------------------------------
    # GET → ObtenerAmexHabPorId
    # ---------------------------------------------------------------
    def obtener_amexhab_por_id(self, id_habitacion: str, id_amenidad: int):
        if not id_habitacion:
            raise ValueError("id_habitacion no puede estar vacío.")
        if id_amenidad <= 0:
            raise ValueError("id_amenidad debe ser mayor que 0.")

        url = f"{self.BASE_URL}/{id_habitacion}/{id_amenidad}"

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener AMEXHAB por ID: {e}")

    # ---------------------------------------------------------------
    # POST → CrearAmexHab
    # ---------------------------------------------------------------
    def crear_amexhab(self, id_habitacion: str, id_amenidad: int, estado: bool = True):
        if not id_habitacion:
            raise ValueError("id_habitacion es obligatorio.")
        if id_amenidad <= 0:
            raise ValueError("id_amenidad debe ser mayor a 0.")

        payload = {
            "idHabitacion": id_habitacion,
            "idAmenidad": id_amenidad,
            "estadoAmexHab": estado,
            "fechaModificacionAmexHab": datetime.now().isoformat()
        }

        try:
            response = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al crear AMEXHAB: {e}")

    # ---------------------------------------------------------------
    # PUT → ActualizarAmexHab
    # ---------------------------------------------------------------
    def actualizar_amexhab(self, id_habitacion: str, id_amenidad: int, estado: bool):
        if not id_habitacion:
            raise ValueError("id_habitacion es obligatorio.")
        if id_amenidad <= 0:
            raise ValueError("id_amenidad debe ser mayor a 0.")

        payload = {
            "idHabitacion": id_habitacion,
            "idAmenidad": id_amenidad,
            "estadoAmexHab": estado,
            "fechaModificacionAmexHab": datetime.now().isoformat()
        }

        try:
            response = requests.put(self.BASE_URL, json=payload, headers=self.headers)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al actualizar AMEXHAB: {e}")

    # ---------------------------------------------------------------
    # DELETE → EliminarAmexHab
    # ---------------------------------------------------------------
    def eliminar_amexhab(self, id_habitacion: str, id_amenidad: int):
        if not id_habitacion:
            raise ValueError("id_habitacion es obligatorio.")
        if id_amenidad <= 0:
            raise ValueError("id_amenidad debe ser mayor a 0.")

        url = f"{self.BASE_URL}/{id_habitacion}/{id_amenidad}"

        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code == 404:
                return False
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al eliminar AMEXHAB: {e}")

