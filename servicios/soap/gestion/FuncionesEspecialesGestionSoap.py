
import requests
from datetime import datetime
from decimal import Decimal

from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class FuncionesEspecialesGestionSoap:
    """
    Cliente SOAP para los servicios de Funciones Especiales:
    - crearPreReservaHabitacion
    - ConfirmarReservaInterna
    - EmitirFacturaInterna
    - CancelarPreReserva

    WSDL:
      https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/GestionFuncionesEspecialesWS.asmx?wsdl
    """

    def __init__(self):
        self.wsdl = (
            "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/"
            "GestionFuncionesEspecialesWS.asmx?wsdl"
        )

        # Igual que en FacturaGestionSoap: sesión con verify=False
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ============================================================
    # UTILERÍA
    # ============================================================
    @staticmethod
    def _to_iso(dt):
        """Convierte string o datetime → ISO 8601 (como usas en REST)."""
        if isinstance(dt, datetime):
            return dt.replace(microsecond=0).isoformat()
        if isinstance(dt, str):
            return dt
        raise ValueError("Fecha inválida: debe ser string ISO o datetime.")

    # ============================================================
    # 1) CREAR PRE-RESERVA (SOAP ↔ REST crear_prereserva)
    # ============================================================
    def crear_prereserva(
            self,
            id_habitacion: str,
            fecha_inicio,
            fecha_fin,
            numero_huespedes: int,
            nombre: str = None,
            apellido: str = None,
            correo: str = None,
            tipo_documento: str = None,
            documento: str = None,
            duracion_hold_seg: int = None,
            precio_actual: float = None
    ):
        """
        Mapea a:
          SOAP: crearPreReservaHabitacion(idHabitacion, fechaInicio, fechaFin,
                                          numeroHuespedes, duracionHoldSegundos, precioActual)

        Ojo: SOAP no usa nombre, apellido, correo, etc. (igual que ya viste).
        """

        # Normalizamos fechas como en REST
        fecha_inicio_iso = self._to_iso(fecha_inicio)
        fecha_fin_iso = self._to_iso(fecha_fin)

        try:
            result = self.client.service.crearPreReservaHabitacion(
                id_habitacion,
                fecha_inicio_iso,
                fecha_fin_iso,
                int(numero_huespedes),
                duracion_hold_seg,
                precio_actual,
            )
            data = serialize_object(result)  # normalmente {'IdHold': 'HOCA000060', ...}
            # Imitar la forma del REST, que devuelve un json con IdHold
            return {"IdHold": data.get("IdHold")}
        except Fault as e:
            raise Exception(f"Error SOAP crear_prereserva: {e}")

    # ============================================================
    # 2) CONFIRMAR RESERVA INTERNA (SOAP ↔ REST confirmar_reserva_interna)
    # ============================================================

    def confirmar_reserva_interna(
        self,
        *,
        idHabitacion,
        idHold,
        nombre,
        apellido,
        correo,
        tipoDocumento,
        documento,
        fechaInicio,
        fechaFin,
        numeroHuespedes,
    ):
        history = None
        """
        SOAP:
        ConfirmarReservaInterna(
            string idHabitacion,
            string idHold,
            string nombre,
            string apellido,
            string correo,
            string tipoDocumento,
            string documento,
            DateTime fechaInicio,
            DateTime fechaFin,
            int numeroHuespedes
        )
        """

        # =============================
        # VALIDACIONES BÁSICAS
        # =============================
        obligatorios = {
            "idHabitacion": idHabitacion,
            "idHold": idHold,
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo,
            "fechaInicio": fechaInicio,
            "fechaFin": fechaFin,
            "numeroHuespedes": numeroHuespedes,
        }

        faltantes = [k for k, v in obligatorios.items() if not v]
        if faltantes:
            raise ValueError(f"Faltan campos obligatorios: {', '.join(faltantes)}")

        numeroHuespedes = int(numeroHuespedes)

        # =============================
        # CONVERTIR FECHAS A DATETIME
        # =============================
        if isinstance(fechaInicio, str):
            fechaInicio = datetime.fromisoformat(fechaInicio)

        if isinstance(fechaFin, str):
            fechaFin = datetime.fromisoformat(fechaFin)

        # Helpers para normalizar tipos
        def fix_decimal(v):
            return float(v) if isinstance(v, Decimal) else v

        def fix_datetime(v):
            return v.isoformat() if isinstance(v, datetime) else v

        try:
            print("\n[SOAP] Confirmando reserva con:")
            print("HABITACION:", idHabitacion)
            print("HOLD:", idHold)
            print("FECHA INICIO:", fechaInicio)
            print("FECHA FIN:", fechaFin)
            print("HUESPEDES:", numeroHuespedes)
            from zeep.plugins import HistoryPlugin

            history = HistoryPlugin()
            self.client = Client(wsdl=self.wsdl, plugins=[history])

            service = self.client.bind(
                "GestionFuncionesEspecialesWS",
                "GestionFuncionesEspecialesWSSoap12"
            )

            result = service.ConfirmarReservaInterna(
                idHabitacion,
                idHold,
                nombre,
                apellido,
                correo,
                tipoDocumento,
                documento,
                fechaInicio,
                fechaFin,
                numeroHuespedes
            )

            data = serialize_object(result)  # dict con Decimals y datetimes

            if not isinstance(data, dict):
                # por si acaso, pero en tu caso siempre será dict
                return data

            # =============================
            # NORMALIZAR A FORMATO REST
            # =============================
            salida = {
                # CAMPOS PRINCIPALES (mismo nombre que REST)
                "IdReserva": data.get("IdReserva") or data.get("idReserva"),
                "CostoTotalReserva": fix_decimal(
                    data.get("CostoTotalReserva") or data.get("costoTotalReserva")
                ),
                "FechaRegistro": fix_datetime(
                    data.get("FechaRegistro") or data.get("fechaRegistro")
                ),
                "FechaInicio": fix_datetime(
                    data.get("FechaInicio") or data.get("fechaInicio")
                ),
                "FechaFin": fix_datetime(
                    data.get("FechaFin") or data.get("fechaFin")
                ),
                "EstadoGeneral": (
                    data.get("EstadoGeneral") or data.get("estadoGeneral") or ""
                ).strip(),
                "Estado": data.get("Estado") or data.get("estado"),

                # DATOS DEL CLIENTE
                "Nombre": data.get("Nombre") or data.get("nombre"),
                "Apellido": data.get("Apellido") or data.get("apellido"),
                "Correo": data.get("Correo") or data.get("correo"),
                "TipoDocumento": data.get("TipoDocumento") or data.get("tipoDocumento"),

                # DATOS DE LA HABITACIÓN
                "Habitacion": data.get("Habitacion") or data.get("habitacion"),
                "PrecioNormal": fix_decimal(
                    data.get("PrecioNormal") or data.get("precioNormal")
                ),
                "PrecioActual": fix_decimal(
                    data.get("PrecioActual") or data.get("precioActual")
                ),
                "Capacidad": data.get("Capacidad") or data.get("capacidad"),

                "_links": None,  # para imitar al microservicio REST
            }

            return salida

        except Fault as e:

            print("\n📨 SOAP REQUEST ENVIADO:")
            from lxml import etree

            print("\n📨 SOAP REQUEST ENVIADO:")
            print(etree.tostring(history.last_sent["envelope"], pretty_print=True).decode())

            print("\n📩 SOAP RESPONSE RECIBIDO:")
            print(etree.tostring(history.last_received["envelope"], pretty_print=True).decode())

            raise Exception(f"Error SOAP confirmar_reserva_interna: {e}")

    # ============================================================
    # 3) EMITIR FACTURA INTERNA (SOAP ↔ REST emitir_factura_interna)
    # ============================================================
    def emitir_factura_interna(
            self,
            *,
            idReserva: int,
            correo: str,
            nombre: str,
            apellido: str,
            tipoDocumento: str = "",
            documento: str = "",
    ):
        """
        Mapea contra:
          SOAP: EmitirFacturaInterna(idReserva, correo, nombre, apellido, tipoDocumento, documento)
        """

        # VALIDACIONES IGUALES A REST
        if not idReserva:
            raise ValueError("idReserva es obligatorio")
        if not correo:
            raise ValueError("correo es obligatorio")
        if not nombre:
            raise ValueError("nombre es obligatorio")
        if not apellido:
            raise ValueError("apellido es obligatorio")

        try:
            result = self.client.service.EmitirFacturaInterna(
                int(idReserva),
                correo,
                nombre,
                apellido,
                tipoDocumento or "",
                documento or "",
            )
            data = serialize_object(result)

            # Normalización simple tipo REST
            # Ajusta estos campos según lo que retorne tu API
            def fix_decimal(v):
                if isinstance(v, Decimal):
                    return float(v)
                return v
            out = {}
            if isinstance(data, dict):
                for k, v in data.items():
                    key = k[0].lower() + k[1:] if k and k[0].isupper() else k
                    out[key] = fix_decimal(v)
                return out

            return data

        except Fault as e:
            raise Exception(f"Error SOAP emitir_factura_interna: {e}")

    # ============================================================
    # 4) CANCELAR PRE-RESERVA (SOAP ↔ REST cancelar_prereserva)
    # ============================================================
    def cancelar_prereserva(self, id_hold: str):
        """
        SOAP:
          CancelarPreReserva(string idHold)

        REST:
          DELETE /prereserva/{idHold}
          → { "ok": true, "mensaje": "...", "raw": ... }
        """
        if not id_hold:
            raise ValueError("id_hold es obligatorio.")

        try:
            result = self.client.service.CancelarPreReserva(id_hold)
            data = serialize_object(result)

            # Normalización tipo REST
            return {
                "ok": True,
                "mensaje": "Pre-reserva cancelada correctamente.",
                "raw": data,
            }
        except Fault as e:
            raise Exception(f"Error SOAP cancelar_prereserva: {e}")


