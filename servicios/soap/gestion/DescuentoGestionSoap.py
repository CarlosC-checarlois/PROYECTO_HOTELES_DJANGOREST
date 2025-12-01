import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from datetime import datetime


class DescuentosGestionSoap:

    def __init__(self):
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/DescuentoWS.asmx?wsdl"

        # Permitir certificados autofirmados (Azure/IIS)
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

        # Obtenemos el tipo DTO real
        self.DescuentoDto = self.client.get_type("ns0:DescuentoDto")

    # ============================================================
    # NORMALIZACIÓN → Formato idéntico al REST
    # ============================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        return {
            "IdDescuento": d.get("IdDescuento"),
            "NombreDescuento": d.get("NombreDescuento"),
            "ValorDescuento": float(d.get("ValorDescuento")) if d.get("ValorDescuento") else None,
            "FechaInicioDescuento": (
                d.get("FechaInicioDescuento").isoformat()
                if d.get("FechaInicioDescuento") else None
            ),
            "FechaFinDescuento": (
                d.get("FechaFinDescuento").isoformat()
                if d.get("FechaFinDescuento") else None
            ),
            "EstadoDescuento": d.get("EstadoDescuento"),
            "FechaModificacionDescuento": (
                d.get("FechaModificacionDescuento").isoformat()
                if d.get("FechaModificacionDescuento") else None
            )
        }

    # ============================================================
    # CONSTRUCTOR DTO → Igual que el payload REST
    # ============================================================
    def _build_dto(self, id_descuento, nombre, valor, fecha_inicio, fecha_fin, estado):
        return self.DescuentoDto(
            IdDescuento=id_descuento,
            NombreDescuento=nombre,
            ValorDescuento=valor,
            FechaInicioDescuento=fecha_inicio if fecha_inicio else None,
            FechaFinDescuento=fecha_fin if fecha_fin else None,
            EstadoDescuento=estado,
            FechaModificacionDescuento=datetime.now(),
        )

    # ============================================================
    # GET → obtener_descuentos()
    # ============================================================
    def obtener_descuentos(self):
        try:
            resp = self.client.service.ObtenerDescuentos()
            data = serialize_object(resp)

            # Si ya viene como lista
            if isinstance(data, list):
                return [self._normalize(x) for x in data]

            # Si viene como dict con key 'DescuentoDto'
            if isinstance(data, dict) and "DescuentoDto" in data:
                return [self._normalize(x) for x in data["DescuentoDto"]]

            return []

        except Fault as e:
            raise Exception(f"Error SOAP al obtener descuentos: {e}")

    # ============================================================
    # GET → obtener_descuento_por_id()
    # ============================================================
    def obtener_descuento_por_id(self, id_descuento):
        try:
            resp = self.client.service.ObtenerDescuentoPorId(id_descuento)
            return self._normalize(resp)

        except Fault as e:
            raise Exception(f"Error SOAP al obtener descuento {id_descuento}: {e}")

    # ============================================================
    # POST → crear_descuento()
    # ============================================================
    def crear_descuento(self, id_descuento, nombre, valor, fecha_inicio=None, fecha_fin=None, estado=True):
        try:
            dto = self._build_dto(id_descuento, nombre, valor, fecha_inicio, fecha_fin, estado)
            resp = self.client.service.CrearDescuento(dto)
            return self._normalize(resp)

        except Fault as e:
            raise Exception(f"Error SOAP al crear descuento: {e}")

    # ============================================================
    # PUT → actualizar_descuento()
    # ============================================================
    def actualizar_descuento(self, id_descuento, nombre, valor, fecha_inicio, fecha_fin, estado):
        try:
            dto = self._build_dto(id_descuento, nombre, valor, fecha_inicio, fecha_fin, estado)
            resp = self.client.service.ActualizarDescuento(id_descuento, dto)
            return self._normalize(resp)

        except Fault as e:
            raise Exception(f"Error SOAP al actualizar descuento {id_descuento}: {e}")

    # ============================================================
    # DELETE → eliminar_descuento()
    # ============================================================
    def eliminar_descuento(self, id_descuento):
        try:
            result = self.client.service.EliminarDescuento(id_descuento)
            return bool(result)

        except Fault as e:
            raise Exception(f"Error SOAP al eliminar descuento {id_descuento}: {e}")
        
