# ReservaGestionRest.py
from pprint import pprint

import requests
from datetime import datetime


class ReservaGestionRest:
    """
    Cliente REST para la entidad RESERVA.
    Compatible con:
    api/gestion/reserva
    """

    BASE_URL = "https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/reservas"

    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    # =====================================================================================
    # GET → Listar reservas
    # =====================================================================================
    def obtener_reservas(self):
        try:
            resp = requests.get(self.BASE_URL, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener reservas: {e}")

    # =====================================================================================
    # GET → Obtener reserva por ID
    # =====================================================================================
    def obtener_reserva_por_id(self, id_reserva: int):
        if not id_reserva:
            raise ValueError("ID_RESERVA es obligatorio.")

        url = f"{self.BASE_URL}/{id_reserva}"

        try:
            resp = requests.get(url, headers=self.headers)

            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener reserva: {e}")

    # =====================================================================================
    # POST → Crear reserva
    # =====================================================================================
    def crear_reserva(self, dto: dict):
        """
        dto debe contener los campos EXACTOS del JSON esperado por el controlador:
        {
            "idReserva": int,
            "idUnicoUsuario": int | null,
            "idUnicoUsuarioExterno": int | null,
            "costoTotalReserva": decimal | null,
            "fechaRegistroReserva": ISO8601,
            "fechaInicioReserva": ISO8601,
            "fechaFinalReserva": ISO8601,
            "estadoGeneralReserva": str,
            "estadoReserva": bool
        }
        """

        if "idReserva" not in dto:
            raise ValueError("idReserva es obligatorio en dto.")

        dto["fechaModificacionReserva"] = datetime.now().isoformat()

        try:
            resp = requests.post(self.BASE_URL, json=dto, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al crear reserva: {e}")

    # =====================================================================================
    # PUT → Actualizar reserva
    # =====================================================================================
    def actualizar_reserva(self, id_reserva: int, dto: dict):
        if not id_reserva:
            raise ValueError("ID_RESERVA es obligatorio.")

        dto["fechaModificacionReserva"] = datetime.now().isoformat()

        url = f"{self.BASE_URL}/{id_reserva}"

        try:
            resp = requests.put(url, json=dto, headers=self.headers)

            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al actualizar reserva: {e}")

    # =====================================================================================
    # DELETE → Eliminar reserva (lógico)
    # =====================================================================================
    def eliminar_reserva(self, id_reserva: int):
        if not id_reserva:
            raise ValueError("ID_RESERVA es obligatorio.")

        url = f"{self.BASE_URL}/{id_reserva}"

        try:
            resp = requests.delete(url, headers=self.headers)

            if resp.status_code == 404:
                return False

            resp.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al eliminar reserva: {e}")

    # =====================================================================================
    # INTEGRACIÓN → Crear Pre-Reserva
    # =====================================================================================
    def crear_prereserva(
        self, id_habitacion, fecha_inicio, fecha_fin, numero_huespedes,
        nombre=None, apellido=None, correo=None, tipo_doc=None, documento=None,
        duracion_seg=None, precio_actual=None
    ):
        url = f"{self.BASE_URL}/prereserva"

        payload = {
            "idHabitacion": id_habitacion,
            "fechaInicio": fecha_inicio,
            "fechaFin": fecha_fin,
            "numeroHuespedes": numero_huespedes,
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo,
            "tipoDoc": tipo_doc,
            "documento": documento,
            "duracionSeg": duracion_seg,
            "precioActual": precio_actual
        }

        try:
            resp = requests.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al crear pre-reserva: {e}")

    # =====================================================================================
    # INTEGRACIÓN → Confirmar Reserva
    # =====================================================================================
    def confirmar_reserva(
        self, id_habitacion, id_hold, nombre, apellido, correo, tipo_doc,
        fecha_inicio, fecha_fin, numero_huespedes
    ):
        url = f"{self.BASE_URL}/confirmar"

        payload = {
            "idHabitacion": id_habitacion,
            "idHold": id_hold,
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo,
            "tipoDoc": tipo_doc,
            "fechaInicio": fecha_inicio,
            "fechaFin": fecha_fin,
            "numeroHuespedes": numero_huespedes,
        }

        try:
            resp = requests.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al confirmar reserva: {e}")

    # =====================================================================================
    # INTEGRACIÓN → Buscar datos para reservación
    # =====================================================================================
    def buscar_datos_reserva(self, id_reserva=None):
        url = f"{self.BASE_URL}/buscar"

        payload = {"idReserva": id_reserva}

        try:
            resp = requests.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al buscar datos de reserva: {e}")

cliente = ReservaGestionRest()
pprint(cliente.obtener_reservas())
