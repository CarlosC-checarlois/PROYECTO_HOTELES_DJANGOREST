import requests
from datetime import datetime
from decimal import Decimal

from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class HabitacionesGestionSoap:

    def __init__(self):
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/HabitacionWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()
        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # =============================================================
    # Normalizador → Igual que REST
    # =============================================================
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        # Convertir Decimal → float
        def num(x):
            return float(x) if isinstance(x, Decimal) else x

        def iso(x):
            return x.isoformat() if hasattr(x, "isoformat") else x

        return {
            "IdHabitacion": d.get("IdHabitacion"),
            "IdTipoHabitacion": d.get("IdTipoHabitacion"),
            "IdCiudad": d.get("IdCiudad"),
            "IdHotel": d.get("IdHotel"),
            "NombreHabitacion": d.get("NombreHabitacion"),
            "PrecioNormalHabitacion": num(d.get("PrecioNormalHabitacion")),
            "PrecioActualHabitacion": num(d.get("PrecioActualHabitacion")),
            "CapacidadHabitacion": d.get("CapacidadHabitacion"),
            "EstadoHabitacion": d.get("EstadoHabitacion"),
            "EstadoActivoHabitacion": d.get("EstadoActivoHabitacion"),
            "FechaRegistroHabitacion": iso(d.get("FechaRegistroHabitacion")),
            "FechaModificacionHabitacion": iso(d.get("FechaModificacionHabitacion")),
        }

    # =============================================================
    # Denormalizador → Construir DTO igual que REST
    # =============================================================
    def _denormalize(self, **data):
        return {
            "IdHabitacion": data["idHabitacion"],
            "IdTipoHabitacion": data["idTipoHabitacion"],
            "IdCiudad": data["idCiudad"],
            "IdHotel": data["idHotel"],
            "NombreHabitacion": data.get("nombreHabitacion"),
            "PrecioNormalHabitacion": data.get("precioNormalHabitacion"),
            "PrecioActualHabitacion": data.get("precioActualHabitacion"),
            "CapacidadHabitacion": data.get("capacidadHabitacion"),
            "EstadoHabitacion": data.get("estadoHabitacion"),
            "EstadoActivoHabitacion": data.get("estadoActivoHabitacion"),
            "FechaRegistroHabitacion": datetime.now(),
            "FechaModificacionHabitacion": datetime.now(),
        }

    # =============================================================
    # GET → obtener_habitaciones (igual REST)
    # =============================================================
    def obtener_habitaciones(self):
        try:
            result = self.client.service.ObtenerHabitaciones()
            result = serialize_object(result)
            return [self._normalize(x) for x in result]
        except Fault as e:
            raise Exception(f"Error SOAP al obtener habitaciones: {e}")

    # =============================================================
    # GET → obtener_por_id (igual REST)
    # =============================================================
    def obtener_por_id(self, id_habitacion):
        try:
            result = self.client.service.ObtenerHabitacionPorId(id_habitacion)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener habitación ({id_habitacion}): {e}")

    # =============================================================
    # POST → crear_habitacion (igual REST)
    # =============================================================
    def crear_habitacion(
        self,
        id_habitacion,
        id_tipo_habitacion,
        id_ciudad,
        id_hotel,
        nombre_habitacion=None,
        precio_normal=None,
        precio_actual=None,
        capacidad=None,
        estado=None,
        estado_activo=True,
        fecha_registro=None
    ):
        dto = self._denormalize(
            idHabitacion=id_habitacion,
            idTipoHabitacion=id_tipo_habitacion,
            idCiudad=id_ciudad,
            idHotel=id_hotel,
            nombreHabitacion=nombre_habitacion,
            precioNormalHabitacion=precio_normal,
            precioActualHabitacion=precio_actual,
            capacidadHabitacion=capacidad,
            estadoHabitacion=estado,
            estadoActivoHabitacion=estado_activo
        )

        try:
            result = self.client.service.CrearHabitacion(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear habitación: {e}")

    # =============================================================
    # PUT → actualizar_habitacion (igual REST)
    # =============================================================
    def actualizar_habitacion(
        self,
        id_habitacion,
        id_tipo_habitacion,
        id_ciudad,
        id_hotel,
        nombre_habitacion=None,
        precio_normal=None,
        precio_actual=None,
        capacidad=None,
        estado=None,
        estado_activo=None
    ):
        dto = self._denormalize(
            idHabitacion=id_habitacion,
            idTipoHabitacion=id_tipo_habitacion,
            idCiudad=id_ciudad,
            idHotel=id_hotel,
            nombreHabitacion=nombre_habitacion,
            precioNormalHabitacion=precio_normal,
            precioActualHabitacion=precio_actual,
            capacidadHabitacion=capacidad,
            estadoHabitacion=estado,
            estadoActivoHabitacion=estado_activo
        )

        try:
            result = self.client.service.ActualizarHabitacion(id_habitacion, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar habitación: {e}")

    # =============================================================
    # DELETE → eliminar_habitacion (igual REST)
    # =============================================================
    def eliminar_habitacion(self, id_habitacion):
        try:
            return self.client.service.EliminarHabitacion(id_habitacion)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar habitación ({id_habitacion}): {e}")
