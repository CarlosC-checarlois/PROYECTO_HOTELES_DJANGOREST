from pprint import pprint

import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class ImagenHabitacionGestionSoap:

    def __init__(self):

        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/ImagenHabitacionWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()
        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ========================================================
    # Normalizador → pasar de DTO SOAP a dict tipo REST
    # ========================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        fecha = d.get("FechaModificacionImagenHabitacion")
        if hasattr(fecha, "isoformat"):
            fecha = fecha.isoformat()

        return {
            "IdImagenHabitacion": d.get("IdImagenHabitacion"),
            "IdHabitacion": d.get("IdHabitacion"),
            "UrlImagen": d.get("UrlImagen"),
            "EstadoImagen": d.get("EstadoImagen"),
            "FechaModificacionImagenHabitacion": fecha,
        }

    # ========================================================
    # DTO → crear objeto SOAP ImagenHabitacionDto
    # ========================================================
    def _denormalize(self, id_imagen, id_habitacion, url_imagen, estado):
        """
        Construye un objeto del tipo ImagenHabitacionDto definido en el WSDL.
        OJO: si 'ns0:ImagenHabitacionDto' no existe, cambia 'ns0' por 'tns' u otro
        namespace que veas en client.wsdl.dump().
        """
        dto_type = self.client.get_type('ns0:ImagenHabitacionDto')

        return dto_type(
            IdImagenHabitacion=id_imagen,
            IdHabitacion=id_habitacion,
            UrlImagen=url_imagen,
            EstadoImagen=estado,
            FechaModificacionImagenHabitacion=datetime.now(),
        )

    # ========================================================
    # GET → Obtener todas las imágenes
    # ========================================================
    def obtener_imagenes(self):
        try:
            r = self.client.service.ObtenerImagenesHabitacion()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al obtener imágenes: {e}")

    # ========================================================
    # GET → Obtener imagen por ID
    # ========================================================
    def obtener_imagen_por_id(self, id_imagen: int):
        try:
            r = self.client.service.ObtenerImagenPorId(id_imagen)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener imagen por ID: {e}")

    # ========================================================
    # POST → Crear imagen
    # ========================================================
    def crear_imagen(self, id_habitacion: str, url_imagen: str, estado_imagen=True):

        # Para crear, enviamos IdImagenHabitacion = 0 (el servidor asigna el ID real)
        dto = self._denormalize(0, id_habitacion, url_imagen, estado_imagen)

        try:
            new_id = self.client.service.AgregarImagenHabitacion(dto)
            return {"idImagenHabitacion": new_id}
        except Fault as e:
            raise Exception(f"SOAP Error al crear imagen: {e}")

    # ========================================================
    # PUT → Actualizar imagen
    # ========================================================
    def actualizar_imagen(self, id_imagen, id_habitacion, url_imagen, estado_imagen):

        dto = self._denormalize(id_imagen, id_habitacion, url_imagen, estado_imagen)

        try:
            r = self.client.service.ActualizarImagenHabitacion(id_imagen, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar imagen: {e}")

    # ========================================================
    # DELETE → Eliminación lógica
    # ========================================================
    def eliminar_imagen(self, id_imagen):
        try:
            ok = self.client.service.EliminarImagenHabitacion(id_imagen)
            return bool(ok)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar imagen: {e}")


if __name__ == "__main__":
    cliente = ImagenHabitacionGestionSoap()

    print("\nCREAR:")
    resp = cliente.crear_imagen(
        id_habitacion="HACA000015",
        url_imagen="https://miservidor.com/img1.jpg",
        estado_imagen=True
    )
    pprint(resp)
