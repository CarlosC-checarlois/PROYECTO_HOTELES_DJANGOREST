import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class ImagenHabitacionGestionSoap:

    def __init__(self):
        # WSDL publicado en Azure (tu servicio SOAP)
        self.wsdl = (
            "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/"
            "ImagenHabitacionWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ========================================================
    # Normalizar objeto Zeep → dict Python
    # ========================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(x):
            return x.isoformat() if x else None

        return {
            "idImagenHabitacion": d.get("IdImagenHabitacion"),
            "idHabitacion": d.get("IdHabitacion"),
            "urlImagen": d.get("UrlImagen"),
            "estadoImagen": d.get("EstadoImagen"),
            "fechaModificacionImagenHabitacion": fmt(d.get("FechaModificacionImagenHabitacion")),
        }

    # ========================================================
    # LISTAR TODAS LAS IMÁGENES DE UNA HABITACIÓN
    # ========================================================
    def listar(self, id_habitacion):
        try:
            r = self.client.service.ObtenerImagenesHabitacion(id_habitacion)
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al listar imágenes: {e}")

    # ========================================================
    # OBTENER POR ID
    # ========================================================
    def obtener_por_id(self, id_imagen):
        try:
            r = self.client.service.ObtenerImagenPorId(id_imagen)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener imagen por ID: {e}")

    # ========================================================
    # CREAR IMAGEN
    # ========================================================
    def crear(self, dto):
        try:
            new_id = self.client.service.AgregarImagenHabitacion(dto)
            return new_id
        except Fault as e:
            raise Exception(f"SOAP Error al crear imagen: {e}")

    # ========================================================
    # ACTUALIZAR IMAGEN
    # ========================================================
    def actualizar(self, id_imagen, dto):
        try:
            r = self.client.service.ActualizarImagenHabitacion(id_imagen, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar imagen: {e}")

    # ========================================================
    # ELIMINAR IMAGEN (lógico)
    # ========================================================
    def eliminar(self, id_imagen):
        try:
            return self.client.service.EliminarImagenHabitacion(id_imagen)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar imagen: {e}")
