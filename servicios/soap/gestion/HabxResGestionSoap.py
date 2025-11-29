import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class HabxResGestionSoap:

    def __init__(self):
        # WSDL publicado en Azure
        self.wsdl = (
            "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/"
            "HabxResWS.asmx?wsdl"
        )

        # Azure → certificados intermedios, permitimos verify=False
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ==========================================================
    # NORMALIZACIÓN → deja igual que REST
    # ==========================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(x):
            return x.isoformat() if x else None

        return {
            "idHabxRes": d.get("IdHabxRes"),
            "idHabitacion": d.get("IdHabitacion"),
            "idReserva": d.get("IdReserva"),
            "capacidadReservaHabxRes": d.get("CapacidadReservaHabxRes"),
            "costoCalculadoHabxRes": d.get("CostoCalculadoHabxRes"),
            "descuentoHabxRes": d.get("DescuentoHabxRes"),
            "impuestosHabxRes": d.get("ImpuestosHabxRes"),
            "estadoHabxRes": d.get("EstadoHabxRes"),
            "fechaModificacionHabxRes": fmt(d.get("FechaModificacionHabxRes"))
        }

    # ==========================================================
    # LISTAR
    # ==========================================================
    def listar(self):
        try:
            r = self.client.service.ObtenerHabxRes()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"Error SOAP al listar HabxRes: {e}")

    # ==========================================================
    # OBTENER POR ID
    # ==========================================================
    def obtener_por_id(self, id_habxres):
        try:
            r = self.client.service.ObtenerHabxResPorId(id_habxres)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener HabxRes {id_habxres}: {e}")

    # ==========================================================
    # CREAR
    # ==========================================================
    def crear(self, dto):
        try:
            r = self.client.service.CrearHabxRes(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al crear HabxRes: {e}")

    # ==========================================================
    # ACTUALIZAR
    # ==========================================================
    def actualizar(self, id_habxres, dto):
        try:
            r = self.client.service.ActualizarHabxRes(id_habxres, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar HabxRes {id_habxres}: {e}")

    # ==========================================================
    # ELIMINAR
    # ==========================================================
    def eliminar(self, id_habxres):
        try:
            return self.client.service.EliminarHabxRes(id_habxres)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar HabxRes {id_habxres}: {e}")
