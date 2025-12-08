# PagoGestionRest.py
from __future__ import annotations

import requests
from datetime import datetime


class PagoGestionRest:
    """
    Cliente REST para la entidad PAGO.
    Equivalente al controlador PagoGestionController en C#.

    URL base:
    https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/pago
    """

    BASE_URL = "https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/pago"

    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    # ========================================================
    # GET → Listar pagos
    # ========================================================
    def obtener_pagos(self):
        try:
            resp = requests.get(self.BASE_URL, headers=self.headers)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener pagos: {e}")

    # ========================================================
    # GET → Obtener pago por ID
    # ========================================================
    def obtener_pago_por_id(self, id_pago: int):
        if not id_pago:
            raise ValueError("ID_PAGO es obligatorio.")

        url = f"{self.BASE_URL}/{id_pago}"

        try:
            resp = requests.get(url, headers=self.headers)

            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener pago por ID: {e}")

    # ========================================================
    # POST → Crear pago
    # ========================================================
    def crear_pago(
        self,
        id_pago: int,
        id_metodo_pago: int,
        id_unico_usuario_externo: int | None,
        id_unico_usuario: int,
        id_factura: int,
        cuenta_origen: str | None,
        cuenta_destino: str | None,
        monto_total: float | None,
        fecha_emision: datetime | None,
        estado_pago: bool = True
    ):
        if not id_pago:
            raise ValueError("ID_PAGO es obligatorio.")
        if not id_metodo_pago:
            raise ValueError("ID_METODO_PAGO es obligatorio.")

        payload = {
            "idPago": id_pago,
            "idMetodoPago": id_metodo_pago,
            "idUnicoUsuarioExterno": id_unico_usuario_externo,
            "idUnicoUsuario": id_unico_usuario,
            "idFactura": id_factura,
            "cuentaOrigenPago": cuenta_origen,
            "cuentaDestinoPago": cuenta_destino,
            "montoTotalPago": monto_total,
            "fechaEmisionPago": fecha_emision.isoformat() if fecha_emision else None,
            "estadoPago": estado_pago,
            "fechaModificacionPago": datetime.now().isoformat()
        }

        try:
            resp = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al crear pago: {e}")

    # ========================================================
    # PUT → Actualizar pago
    # ========================================================
    def actualizar_pago(
        self,
        id_pago: int,
        id_metodo_pago: int,
        id_unico_usuario_externo: int | None,
        id_unico_usuario: int,
        id_factura: int,
        cuenta_origen: str | None,
        cuenta_destino: str | None,
        monto_total: float | None,
        fecha_emision: datetime | None,
        estado_pago: bool
    ):
        if not id_pago:
            raise ValueError("ID_PAGO es obligatorio.")

        payload = {
            "idPago": id_pago,
            "idMetodoPago": id_metodo_pago,
            "idUnicoUsuarioExterno": id_unico_usuario_externo,
            "idUnicoUsuario": id_unico_usuario,
            "idFactura": id_factura,
            "cuentaOrigenPago": cuenta_origen,
            "cuentaDestinoPago": cuenta_destino,
            "montoTotalPago": monto_total,
            "fechaEmisionPago": fecha_emision.isoformat() if fecha_emision else None,
            "estadoPago": estado_pago,
            "fechaModificacionPago": datetime.now().isoformat()
        }

        url = f"{self.BASE_URL}/{id_pago}"

        try:
            resp = requests.put(url, json=payload, headers=self.headers)

            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al actualizar pago: {e}")

    # ========================================================
    # DELETE → Eliminación lógica
    # ========================================================
    def eliminar_pago(self, id_pago: int):
        if not id_pago:
            raise ValueError("ID_PAGO es obligatorio.")

        url = f"{self.BASE_URL}/{id_pago}"

        try:
            resp = requests.delete(url, headers=self.headers)

            if resp.status_code == 404:
                return False

            resp.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al eliminar pago: {e}")


