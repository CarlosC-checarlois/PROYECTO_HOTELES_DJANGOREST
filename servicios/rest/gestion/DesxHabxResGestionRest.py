# desxhabxres_gestion_rest.py
import requests
from datetime import datetime


class DesxHabxResGestionRest:
    """
    Cliente REST para el recurso DESXHABXRES.
    Equivale al controlador C# DesxHabxResGestionController.

    BASE:
    https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/desxhabxres
    """

    BASE_URL = "https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/desxhabxres"

    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    # ============================================================
    # GET → Obtener lista completa
    # ============================================================
    def obtener_desxhabxres(self):
        try:
            resp = requests.get(self.BASE_URL, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener lista de DesxHabxRes: {e}")

    # ============================================================
    # GET → Obtener por ID compuesto
    # ============================================================
    def obtener_por_id(self, id_descuento: int, id_habxres: int):
        if id_descuento <= 0 or id_habxres <= 0:
            raise ValueError("Los IDs deben ser mayores a 0.")

        url = f"{self.BASE_URL}/{id_descuento}/{id_habxres}"

        try:
            resp = requests.get(url, headers=self.headers)

            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener DesxHabxRes: {e}")

    # ============================================================
    # POST → Crear
    # ============================================================
    def crear_desxhabxres(self, id_descuento, id_habxres, monto=None, estado=True):
        if id_descuento <= 0 or id_habxres <= 0:
            raise ValueError("Los IDs deben ser mayores a 0.")

        payload = {
            "idDescuento": id_descuento,
            "idHabxRes": id_habxres,
            "montoDesxHabxRes": monto,
            "estadoDesxHabxRes": estado,
            "fechaModificacionDesxHabxRes": datetime.now().isoformat()
        }

        try:
            resp = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al crear DesxHabxRes: {e}")

    # ============================================================
    # PUT → Actualizar
    # ============================================================
    def actualizar_desxhabxres(self, id_descuento, id_habxres, monto, estado):
        if id_descuento <= 0 or id_habxres <= 0:
            raise ValueError("Los IDs deben ser mayores a 0.")

        payload = {
            "idDescuento": id_descuento,
            "idHabxRes": id_habxres,
            "montoDesxHabxRes": monto,
            "estadoDesxHabxRes": estado,
            "fechaModificacionDesxHabxRes": datetime.now().isoformat()
        }

        try:
            resp = requests.put(self.BASE_URL, json=payload, headers=self.headers)

            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al actualizar DesxHabxRes: {e}")

    # ============================================================
    # DELETE → Eliminación lógica
    # ============================================================
    def eliminar_desxhabxres(self, id_descuento, id_habxres):
        if id_descuento <= 0 or id_habxres <= 0:
            raise ValueError("Los IDs deben ser mayores a 0.")

        url = f"{self.BASE_URL}/{id_descuento}/{id_habxres}"

        try:
            resp = requests.delete(url, headers=self.headers)

            if resp.status_code == 404:
                return False

            resp.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al eliminar DesxHabxRes: {e}")

