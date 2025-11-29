# hold_gestion_rest.py
from pprint import pprint

import requests
from datetime import datetime


class HoldGestionRest:
    """
    Cliente REST para la entidad HOLD.
    Equivalente al controlador HoldGestionController en C#.

    URL base:
    https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/hold
    """

    BASE_URL = "https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/hold"

    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    # ========================================================
    # GET → Obtener todos los HOLDs
    # ========================================================
    def obtener_hold(self):
        try:
            resp = requests.get(self.BASE_URL, headers=self.headers)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener HOLD: {e}")

    # ========================================================
    # GET → Obtener HOLD por ID
    # ========================================================
    def obtener_hold_por_id(self, id_hold: str):
        if not id_hold:
            raise ValueError("ID_HOLD es obligatorio.")

        url = f"{self.BASE_URL}/{id_hold}"

        try:
            resp = requests.get(url, headers=self.headers)

            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener HOLD por ID: {e}")

    # ========================================================
    # POST → Crear HOLD
    # ========================================================
    def crear_hold(
        self,
        id_hold: str,
        id_habitacion: str,
        id_reserva: int,
        tiempo_hold: int = None,
        fecha_inicio: datetime = None,
        fecha_final: datetime = None,
        estado: bool = True
    ):
        # Validaciones
        if not id_hold:
            raise ValueError("ID_HOLD es obligatorio.")
        if not id_habitacion:
            raise ValueError("ID_HABITACION es obligatorio.")
        if not id_reserva:
            raise ValueError("ID_RESERVA es obligatorio.")

        payload = {
            "idHold": id_hold,
            "idHabitacion": id_habitacion,
            "idReserva": id_reserva,
            "tiempoHold": tiempo_hold,
            "fechaInicioHold": fecha_inicio.isoformat() if fecha_inicio else None,
            "fechaFinalHold": fecha_final.isoformat() if fecha_final else None,
            "estadoHold": estado
        }

        try:
            resp = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al crear HOLD: {e}")

    # ========================================================
    # PUT → Actualizar HOLD
    # ========================================================
    def actualizar_hold(
        self,
        id_hold: str,
        id_habitacion: str,
        id_reserva: int,
        tiempo_hold=None,
        fecha_inicio: datetime = None,
        fecha_final: datetime = None,
        estado=None
    ):
        if not id_hold:
            raise ValueError("ID_HOLD es obligatorio.")

        payload = {
            "idHold": id_hold,
            "idHabitacion": id_habitacion,
            "idReserva": id_reserva,
            "tiempoHold": tiempo_hold,
            "fechaInicioHold": fecha_inicio.isoformat() if fecha_inicio else None,
            "fechaFinalHold": fecha_final.isoformat() if fecha_final else None,
            "estadoHold": estado
        }

        url = f"{self.BASE_URL}/{id_hold}"

        try:
            resp = requests.put(url, json=payload, headers=self.headers)

            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al actualizar HOLD: {e}")

    # ========================================================
    # DELETE → Eliminación lógica del HOLD
    # ========================================================
    def eliminar_hold(self, id_hold: str):
        if not id_hold:
            raise ValueError("ID_HOLD es obligatorio.")

        url = f"{self.BASE_URL}/{id_hold}"

        try:
            resp = requests.delete(url, headers=self.headers)

            if resp.status_code == 404:
                return False

            resp.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al eliminar HOLD: {e}")

c = HoldGestionRest()
c = c.obtener_hold()

pprint(c)