# amenidades_gestion_rest.py
from pprint import pprint

import requests
from datetime import datetime
from pprint import pprint
import requests
from datetime import datetime
import json

class AmenidadesGestionRest:
    """
    Cliente REST para consumir el endpoint de Amenidades:
    https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/amenidades

    Equivalente al controlador C# AmenidadesGestionController.
    """

    BASE_URL = "https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/amenidades"

    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    # ============================================================
    # GET: Obtener todas las amenidades
    # ============================================================
    def obtener_amenidades(self):
        try:
            response = requests.get(self.BASE_URL, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener amenidades: {e}")

    # ============================================================
    # GET: Obtener amenidad por ID
    # ============================================================
    def obtener_amenidad_por_id(self, id_amenidad: int):
        if id_amenidad <= 0:
            raise ValueError("El ID debe ser mayor que cero.")

        try:
            response = requests.get(f"{self.BASE_URL}/{id_amenidad}", headers=self.headers)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener amenidad por ID: {e}")

    # ============================================================
    # POST: Crear amenidad
    # ============================================================
    def crear_amenidad(self, id_amenidad: int, nombre: str, estado: bool = True):
        if id_amenidad <= 0:
            raise ValueError("El campo 'id_amenidad' es obligatorio y debe ser mayor a 0.")
        if not nombre:
            raise ValueError("El campo 'nombre' es obligatorio.")

        payload = {
            "idAmenidad": id_amenidad,
            "nombreAmenidad": nombre,
            "estadoAmenidad": estado,
            "fechaModificacionAmenidad": datetime.now().isoformat()
        }

        try:
            response = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al crear amenidad: {e}")

    # ============================================================
    # PUT: Actualizar amenidad
    # ============================================================
    def actualizar_amenidad(self, id_amenidad: int, nombre: str, estado: bool = True):
        if id_amenidad <= 0:
            raise ValueError("El ID debe ser mayor que cero.")
        if not nombre:
            raise ValueError("El campo 'nombre' es obligatorio.")

        payload = {
            "idAmenidad": id_amenidad,
            "nombreAmenidad": nombre,
            "estadoAmenidad": estado,
            "fechaModificacionAmenidad": datetime.now().isoformat()
        }

        try:
            response = requests.put(f"{self.BASE_URL}/{id_amenidad}", json=payload, headers=self.headers)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al actualizar amenidad: {e}")

    # ============================================================
    # DELETE: Eliminación lógica
    # ============================================================
    def eliminar_amenidad(self, id_amenidad: int):
        if id_amenidad <= 0:
            raise ValueError("El ID debe ser mayor que cero.")
        try:
            response = requests.delete(f"{self.BASE_URL}/{id_amenidad}", headers=self.headers)
            if response.status_code == 404:
                return False
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al eliminar amenidad: {e}")
c = AmenidadesGestionRest()
amenidades = c.obtener_amenidades()
print(json.dumps(amenidades, indent=2))  # Esto convierte el diccionario Python en un string JSON legible
