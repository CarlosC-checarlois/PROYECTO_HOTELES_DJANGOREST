
import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class TipoHabitacionGestionSoap:

    def __init__(self):
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/TipoHabitacionWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

        # Tipo SOAP real
        self.dto_type = self.client.get_type('ns0:TipoHabitacionDto')

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _map_field(self, data: dict, *keys, default=None):
        for k in keys:
            if k in data and data[k] is not None:
                return data[k]
        return default

    def _bool_to_soap(self, value):
        """
        Convierte cualquier valor booleano a formato SOAP: '1' o '0'
        """
        if value is None:
            return "1"  # default true

        if isinstance(value, bool):
            return "1" if value else "0"

        if isinstance(value, int):
            return "1" if value != 0 else "0"

        if isinstance(value, str):
            value = value.strip().lower()
            if value in ["true", "1", "yes", "si"]:
                return "1"
            if value in ["false", "0", "no"]:
                return "0"

        return "1"  # fallback seguro

    # ==========================================================
    # SOAP -> REST NORMALIZADO
    # ==========================================================
    def _normalize(self, d):

        if d is None:
            return None

        d = serialize_object(d)

        nombre = self._map_field(d, "NombreHabitacion", "nombreTipoHabitacion")
        estado = self._map_field(d, "EstadoTipoHabitacion", "estadoTipoHabitacion")
        fecha  = d.get("FechaModificacionTipoHabitacion")

        if hasattr(fecha, "isoformat"):
            fecha = fecha.isoformat()

        return {
            "IdTipoHabitacion": d.get("IdTipoHabitacion"),
            "NombreHabitacion": nombre,
            "EstadoTipoHabitacion": bool(estado) if estado is not None else True,
            "FechaModificacionTipoHabitacion": fecha
        }

    # ==========================================================
    # REST / SOAP -> SOAP DTO REAL
    # ==========================================================
    def _denormalize(self, tipo_dto: dict, id_tipo=0):

        nombre = self._map_field(
            tipo_dto,
            "NombreHabitacion",
            "nombreTipoHabitacion"
        )

        estado = self._map_field(
            tipo_dto,
            "EstadoTipoHabitacion",
            "estadoTipoHabitacion",
            default=True
        )

        if not nombre:
            raise ValueError("El nombre del tipo de habitación es obligatorio.")

        estado_soap = self._bool_to_soap(estado)

        return self.dto_type(
            IdTipoHabitacion=id_tipo,
            NombreHabitacion=nombre,
            EstadoTipoHabitacion=estado_soap,
            FechaModificacionTipoHabitacion=datetime.now()
        )

    # ==========================================================
    # CRUD
    # ==========================================================

    def obtener_tipos(self):
        try:
            r = self.client.service.ObtenerTiposHabitacion()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise ConnectionError(f"SOAP Error al obtener tipos: {e}")

    def obtener_tipo_por_id(self, id_tipo):
        try:
            r = self.client.service.ObtenerTipoHabitacionPorId(id_tipo)
            return self._normalize(r)
        except Fault as e:
            raise ConnectionError(f"SOAP Error al obtener tipo {id_tipo}: {e}")

    def crear_tipo(self, tipo_dto: dict):
        try:

            data = tipo_dto or {}

            # -------------------------------
            # 1) Resolver ID (si viene, se usa; si no, 0)
            # -------------------------------
            id_val = (
                data.get("IdTipoHabitacion")
                or data.get("idTipoHabitacion")
                or 0
            )

            # -------------------------------
            # 2) Resolver NOMBRE (obligatorio)
            # -------------------------------
            nombre = (
                data.get("NombreHabitacion")
                or data.get("nombreTipoHabitacion")
            )
            if not nombre:
                raise ValueError(
                    "El nombre del tipo de habitación es obligatorio "
                    "(NombreHabitacion / nombreTipoHabitacion)."
                )

            # -------------------------------
            # 3) Resolver ESTADO y convertirlo a 1 / 0
            # -------------------------------
            estado_raw = (
                data.get("EstadoTipoHabitacion")
                if "EstadoTipoHabitacion" in data
                else data.get("estadoTipoHabitacion", True)
            )

            # función interna para mapear a '1' / '0'
            def _to_flag(v):
                if v is None:
                    return 1
                if isinstance(v, bool):
                    return 1 if v else 0
                if isinstance(v, (int, float)):
                    return 1 if int(v) != 0 else 0
                if isinstance(v, str):
                    s = v.strip().lower()
                    if s in ("1", "true", "sí", "si", "yes"):
                        return 1
                    if s in ("0", "false", "no"):
                        return 0
                # fallback seguro
                return 1

            estado_flag = _to_flag(estado_raw)

            # -------------------------------
            # 4) Construir DTO SOAP REAL
            # -------------------------------
            dto_soap = self.dto_type(
                IdTipoHabitacion=id_val,
                NombreHabitacion=nombre,
                EstadoTipoHabitacion=estado_flag,
                FechaModificacionTipoHabitacion=datetime.now()
            )

            # -------------------------------
            # 5) Llamar al servicio SOAP
            # -------------------------------
            r = self.client.service.CrearTipoHabitacion(dto_soap)

            # -------------------------------
            # 6) Normalizar respuesta a REST
            # -------------------------------
            r = serialize_object(r) or {}

            # estado puede venir como 1, True, "true", etc.
            estado_resp_raw = r.get("EstadoTipoHabitacion")
            if isinstance(estado_resp_raw, bool):
                estado_resp = estado_resp_raw
            elif isinstance(estado_resp_raw, (int, float)):
                estado_resp = bool(estado_resp_raw)
            elif isinstance(estado_resp_raw, str):
                estado_resp = estado_resp_raw.strip().lower() in ("1", "true", "sí", "si", "yes")
            else:
                estado_resp = True

            fecha = r.get("FechaModificacionTipoHabitacion")
            if hasattr(fecha, "isoformat"):
                fecha = fecha.isoformat()

            # IMPORTANTE: aquí devolvemos el DTO en el formato
            # "REST" que tus vistas esperan (camel bajo).
            return {
                "idTipoHabitacion": r.get("IdTipoHabitacion"),
                "nombreTipoHabitacion": r.get("NombreHabitacion"),
                "estadoTipoHabitacion": estado_resp,
                # mantenemos la descripción que vino de arriba (o vacío)
                "descripcionTipoHabitacion": data.get("descripcionTipoHabitacion", ""),
                "fechaModificacionTipoHabitacion": fecha,
            }

        except Fault as e:
            # errores propios del SOAP
            raise ConnectionError(f"SOAP Error al crear tipo: {e}")
        except Exception as e:
            # errores de validación / mapeo
            raise ValueError(f"Error validación tipo habitación: {e}")

    def actualizar_tipo(self, id_tipo: int, tipo_dto: dict):
        try:
            dto = self._denormalize(tipo_dto, id_tipo)
            r = self.client.service.ActualizarTipoHabitacion(id_tipo, dto)
            return self._normalize(r)
        except Fault as e:
            raise ConnectionError(f"SOAP Error al actualizar tipo {id_tipo}: {e}")
        except Exception as e:
            raise ValueError(f"Error validación tipo habitación: {e}")

    def eliminar_tipo(self, id_tipo: int):
        try:
            ok = self.client.service.EliminarTipoHabitacion(id_tipo)
            return bool(ok)
        except Fault as e:
            raise ConnectionError(f"SOAP Error al eliminar tipo {id_tipo}: {e}")

