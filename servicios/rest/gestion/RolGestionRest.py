from pprint import pprint

import requests

class RolGestionRest:
    def __init__(self):
        # URL BASE DE TU API EN AZURE
        self.base_url = "https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/rol"

    # ----------------------------------------------------------------------
    # OBTENER TODOS LOS ROLES
    # ----------------------------------------------------------------------
    def obtener_roles(self):
        try:
            resp = requests.get(self.base_url)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise ConnectionError(f"Error al obtener roles: {e}")

    # ----------------------------------------------------------------------
    # OBTENER ROL POR ID
    # ----------------------------------------------------------------------
    def obtener_rol_por_id(self, id_rol: int):
        try:
            url = f"{self.base_url}/{id_rol}"
            resp = requests.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise ConnectionError(f"Error al obtener el rol {id_rol}: {e}")

    # ----------------------------------------------------------------------
    # CREAR ROL
    # ----------------------------------------------------------------------
    def crear_rol(self, rol_dto: dict):
        try:
            resp = requests.post(self.base_url, json=rol_dto)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise ConnectionError(f"Error al crear rol: {e}")

    # ----------------------------------------------------------------------
    # ACTUALIZAR ROL
    # ----------------------------------------------------------------------
    def actualizar_rol(self, id_rol: int, rol_dto: dict):
        try:
            url = f"{self.base_url}/{id_rol}"
            resp = requests.put(url, json=rol_dto)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise ConnectionError(f"Error al actualizar rol {id_rol}: {e}")

    # ----------------------------------------------------------------------
    # ELIMINAR ROL
    # ----------------------------------------------------------------------
    def eliminar_rol(self, id_rol: int):
        try:
            url = f"{self.base_url}/{id_rol}"
            resp = requests.delete(url)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise ConnectionError(f"Error al eliminar rol {id_rol}: {e}")

c = RolGestionRest()
pprint(c.obtener_roles())