import requests
from datetime import datetime
from decimal import Decimal
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from datetime import datetime


###en caso de no ncesitar el formateo forzado de fechas, eliminar esta funcion

def _safe_datetime(val):
    if val is None:
        return None

    # Caso normal: ya es datetime
    if hasattr(val, "isoformat"):
        return val.isoformat()

    # Caso Zeep devolviendo bytes
    if isinstance(val, bytes):
        try:
            # muchos servicios SOAP usan UTF-8 directo
            s = val.decode("utf-8")
            return s
        except:
            pass
        try:
            # intento de decode latin-1
            s = val.decode("latin-1")
            return s
        except:
            return str(val)

    # Si es string, intenta parsear
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val).isoformat()
        except:
            return val

    return str(val)



class PagoGestionSoap:

    def __init__(self):
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/PagoWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ===============================================================
    # NORMALIZADOR → igualito al JSON de REST
    # ===============================================================
    def _normalize(self, p):
        if p is None:
            return None

        d = serialize_object(p)

        # Convertir decimales a float (REST no entiende Decimal)
        def fix(v):
            if isinstance(v, Decimal):
                return float(v)
            return v

        return {
            "IdPago": d.get("IdPago"),
            "IdMetodoPago": d.get("IdMetodoPago"),
            "IdUnicoUsuarioExterno": d.get("IdUnicoUsuarioExterno"),
            "IdUnicoUsuario": d.get("IdUnicoUsuario"),
            "IdFactura": d.get("IdFactura"),
            "CuentaOrigenPago": d.get("CuentaOrigenPago"),
            "CuentaDestinoPago": d.get("CuentaDestinoPago"),
            "MontoTotalPago": fix(d.get("MontoTotalPago")),

            "FechaEmisionPago": _safe_datetime(d.get("FechaEmisionPago")),
            "FechaActualizacionPago": _safe_datetime(d.get("FechaActualizacionPago")),

            "EstadoPago": d.get("EstadoPago"),
            
        }

    # ===============================================================
    # DESNORMALIZADOR → convierte REST → SOAP DTO
    # ===============================================================
    def _denormalize(self, **kwargs):

        return {
            "IdPago": kwargs.get("id_pago"),
            "IdMetodoPago": kwargs.get("id_metodo_pago"),
            "IdUnicoUsuarioExterno": kwargs.get("id_unico_usuario_externo"),
            "IdUnicoUsuario": kwargs.get("id_unico_usuario"),
            "IdFactura": kwargs.get("id_factura"),
            "CuentaOrigenPago": kwargs.get("cuenta_origen"),
            "CuentaDestinoPago": kwargs.get("cuenta_destino"),
            "MontoTotalPago": kwargs.get("monto_total"),
            "FechaEmisionPago": kwargs.get("fecha_emision"),
            "EstadoPago": kwargs.get("estado_pago"),
            "FechaModificacionPago": datetime.now(),
        }

    # ===============================================================
    # REST: obtener_pagos()
    # ===============================================================
    def obtener_pagos(self):
        try:
            result = self.client.service.ObtenerPago()
            arr = serialize_object(result)
            return [self._normalize(r) for r in arr]
        except Fault as e:
            raise Exception(f"Error SOAP al obtener pagos: {e}")

    # ===============================================================
    # REST: obtener_pago_por_id(id_pago)
    # ===============================================================
    def obtener_pago_por_id(self, id_pago):
        try:
            result = self.client.service.ObtenerPagoPorId(id_pago)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener pago {id_pago}: {e}")

    # ===============================================================
    # REST: crear_pago()
    # ===============================================================
    def crear_pago(
        self,
        id_pago,
        id_metodo_pago,
        id_unico_usuario_externo,
        id_unico_usuario,
        id_factura,
        cuenta_origen,
        cuenta_destino,
        monto_total,
        fecha_emision,
        estado_pago=True
    ):

        dto = self._denormalize(
            id_pago=id_pago,
            id_metodo_pago=id_metodo_pago,
            id_unico_usuario_externo=id_unico_usuario_externo,
            id_unico_usuario=id_unico_usuario,
            id_factura=id_factura,
            cuenta_origen=cuenta_origen,
            cuenta_destino=cuenta_destino,
            monto_total=monto_total,
            fecha_emision=fecha_emision,
            estado_pago=estado_pago
        )

        try:
            result = self.client.service.CrearPago(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear pago: {e}")

    # ===============================================================
    # REST: actualizar_pago()
    # ===============================================================
    def actualizar_pago(
        self,
        id_pago,
        id_metodo_pago,
        id_unico_usuario_externo,
        id_unico_usuario,
        id_factura,
        cuenta_origen,
        cuenta_destino,
        monto_total,
        fecha_emision,
        estado_pago
    ):

        dto = self._denormalize(
            id_pago=id_pago,
            id_metodo_pago=id_metodo_pago,
            id_unico_usuario_externo=id_unico_usuario_externo,
            id_unico_usuario=id_unico_usuario,
            id_factura=id_factura,
            cuenta_origen=cuenta_origen,
            cuenta_destino=cuenta_destino,
            monto_total=monto_total,
            fecha_emision=fecha_emision,
            estado_pago=estado_pago
        )

        try:
            result = self.client.service.ActualizarPago(id_pago, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar pago {id_pago}: {e}")

    # ===============================================================
    # REST: eliminar_pago(id_pago)
    # ===============================================================
    def eliminar_pago(self, id_pago):
        try:
            return self.client.service.EliminarPago(id_pago)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar pago {id_pago}: {e}")

