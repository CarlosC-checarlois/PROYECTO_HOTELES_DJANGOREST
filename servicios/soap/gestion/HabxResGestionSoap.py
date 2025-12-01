import requests
from datetime import datetime
from decimal import Decimal
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class HabxResGestionSoap:

    def __init__(self):
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/HabxResWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()
        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # --------------------------------------------------------------
    # INTERNAL HELPERS
    # --------------------------------------------------------------
    def _fix_decimal(self, value):
        if isinstance(value, Decimal):
            return float(value)
        return value

    def _normalize(self, d):
        """
        Convierte el objeto SOAP en el mismo formato JSON que REST.
        """
        if d is None:
            return None

        d = serialize_object(d)

        fecha = d.get("FechaModificacionHabxRes")
        if hasattr(fecha, "isoformat"):
            fecha = fecha.isoformat()

        return {
            "IdHabxRes": d.get("IdHabxRes"),
            "IdHabitacion": d.get("IdHabitacion"),
            "IdReserva": d.get("IdReserva"),
            "CapacidadReservaHabxRes": d.get("CapacidadReservaHabxRes"),
            "CostoCalculadoHabxRes": self._fix_decimal(d.get("CostoCalculadoHabxRes")),
            "DescuentoHabxRes": self._fix_decimal(d.get("DescuentoHabxRes")),
            "ImpuestosHabxRes": self._fix_decimal(d.get("ImpuestosHabxRes")),
            "EstadoHabxRes": d.get("EstadoHabxRes"),
            "FechaModificacionHabxRes": fecha
        }

    def _denormalize(self, id_habxres, id_habitacion, id_reserva,
                      capacidad, costo, descuento, impuestos, estado):
        """
        Construye el DTO idéntico al que SOAP espera.
        """
        return {
            "IdHabxRes": id_habxres,
            "IdHabitacion": id_habitacion,
            "IdReserva": id_reserva,
            "CapacidadReservaHabxRes": capacidad,
            "CostoCalculadoHabxRes": costo,
            "DescuentoHabxRes": descuento,
            "ImpuestosHabxRes": impuestos,
            "EstadoHabxRes": estado,
            "FechaModificacionHabxRes": datetime.now()
        }

    # --------------------------------------------------------------
    # GET → obtener lista 
    # --------------------------------------------------------------
    def obtener_habxres(self):
        try:
            result = self.client.service.ObtenerHabxRes()
            result = serialize_object(result)

            return [self._normalize(x) for x in result]

        except Fault as e:
            raise Exception(f"Error SOAP al obtener HabxRes: {e}")

    # --------------------------------------------------------------
    # GET → obtener por ID 
    # --------------------------------------------------------------
    def obtener_por_id(self, id_habxres):
        try:
            r = self.client.service.ObtenerHabxResPorId(id_habxres)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener HabxRes {id_habxres}: {e}")

    # --------------------------------------------------------------
    # POST → crear 
    # --------------------------------------------------------------
    def crear_habxres(self,
                       id_habxres,
                       id_habitacion,
                       id_reserva,
                       capacidad=None,
                       costo=None,
                       descuento=None,
                       impuestos=None,
                       estado=True):

        dto = self._denormalize(
            id_habxres, id_habitacion, id_reserva,
            capacidad, costo, descuento, impuestos, estado
        )

        try:
            r = self.client.service.CrearHabxRes(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al crear HabxRes: {e}")

    # --------------------------------------------------------------
    # PUT → actualizar 
    # --------------------------------------------------------------
    def actualizar_habxres(self,
                           id_habxres,
                           id_habitacion,
                           id_reserva,
                           capacidad=None,
                           costo=None,
                           descuento=None,
                           impuestos=None,
                           estado=None):

        dto = self._denormalize(
            id_habxres, id_habitacion, id_reserva,
            capacidad, costo, descuento, impuestos, estado
        )

        try:
            r = self.client.service.ActualizarHabxRes(id_habxres, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar HabxRes {id_habxres}: {e}")

    # --------------------------------------------------------------
    # DELETE → eliminar lógica 
    # --------------------------------------------------------------
    def eliminar_habxres(self, id_habxres):
        try:
            return self.client.service.EliminarHabxRes(id_habxres)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar HabxRes {id_habxres}: {e}")


