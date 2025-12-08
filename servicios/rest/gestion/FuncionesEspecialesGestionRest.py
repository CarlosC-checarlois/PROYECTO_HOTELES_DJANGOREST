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
            "precioActual": precio_actual,
        }

        try:
            resp = requests.post(url, json=payload, headers=self.headers)
        except requests.exceptions.RequestException as e:
            # Error de red, DNS, timeout, etc.
            raise ConnectionError(f"No se pudo conectar con el servidor de pre-reservas: {e}")

        # Aquí ya hay respuesta HTTP, aunque sea 500
        if resp.status_code >= 400:
            # Intenta leer cuerpo como texto para debug
            try:
                cuerpo = resp.text
            except Exception:
                cuerpo = "<no se pudo leer el cuerpo>"

            raise ConnectionError(
                f"Error al crear la pre-reserva "
                f"(HTTP {resp.status_code}): {cuerpo}"
            )

        # Si todo fue bien, devolvemos JSON
        try:
            return resp.json()
        except ValueError:
            raise ConnectionError(
                f"El servidor devolvió una respuesta no JSON: {resp.text}"
            )

    def confirmar_reserva_interna(
            self,
            *,
            idHabitacion: str,
            idHold: str,
            nombre: str,
            apellido: str,
            correo: str,
            tipoDocumento: str,
            documento: str,
            fechaInicio,
            fechaFin,
            numeroHuespedes: int,
    ):
        """
        Envía el payload EXACTO como Swagger:

        {
          "idHabitacion": "HACA000417",
          "idHold": "HOCA000028",
          "nombre": "Prueba",
          "apellido": "Automatica",
          "correo": "prueba_auto@hotel.com",
          "tipoDocumento": "CEDULA",
          "documento": "0123456789",
          "fechaInicio": "2025-12-11T15:00:00",
          "fechaFin": "2025-12-12T11:00:00",
          "numeroHuespedes": 1
        }
        """

        url = f"{self.BASE_URL}/confirmar-usuario-interno"

        # ==========================
        # VALIDACIONES
        # ==========================
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

        try:
            numeroHuespedes = int(numeroHuespedes)
            if numeroHuespedes <= 0:
                raise ValueError
        except:
            raise ValueError("numeroHuespedes debe ser un número entero mayor que 0")

        # ==========================
        # PAYLOAD EXACTO SWAGGER
        # ==========================
        payload = {
            "idHabitacion": idHabitacion,
            "idHold": idHold,
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo,
            "tipoDocumento": tipoDocumento,
            "documento": documento,
            "fechaInicio": self._to_iso(fechaInicio),
            "fechaFin": self._to_iso(fechaFin),
            "numeroHuespedes": numeroHuespedes,
        }

        print("\n[CONFIRMAR_INTERNO] Payload enviado a API:")
        print(payload)
        print("=======================================")

        # ==========================
        # REQUEST HTTP
        # ==========================
        try:
            resp = requests.post(url, json=payload, headers=self.headers, timeout=20)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"[ERROR CONFIRMAR] {e}")

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
        Envía exactamente como Swagger vía query params:

        POST /emitir-interno?idReserva=123
                          &correo=a@mail.com
                          &nombre=Juan
                          &apellido=Perez
                          &tipoDocumento=CEDULA
                          &documento=0123456789
        """

        url = f"{self.BASE_URL}/emitir-interno"

        # ==========================
        # VALIDACIONES BÁSICAS
        # ==========================
        if not idReserva:
            raise ValueError("idReserva es obligatorio")
        if not correo:
            raise ValueError("correo es obligatorio")
        if not nombre:
            raise ValueError("nombre es obligatorio")
        if not apellido:
            raise ValueError("apellido es obligatorio")

        # ==========================
        # PARAMS EXACTOS COMO API
        # ==========================
        params = {
            "idReserva": int(idReserva),
            "correo": correo,
            "nombre": nombre,
            "apellido": apellido,
            "tipoDocumento": tipoDocumento or "",
            "documento": documento or "",
        }

        print("\n[FACTURA_INTERNO] Query enviada a API:")
        print(params)
        print("=====================================")

        # ==========================
        # REQUEST HTTP
        # ==========================
        try:
            resp = requests.post(url, params=params, headers=self.headers, timeout=15)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"[ERROR FACTURA] {e}")

    def cancelar_prereserva(self, id_hold: str):
        """
        Cancela una pre-reserva (HOLD activo) usando el endpoint:
        DELETE /prereserva/{idHold}

        Ejemplo de respuesta:
        { "mensaje": "Pre-reserva cancelada correctamente." }
        """
        if not id_hold:
            raise ValueError("id_hold es obligatorio.")

        # ✅ URL correcta, con el idHold en la ruta
        url = f"{self.BASE_URL}/prereserva/{id_hold}"

        try:
            # DELETE, sin body
            resp = requests.delete(url, headers={"Accept": "application/json"})
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"No se pudo conectar para cancelar la pre-reserva: {e}")

        # Intentar parsear la respuesta siempre
        try:
            data = resp.json() if resp.content else {}
        except ValueError:
            data = {"raw": resp.text}

        if resp.status_code >= 400:
            # Para debug, mostramos el cuerpo que devuelve el API
            raise ConnectionError(
                f"Error al cancelar la pre-reserva (HTTP {resp.status_code}): {data}"
            )

        # Normalizamos lo que devolvemos
        mensaje = data.get("mensaje") if isinstance(data, dict) else None
        return {
            "ok": True,
            "mensaje": mensaje or "Pre-reserva cancelada correctamente.",
            "raw": data,
        }

def main():
    rest = FuncionesEspecialesGestionRest()

    print("\n========== EJECUTANDO confirmar_reserva_interna (REST) ==========\n")

    try:
        respuesta = rest.confirmar_reserva_interna(
            idHabitacion="HACA000785",
            idHold="HOCA000064",   # 👈 tu HOLD REAL
            nombre="usuario",
            apellido="hotel",
            correo="hotelusuario@gmail.com",
            tipoDocumento="CEDULA",
            documento="1111111111",
            fechaInicio="2026-01-03T15:00:00",
            fechaFin="2026-01-04T11:00:00",
            numeroHuespedes=2
        )

        print("\n✅ RESPUESTA COMPLETA DEL SERVICIO REST:\n")
        print(respuesta)

        print("\n👉 Intentando extraer ID de reserva...\n")

        id_reserva = (
            respuesta.get("idReserva")
            or respuesta.get("IdReserva")
            or respuesta.get("reservaId")
        )

        print("ID RESERVA:", id_reserva)

    except Exception as e:
        print("\n❌ ERROR AL CONFIRMAR RESERVA (REST):\n")
        print(e)

