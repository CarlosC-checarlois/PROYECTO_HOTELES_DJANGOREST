# buscar_habitaciones_soap.py
import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from datetime import datetime
from decimal import Decimal


class HabitacionesSoap:
    """
    Cliente SOAP equivalente a HabitacionesRest.buscar_habitaciones()
    """

    WSDL = "https://intehoca-eheqd8h6bvdyfqfy.canadacentral-01.azurewebsites.net/BuscarHabitacionesWS.asmx?WSDL"

    def __init__(self):
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.WSDL, transport=transport)

    # =======================================
    # CONVERTIR STRING → DATETIME
    # =======================================
    def _parse_date(self, date):
        if not date:
            return None
        if isinstance(date, datetime):
            return date
        return datetime.fromisoformat(str(date))

    # =======================================
    # MÉTODO PRINCIPAL
    # =======================================
    def buscar_habitaciones(
        self,
        date_from=None,
        date_to=None,
        tipo_habitacion=None,
        capacidad=None,
        precio_min=None,
        precio_max=None,
    ):
        try:
            # =====================================
            # NORMALIZAR ARGUMENTOS
            # =====================================
            date_from = self._parse_date(date_from)
            date_to = self._parse_date(date_to)

            capacidad = int(capacidad) if capacidad is not None else None
            precio_min = float(precio_min) if precio_min is not None else None
            precio_max = float(precio_max) if precio_max is not None else None

            # =====================================
            # LLAMADA SOAP
            # =====================================
            result = self.client.service.buscarHabitaciones(
                date_from,
                date_to,
                tipo_habitacion,
                capacidad,
                precio_min,
                precio_max,
            )

            data = serialize_object(result)

            # =====================================
            # NORMALIZAR JSON
            # =====================================
            habitaciones = []

            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = data.get("HabitacionListItemDto") or data.get("habitacionListItemDto") or []
            else:
                return []

            for h in items:
                if not isinstance(h, dict):
                    continue

                obj = {}
                for k, v in h.items():

                    # CamelCase → camelCase
                    key = k[0].lower() + k[1:] if k and k[0].isupper() else k

                    # Decimal → float
                    if isinstance(v, Decimal):
                        v = float(v)

                    # datetime → ISO
                    if hasattr(v, "isoformat"):
                        v = v.isoformat()

                    obj[key] = v

                habitaciones.append(obj)

            return habitaciones

        except Fault as e:
            raise Exception(f"Error SOAP buscar_habitaciones: {e}")
