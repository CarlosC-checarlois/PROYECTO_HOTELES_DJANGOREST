# factura_rest.py
import requests


class FacturaRest:
    """
    Cliente REST para emitir facturas.
    Equivalente al FacturaController en C#.
    """

    BASE_URL = "https://reca.azurewebsites.net/api/v1/hoteles/invoices"

    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    def emitir_factura(self, id_reserva: int, correo: str = None):
        """
        Envía una solicitud POST para emitir una factura.
        :param id_reserva: ID numérico de la reserva (obligatorio).
        :param correo: correo electrónico opcional para enviar la factura.
        :return: JSON con los datos de la factura emitida.
        """

        # ===== VALIDACIONES =====
        if id_reserva is None or id_reserva <= 0:
            raise ValueError("El campo 'id_reserva' debe ser mayor que 0.")

        # ===== BODY =====
        payload = {"idReserva": id_reserva}
        if correo:
            payload["correo"] = correo

        # ===== PETICIÓN =====
        try:
            response = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al conectar con el servicio de facturación: {e}")
