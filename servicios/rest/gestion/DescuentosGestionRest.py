
import requests
from datetime import datetime


class DescuentosGestionRest:
    """
    Cliente REST para el recurso DESCUENTO.
    Equivale al controlador C#: DescuentosGestionController

    ENDPOINT BASE:
    https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/descuentos
    """

    BASE_URL = "https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/descuentos"

    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    # ============================================================
    # GET → ObtenerDescuentos
    # ============================================================
    def obtener_descuentos(self):
        try:
            resp = requests.get(self.BASE_URL, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener descuentos: {e}")

    # ============================================================
    # GET → ObtenerDescuentoPorId
    # ============================================================
    def obtener_descuento_por_id(self, id_descuento: int):
        if id_descuento <= 0:
            raise ValueError("El id debe ser mayor a 0.")

        url = f"{self.BASE_URL}/{id_descuento}"

        try:
            resp = requests.get(url, headers=self.headers)

            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener descuento por ID: {e}")

    # ============================================================
    # POST → CrearDescuento
    # ============================================================
    def crear_descuento(self, id_descuento, nombre, valor, fecha_inicio=None, fecha_fin=None, estado=True):
        if id_descuento <= 0:
            raise ValueError("id_descuento debe ser mayor que 0.")

        payload = {
            "idDescuento": id_descuento,
            "nombreDescuento": nombre,
            "valorDescuento": valor,
            "fechaInicioDescuento": fecha_inicio,
            "fechaFinDescuento": fecha_fin,
            "estadoDescuento": estado,
            "fechaModificacionDescuento": datetime.now().isoformat()
        }

        try:
            resp = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al crear descuento: {e}")

    # ============================================================
    # PUT → ActualizarDescuento
    # ============================================================
    def actualizar_descuento(self, id_descuento, nombre, valor, fecha_inicio, fecha_fin, estado):
        if id_descuento <= 0:
            raise ValueError("id_descuento debe ser mayor que 0.")

        payload = {
            "idDescuento": id_descuento,
            "nombreDescuento": nombre,
            "valorDescuento": valor,
            "fechaInicioDescuento": fecha_inicio,
            "fechaFinDescuento": fecha_fin,
            "estadoDescuento": estado,
            "fechaModificacionDescuento": datetime.now().isoformat()
        }

        url = f"{self.BASE_URL}/{id_descuento}"

        try:
            resp = requests.put(url, json=payload, headers=self.headers)

            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al actualizar descuento: {e}")

    # ============================================================
    # DELETE → EliminarDescuento
    # ============================================================
    def eliminar_descuento(self, id_descuento):
        if id_descuento <= 0:
            raise ValueError("id_descuento debe ser mayor que 0.")

        url = f"{self.BASE_URL}/{id_descuento}"

        try:
            resp = requests.delete(url, headers=self.headers)

            if resp.status_code == 404:
                return False

            resp.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al eliminar descuento: {e}")
