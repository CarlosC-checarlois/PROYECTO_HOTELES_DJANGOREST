# ciudad_gestion_rest.py
from smtpd import PureProxy

import requests
from datetime import datetime

class CiudadGestionRest:
    """
    Cliente REST para la gestión de la tabla CIUDAD.
    Equivalente al CiudadGestionController en C#.

    ENDPOINT BASE:
    https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/ciudad
    """

    BASE_URL = "https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/ciudad"

    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    # ============================================================
    # GET → ObtenerCiudad
    # ============================================================
    def obtener_ciudades(self):
        try:
            response = requests.get(self.BASE_URL, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener ciudades: {e}")

    # ============================================================
    # GET → ObtenerCiudadPorId
    # ============================================================
    def obtener_ciudad_por_id(self, id_ciudad: int):
        if id_ciudad <= 0:
            raise ValueError("El id_ciudad debe ser > 0.")

        url = f"{self.BASE_URL}/{id_ciudad}"

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener ciudad por ID: {e}")

    # ============================================================
    # POST → CrearCiudad
    # ============================================================
    def crear_ciudad(self, id_ciudad: int, id_pais: int, nombre: str, estado: bool = True):
        if id_ciudad <= 0:
            raise ValueError("id_ciudad debe ser mayor que 0.")
        if id_pais <= 0:
            raise ValueError("id_pais debe ser mayor que 0.")
        if not nombre:
            raise ValueError("El nombre de la ciudad es obligatorio.")

        payload = {
            "idCiudad": id_ciudad,
            "idPais": id_pais,
            "nombreCiudad": nombre,
            "estadoCiudad": estado,
            "fechaModificacionCiudad": datetime.now().isoformat()
        }

        try:
            response = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al crear ciudad: {e}")

    # ============================================================
    # PUT → ActualizarCiudad
    # ============================================================
    def actualizar_ciudad(self, id_ciudad: int, id_pais: int, nombre: str, estado: bool):
        if id_ciudad <= 0:
            raise ValueError("id_ciudad debe ser mayor que 0.")
        if id_pais <= 0:
            raise ValueError("id_pais debe ser mayor que 0.")
        if not nombre:
            raise ValueError("El nombre no puede estar vacío.")

        payload = {
            "idCiudad": id_ciudad,
            "idPais": id_pais,
            "nombreCiudad": nombre,
            "estadoCiudad": estado,
            "fechaModificacionCiudad": datetime.now().isoformat()
        }

        url = f"{self.BASE_URL}/{id_ciudad}"

        try:
            response = requests.put(url, json=payload, headers=self.headers)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al actualizar ciudad: {e}")

    # ============================================================
    # DELETE → EliminarCiudad
    # ============================================================
    def eliminar_ciudad(self, id_ciudad: int):
        if id_ciudad <= 0:
            raise ValueError("id_ciudad debe ser mayor que 0.")

        url = f"{self.BASE_URL}/{id_ciudad}"

        try:
            response = requests.delete(url, headers=self.headers)

            if response.status_code == 404:
                return False

            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al eliminar ciudad: {e}")

