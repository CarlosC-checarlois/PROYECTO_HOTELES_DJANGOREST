import requests

class TipoHabitacionGestionRest:

    def __init__(self):
        # URL BASE DEL SERVICIO EN AZURE
        self.base_url = "https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/tipos-habitacion"

    # ================================================================
    # GET: obtener todos los tipos de habitación
    # ================================================================
    def obtener_tipos(self):
        try:
            resp = requests.get(self.base_url)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise ConnectionError(f"Error al obtener lista de tipos de habitación: {e}")

    # ================================================================
    # GET: obtener tipo por ID
    # ================================================================
    def obtener_tipo_por_id(self, id_tipo: int):
        try:
            url = f"{self.base_url}/{id_tipo}"
            resp = requests.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise ConnectionError(f"Error al obtener tipo de habitación {id_tipo}: {e}")

    # ================================================================
    # POST: crear tipo de habitación
    # ================================================================
    def crear_tipo(self, tipo_dto: dict):
        try:
            resp = requests.post(self.base_url, json=tipo_dto)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise ConnectionError(f"Error al crear tipo de habitación: {e}")

    # ================================================================
    # PUT: actualizar tipo de habitación
    # ================================================================
    def actualizar_tipo(self, id_tipo: int, tipo_dto: dict):
        try:
            url = f"{self.base_url}/{id_tipo}"
            resp = requests.put(url, json=tipo_dto)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise ConnectionError(f"Error al actualizar tipo de habitación {id_tipo}: {e}")

    # ================================================================
    # DELETE: eliminar tipo de habitación
    # ================================================================
    def eliminar_tipo(self, id_tipo: int):
        try:
            url = f"{self.base_url}/{id_tipo}"
            resp = requests.delete(url)
            resp.raise_for_status()
            # DELETE retorna NoContent (204), no body
            return True
        except Exception as e:
            raise ConnectionError(f"Error al eliminar tipo de habitación {id_tipo}: {e}")
