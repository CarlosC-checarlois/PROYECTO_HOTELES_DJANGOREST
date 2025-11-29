# facturas_gestion_rest.py
from pprint import pprint

import requests
from datetime import datetime

from servicios.rest.integracion.FacturaRest import FacturaRest


class FacturasGestionRest:
    """
    Cliente REST para el recurso FACTURAS.
    Equivale a FacturasGestionController en C#.

    BASE:
    https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/facturas
    """

    BASE_URL = "https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/facturas"

    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    # =====================================================================
    # GET → Obtener todas las facturas
    # =====================================================================
    def obtener_facturas(self):
        try:
            resp = requests.get(self.BASE_URL, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener facturas: {e}")

    # =====================================================================
    # GET → Obtener factura por ID
    # =====================================================================
    def obtener_por_id(self, id_factura: int):
        if id_factura <= 0:
            raise ValueError("El id_factura debe ser mayor que 0.")

        url = f"{self.BASE_URL}/{id_factura}"

        try:
            resp = requests.get(url, headers=self.headers)

            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener la factura: {e}")

    # =====================================================================
    # POST → Crear factura
    # =====================================================================
    def crear_factura(
        self,
        id_factura: int,
        id_reserva: int,
        subtotal=None,
        descuento=None,
        impuesto=None,
        total=None,
        url_pdf: str = None
    ):
        if id_factura <= 0:
            raise ValueError("IdFactura es obligatorio y debe ser mayor a 0.")

        payload = {
            "idFactura": id_factura,
            "idReserva": id_reserva,
            "subtotal": subtotal,
            "descuento": descuento,
            "impuesto": impuesto,
            "total": total,
            "urlPdf": url_pdf,
            "fechaEmision": datetime.now().isoformat()
        }

        try:
            resp = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al crear la factura: {e}")

    # =====================================================================
    # PUT → Actualizar factura
    # =====================================================================
    def actualizar_factura(
        self,
        id_factura: int,
        id_reserva: int,
        subtotal=None,
        descuento=None,
        impuesto=None,
        total=None,
        url_pdf: str = None
    ):
        if id_factura <= 0:
            raise ValueError("ID inválido.")

        payload = {
            "idFactura": id_factura,
            "idReserva": id_reserva,
            "subtotal": subtotal,
            "descuento": descuento,
            "impuesto": impuesto,
            "total": total,
            "urlPdf": url_pdf
        }

        url = f"{self.BASE_URL}/{id_factura}"

        try:
            resp = requests.put(url, json=payload, headers=self.headers)

            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al actualizar la factura: {e}")

    # =====================================================================
    # DELETE → Eliminar lógico
    # =====================================================================
    def eliminar_factura(self, id_factura: int):
        if id_factura <= 0:
            raise ValueError("El ID debe ser mayor a 0.")

        url = f"{self.BASE_URL}/{id_factura}"

        try:
            resp = requests.delete(url, headers=self.headers)

            if resp.status_code == 404:
                return False

            resp.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al eliminar la factura: {e}")
