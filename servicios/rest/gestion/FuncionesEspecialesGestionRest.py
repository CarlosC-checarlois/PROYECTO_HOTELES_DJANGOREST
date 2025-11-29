# funciones_especiales_gestion_rest.py

import requests
from datetime import datetime


class FuncionesEspecialesGestionRest:
    """
    Cliente REST para los servicios:
    - Crear pre-reserva con HOLD
    - Confirmar reserva para usuario interno
    - Emitir factura para usuario interno

    Base URL:
    https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/v1/hoteles/funciones-especiales
    """

    BASE_URL = "https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/v1/hoteles/funciones-especiales"

    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    # ============================================================
    # UTILERÍA
    # ============================================================
    @staticmethod
    def _to_iso(dt):
        """Convierte string o datetime → ISO 8601"""
        if isinstance(dt, datetime):
            return dt.isoformat()
        if isinstance(dt, str):
            return dt
        raise ValueError("Fecha inválida: debe ser string ISO o datetime.")

    # ============================================================
    # POST → Crear PRE-RESERVA
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
        url = f"{self.BASE_URL}/prereserva"

        payload = {
            "idHabitacion": id_habitacion,
            "fechaInicio": self._to_iso(fecha_inicio),
            "fechaFin": self._to_iso(fecha_fin),
            "numeroHuespedes": numero_huespedes,
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo,
            "tipoDocumento": tipo_documento,
            "documento": documento,
            "duracionHoldSeg": duracion_hold_seg,
            "precioActual": precio_actual
        }

        try:
            resp = requests.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al crear la pre-reserva: {e}")

    # ============================================================
    # POST → Confirmar reserva de usuario interno
    # ============================================================
    def confirmar_reserva_interna(
        self,
        id_habitacion: str,
        id_hold: str,
        id_unico_usuario: int,
        fecha_inicio,
        fecha_fin,
        numero_huespedes: int
    ):
        url = f"{self.BASE_URL}/confirmar-usuario-interno"

        payload = {
            "idHabitacion": id_habitacion,
            "idHold": id_hold,
            "idUnicoUsuario": id_unico_usuario,
            "fechaInicio": self._to_iso(fecha_inicio),
            "fechaFin": self._to_iso(fecha_fin),
            "numeroHuespedes": numero_huespedes
        }

        try:
            resp = requests.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al confirmar la reserva interna: {e}")

    # ============================================================
    # POST → Emitir factura (usuario interno)
    # ============================================================

    def emitir_factura_interna(
            self,
            id_reserva: int,
            correo: str = None,
            url_factura: str = None
    ):
        url = f"{self.BASE_URL}/emitir-interno"

        payload = {
            "IdReserva": id_reserva,
            "Correo": correo,
            "UrlFactura": url_factura,
            "CuentaOrigen": "194",  # ← valor quemado
            "CuentaDestino": "196"  # ← valor quemado
        }

        try:
            resp = requests.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al emitir la factura interna: {e}")

    def cancelar_prereserva(self, id_hold: str):
        """
        Cancela una pre-reserva (HOLD activo) usando el endpoint:
        POST /cancelar-prereserva
        """
        if not id_hold:
            raise ValueError("id_hold es obligatorio.")

        url = f"{self.BASE_URL}/cancelar-prereserva"
        payload = {"idHold": id_hold}

        try:
            resp = requests.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al cancelar la pre-reserva: {e}")
# ============================================================
# PRUEBA RÁPIDA (Sólo si se ejecuta este archivo directamente)
# ============================================================
if __name__ == "__main__":
    api = FuncionesEspecialesGestionRest()

    try:
        resultado = api.emitir_factura_interna(
            id_reserva=113,
            correo="dancarranza@outlook.com",
        )

        print("=== RESPUESTA API ===")
        print(resultado)

    except Exception as e:
        print("ERROR EJECUTANDO CONFIRMAR RESERVA:", e)