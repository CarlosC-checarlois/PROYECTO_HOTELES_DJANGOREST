
import requests


class UsuarioInternoGestionRest:

    def __init__(self):
        # URL base del servicio en Azure
        self.base_url = "https://gereca-dgd0hedaedb2dge4.canadacentral-01.azurewebsites.net/api/gestion/usuarios-internos"

    # ================================================================
    # GET: obtener todos los usuarios internos
    # ================================================================
    def listar(self):
        try:
            resp = requests.get(self.base_url)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise ConnectionError(f"Error al listar usuarios internos: {e}")

    # ================================================================
    # GET: obtener usuario por ID
    # ================================================================
    def obtener_por_id(self, id_usuario: int):
        try:
            url = f"{self.base_url}/{id_usuario}"
            resp = requests.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise ConnectionError(f"Error al obtener usuario interno {id_usuario}: {e}")

    # ================================================================
    # POST: crear usuario interno
    # ================================================================
    def crear(self, usuario_dto: dict):
        try:
            resp = requests.post(self.base_url, json=usuario_dto)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise ConnectionError(f"Error al crear usuario interno: {e}")

    # ================================================================
    # PUT: actualizar usuario interno
    # ================================================================
    def actualizar(self, usuario_dto: dict):
        try:
            resp = requests.put(self.base_url, json=usuario_dto)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise ConnectionError(f"Error al actualizar usuario interno: {e}")

    # ================================================================
    # DELETE: eliminar usuario interno
    # ================================================================
    def eliminar(self, id_usuario: int):
        try:
            url = f"{self.base_url}/{id_usuario}"
            resp = requests.delete(url)
            resp.raise_for_status()
            return True
        except Exception as e:
            raise ConnectionError(f"Error al eliminar usuario interno {id_usuario}: {e}")

    # ================================================================
    # POST: iniciar sesión
    # ================================================================
    def login(self, correo: str, clave: str):
        try:
            url = f"{self.base_url}/login"
            payload = {
                "Correo": correo,
                "Clave": clave
            }
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise ConnectionError(f"Error al iniciar sesión: {e}")
def test_crear_usuario():
    api = UsuarioInternoGestionRest()

    # Construir payload exactamente como lo pide tu API
    nuevo_usuario = {
        "Id": 0,                   # El API ignora este y genera su propio ID
        "IdRol": 1,                # Rol 1 = administrador / usuario normal según tu BD
        "Nombre": "Prueba",
        "Apellido": "Automatica",
        "Correo": "prueba_auto@hotel.com",
        "Clave": "12345678",       # 🔥 SIN HASH — EL API LO ENCRIPTA AUTOMATICAMENTE
        "Estado": True,
        "FechaNacimiento": None,
        "TipoDocumento": None,
        "Documento": None
    }

    print("➡ Enviando usuario nuevo al API...")
    try:
        respuesta = api.crear(nuevo_usuario)
        print("\n✅ Usuario creado correctamente:")
        print(respuesta)

    except Exception as e:
        print("\n❌ Error al crear usuario:")
        print(str(e))

def test_login():
    api = UsuarioInternoGestionRest()

    correo = "prueba_auto@hotel.com"
    clave = "12345678"  # 🔥 CLAVE EN TEXTO PLANO

    print("➡ Probando inicio de sesión...")
    print(f"   Correo: {correo}")
    print(f"   Clave:  {clave}")

    try:
        respuesta = api.login(correo, clave)
        print("\n✅ Inicio de sesión exitoso:")
        print(respuesta)

    except Exception as e:
        print("\n❌ Error al iniciar sesión:")
        print(str(e))

def actualizar_usuario_admin():
    api = UsuarioInternoGestionRest()

    # 1) Obtener todos los usuarios para encontrar el ID del usuario deseado
    usuarios = api.listar()

    usuario = next((u for u in usuarios if u["Correo"] == "carlosconstantevf@outlook.com"), None)

    if not usuario:
        print("❌ Usuario no encontrado.")
        return


    # 2) Construimos el DTO actualizado (respetando lo que ya tiene)
    usuario_actualizado = {
        "Id": usuario["Id"],
        "IdRol": 2,   # 🔥 NUEVO ROL = ADMINISTRADOR
        "Nombre": usuario["Nombre"],
        "Apellido": usuario["Apellido"],
        "Correo": usuario["Correo"],
        "Clave": "",  # IMPORTANTE: vacío → NO CAMBIAR CONTRASEÑA
        "Estado": usuario["Estado"],
        "FechaNacimiento": usuario["FechaNacimiento"],
        "TipoDocumento": usuario["TipoDocumento"],
        "Documento": usuario["Documento"]
    }

    print("\n➡ Enviando actualización...")
    try:
        resp = api.actualizar(usuario_actualizado)
        print("\n✅ Usuario actualizado correctamente:")
    except Exception as e:
        print("\n❌ Error al actualizar usuario:")
        print(str(e))


api = UsuarioInternoGestionRest()

# 1️⃣ Obtener usuario actual
usuario = api.obtener_por_id(1)

print("ANTES:")
print(usuario)

# 2️⃣ Cambiar nombre
usuario["Nombre"] = "CheCarlos"

# 3️⃣ Enviar actualización
actualizado = api.actualizar(usuario)

# 4️⃣ Mostrar resultado
print("\nDESPUÉS:")
print(actualizado)