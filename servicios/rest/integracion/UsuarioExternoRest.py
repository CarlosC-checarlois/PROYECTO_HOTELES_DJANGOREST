# usuario_externo_rest.py
import requests
from typing import Dict, Any


class UsuarioExternoRest:
    """
    Cliente REST para crear usuarios externos.
    Equivalente al UsuarioExternoController en C#.
    """

    BASE_URL = "https://reca.azurewebsites.net/api/v1/hoteles/usuarios/externo"

    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def crear_usuario_externo(
        self,
        booking_user_id: str,
        nombre: str,
        apellido: str,
        correo: str
    ) -> Dict[str, Any]:
        """
        Crea un nuevo usuario externo en el sistema.
        Parámetros:
            booking_user_id (str): ID de usuario externo (obligatorio)
            nombre (str): Nombre del usuario
            apellido (str): Apellido del usuario
            correo (str): Correo electrónico del usuario
        Retorna:
            Un diccionario con los datos del usuario creado
        """

        if not booking_user_id:
            raise ValueError("booking_user_id es obligatorio.")
        if not nombre:
            raise ValueError("nombre es obligatorio.")
        if not apellido:
            raise ValueError("apellido es obligatorio.")
        if not correo:
            raise ValueError("correo es obligatorio.")

        payload = {
            "bookingUserId": booking_user_id,
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo
        }

        try:
            response = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al conectar con el servicio UsuarioExterno: {e}")
