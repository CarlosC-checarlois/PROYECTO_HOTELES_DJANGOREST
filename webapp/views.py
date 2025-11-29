import base64
from xml.sax.handler import property_interning_dict
import boto3
from django.conf import settings

from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime
from servicios.rest.gestion.HoldGestionRest import HoldGestionRest
from servicios.rest.integracion.HabitacionesRest import HabitacionesRest
from servicios.rest.gestion.TipoHabitacionGestionRest import TipoHabitacionGestionRest
from servicios.rest.gestion.AmexHabGestionRest import AmexHabGestionRest
from servicios.rest.gestion.AmenidadesGestionRest import AmenidadesGestionRest

from pprint import pprint
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from servicios.rest.gestion.UsuarioInternoGestionRest import UsuarioInternoGestionRest
from django.shortcuts import render, redirect
from servicios.rest.gestion.PagoGestionRest import PagoGestionRest
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, redirect
from servicios.rest.gestion.UsuarioInternoGestionRest import UsuarioInternoGestionRest
from servicios.rest.gestion.FuncionesEspecialesGestionRest import FuncionesEspecialesGestionRest
import threading
import time
from servicios.rest.gestion.FacturasGestionRest import FacturasGestionRest
from servicios.rest.gestion.PdfGestionRest import PdfGestionRest
from servicios.rest.gestion.HabxResGestionRest import HabxResGestionRest
from servicios.rest.gestion.HabitacionesGestionRest import HabitacionesGestionRest
from servicios.rest.gestion.ReservaGestionRest import ReservaGestionRest
from servicios.rest.gestion.ImagenHabitacionGestionRest import ImagenHabitacionGestionRest
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from utils.pdf_generator import generar_pdf_factura
from utils.s3_upload import subir_pdf_a_s3
from webapp.decorators import admin_required

import uuid


def index_inicio(request):
    return render(request, 'webapp/inicio/index.html')

class HabitacionesView(View):
    template_name = "webapp/habitaciones/index.html"

    def get(self, request):

        # Cargar tipos de habitación
        cliente_tipos = TipoHabitacionGestionRest()
        tipos = cliente_tipos.obtener_tipos()

        return render(request, self.template_name, {
            "usuario_id": request.session.get("usuario_id"),
            "token_sesion": request.session.session_key or "anon-" + str(uuid.uuid4()),
            "tipos_habitacion": tipos
        })


class HabitacionesAjaxView(View):
    def get(self, request):
        try:
            import time
            start_time = time.time()

            # ------------------------------------
            # Filtros
            # ------------------------------------
            tipo_habitacion = request.GET.get("tipo_habitacion") or None
            fecha_entrada = request.GET.get("fecha_entrada") or None
            fecha_salida = request.GET.get("fecha_salida") or None
            capacidad = request.GET.get("capacidad") or None
            precio_min = request.GET.get("precio_min") or None
            precio_max = request.GET.get("precio_max") or None

            # Paginación
            try:
                page = int(request.GET.get("page", 1))
            except:
                page = 1

            page = max(page, 1)
            per_page = 5

            date_from = datetime.strptime(fecha_entrada, "%Y-%m-%d") if fecha_entrada else None
            date_to = datetime.strptime(fecha_salida, "%Y-%m-%d") if fecha_salida else None

            # ------------------------------------
            # OPTIMIZACIÓN: Cargar datos EN PARALELO
            # ------------------------------------

            # Contenedor para almacenar resultados
            datos = {
                "habitaciones_all": None,
                "todas_habitaciones": None,
                "amex_list": None,
                "amenidades_data": None,
                "tipos_list": None,
            }

            # Funciones para ejecutar en threads
            def cargar_buscar():
                cliente = HabitacionesRest()
                datos["habitaciones_all"] = cliente.buscar_habitaciones(
                    date_from=date_from,
                    date_to=date_to,
                    tipo_habitacion=tipo_habitacion,
                    capacidad=int(capacidad) if capacidad else None,
                    precio_min=float(precio_min) if precio_min else None,
                    precio_max=float(precio_max) if precio_max else None,
                )

            def cargar_habitaciones():
                api_habs = HabitacionesGestionRest()
                datos["todas_habitaciones"] = api_habs.obtener_habitaciones()

            def cargar_amexhab():
                amex_rest = AmexHabGestionRest()
                datos["amex_list"] = amex_rest.obtener_amexhab()

            def cargar_amenidades():
                amen_rest = AmenidadesGestionRest()
                datos["amenidades_data"] = amen_rest.obtener_amenidades()

            def cargar_tipos():
                tipos_rest = TipoHabitacionGestionRest()
                datos["tipos_list"] = tipos_rest.obtener_tipos()

            # Crear threads para cargas paralelas
            threads = [
                threading.Thread(target=cargar_buscar),
                threading.Thread(target=cargar_habitaciones),
                threading.Thread(target=cargar_amexhab),
                threading.Thread(target=cargar_amenidades),
                threading.Thread(target=cargar_tipos),
            ]

            # Iniciar todos los threads
            for t in threads:
                t.start()

            # Esperar a que terminen TODOS
            for t in threads:
                t.join()

            elapsed_data = time.time() - start_time
            print(f"[PERF] Carga de datos en paralelo: {elapsed_data:.2f}s")

            # Desempacar datos
            habitaciones_all = datos["habitaciones_all"]
            todas_las_habitaciones = datos["todas_habitaciones"]
            amex_list = datos["amex_list"]
            amenidades_data = datos["amenidades_data"]
            tipos_list = datos["tipos_list"]

            total = len(habitaciones_all)

            # ------------------------------------
            # Paginación
            # ------------------------------------
            start = (page - 1) * per_page
            end = start + per_page
            habitaciones_slice = habitaciones_all[start:end]

            if not habitaciones_slice:
                return JsonResponse({"success": True, "data": [], "total": total})

            # ------------------------------------
            # Crear índices para búsqueda O(1)
            # ------------------------------------
            hab_index = {h["IdHabitacion"]: h for h in todas_las_habitaciones}

            amex_index = {}
            for a in amex_list:
                amex_index.setdefault(a["IdHabitacion"], []).append(a["IdAmenidad"])

            amen_index = {a["IdAmenidad"]: a["NombreAmenidad"] for a in amenidades_data}

            idx_tipos = {t["IdTipoHabitacion"]: t for t in tipos_list}

            resultado = []

            for h in habitaciones_slice:
                hid = h.get("idHabitacion")

                # Usar índice en lugar de llamar API
                detalle = hab_index.get(hid)

                if not detalle:
                    continue

                capacidad_real = detalle.get("CapacidadHabitacion")
                tipo_id = detalle.get("IdTipoHabitacion")
                tipo_data = idx_tipos.get(tipo_id)

                # Amenidades
                ids_amen = amex_index.get(hid, [])
                nombres_amenidades = [amen_index.get(aid, "Amenidad desconocida") for aid in ids_amen]

                # Imagen
                raw_img = h.get("imagenes") or ""
                imagen_principal = raw_img.split("|")[0].strip() if "|" in raw_img else raw_img.strip()
                if not imagen_principal:
                    imagen_principal = "https://imageness3realdecuenca.s3.us-east-2.amazonaws.com/Imagen4.png"

                item = {
                    "id": hid,
                    "nombre": detalle.get("NombreHabitacion"),
                    "hotel": detalle.get("NombreHotel") or h.get("nombreHotel"),
                    "ubicacion": detalle.get("NombreCiudad") or h.get("nombreCiudad"),
                    "precio": detalle.get("PrecioActualHabitacion") or h.get("precioVigente"),
                    "imagen": imagen_principal,
                    "amenidades": nombres_amenidades,
                    "capacidad": capacidad_real,
                    "tipo_nombre": tipo_data.get("NombreHabitacion") if tipo_data else None,
                    "descripcion_tipo": tipo_data.get("DescripcionTipoHabitacion") if tipo_data else None,
                }

                resultado.append(item)

            elapsed_total = time.time() - start_time
            print(f"[PERF] Tiempo total de solicitud: {elapsed_total:.2f}s")

            return JsonResponse({"success": True, "data": resultado, "total": total})

        except Exception as e:
            print("\n❌ ERROR EN SERVIDOR:")
            print(e)
            import traceback
            traceback.print_exc()
            return JsonResponse({"success": False, "error": str(e)}, status=500)


def detalle_habitacion(request, id):
    """
    Vista para mostrar los detalles de una habitación específica.
    OPTIMIZACIÓN: Carga de datos en paralelo
    """
    import time
    start_time = time.time()

    # ==============================
    # CARGAR DATOS EN PARALELO
    # ==============================
    datos = {
        "habitaciones": None,
        "amex_list": None,
        "amenidades_data": None,
    }

    def cargar_habitaciones():
        cliente = HabitacionesRest()
        datos["habitaciones"] = cliente.buscar_habitaciones()

    def cargar_amexhab():
        amex_rest = AmexHabGestionRest()
        datos["amex_list"] = amex_rest.obtener_amexhab()

    def cargar_amenidades():
        amen_rest = AmenidadesGestionRest()
        datos["amenidades_data"] = amen_rest.obtener_amenidades()

    # Crear threads
    threads = [
        threading.Thread(target=cargar_habitaciones),
        threading.Thread(target=cargar_amexhab),
        threading.Thread(target=cargar_amenidades),
    ]

    # Ejecutar en paralelo
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    elapsed_data = time.time() - start_time
    print(f"[PERF] Carga de datos en paralelo: {elapsed_data:.2f}s")

    # ==============================
    # PROCESAR DATOS
    # ==============================

    habitaciones = datos["habitaciones"]
    amex_list = datos["amex_list"]
    amenidades_data = datos["amenidades_data"]

    # Buscar la habitación con el ID proporcionado
    habitacion = next((h for h in habitaciones if h.get("idHabitacion") == id), None)

    if not habitacion:
        # Si no se encuentra la habitación
        return render(request, 'webapp/habitaciones/no_encontrada.html', {"id": id})

    # Filtrar solo registros de la habitación actual
    ids_amenidades = [
        a["IdAmenidad"]
        for a in amex_list
        if a.get("IdHabitacion") == id
    ]

    # Index de amenidad por ID
    amen_index = {a["IdAmenidad"]: a["NombreAmenidad"] for a in amenidades_data}

    # Lista final de nombres de amenidad
    amenidades = [
        amen_index.get(aid, "Amenidad desconocida")
        for aid in ids_amenidades
    ]

    # ==============================
    # Procesar imágenes
    # ==============================
    imagenes_raw = habitacion.get("imagenes", "") or ""
    imagen_lista = [img.strip() for img in imagenes_raw.split("|") if img.strip()]
    if not imagen_lista:
        imagen_lista = ["https://imageness3realdecuenca.s3.us-east-2.amazonaws.com/Imagen4.png"]

    imagen_principal = imagen_lista[0]

    # ==============================
    # Armar contexto
    # ==============================
    contexto = {
        "id": habitacion.get("idHabitacion"),
        "nombre": habitacion.get("nombreHabitacion") or "Habitación",
        "hotel": habitacion.get("nombreHotel") or "Hotel desconocido",
        "ubicacion": habitacion.get("nombreCiudad") or "Ubicación no disponible",
        "pais": habitacion.get("nombrePais") or "No disponible",
        "tipo": habitacion.get("tipoHabitacion") or "N/A",
        "capacidad": habitacion.get("capacidad") or 0,
        "precio": habitacion.get("precioVigente") or habitacion.get("precioActual") or 0,

        "imagenes": imagen_lista,
        "imagen_principal": imagen_principal,

        # ahora se llaman AMENIDADES
        "amenidades": amenidades,
    }

    elapsed_total = time.time() - start_time
    print(f"[PERF] Tiempo total de solicitud: {elapsed_total:.2f}s")

    return render(request, 'webapp/habitaciones/detalle.html', contexto)


@method_decorator(csrf_exempt, name="dispatch")
class FechasOcupadasAjaxView(View):
    """
    Endpoint AJAX para obtener las fechas ocupadas de una habitación.
    Retorna un JSON con las fechas bloqueadas para el calendario.
    """
    def get(self, request, id_habitacion):
        try:
            from datetime import datetime, timedelta
            
            # Obtener todas las reservas
            api_reserva = ReservaGestionRest()
            api_habxres = HabxResGestionRest()
            
            reservas_api = api_reserva.obtener_reservas()
            habxres_list = api_habxres.obtener_habxres()
            
            # Crear índice de HabxRes por IdReserva
            idx_habxres = {h["IdReserva"]: h for h in habxres_list}
            
            # Filtrar reservas de esta habitación que estén confirmadas o en pre-reserva
            fechas_ocupadas = []
            
            for r in reservas_api:
                id_reserva = r.get("IdReserva")
                habxres = idx_habxres.get(id_reserva)
                
                if not habxres:
                    continue
                    
                # Verificar que sea la habitación correcta
                if habxres.get("IdHabitacion") != id_habitacion:
                    continue
                
                # Solo considerar reservas confirmadas o pre-reservas activas
                estado = (r.get("EstadoGeneralReserva") or "").strip().upper()
                # Considerar todos los estados excepto canceladas
                if estado == "CANCELADA":
                    continue
                
                fecha_inicio = r.get("FechaInicioReserva")
                fecha_fin = r.get("FechaFinalReserva")
                
                if fecha_inicio and fecha_fin:
                    # Agregar todas las fechas del rango (incluyendo inicio y fin)
                    try:
                        inicio = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
                        fin = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
                        
                        # Generar todas las fechas del rango
                        fecha_actual = inicio.date()
                        fecha_final = fin.date()
                        
                        while fecha_actual <= fecha_final:
                            fechas_ocupadas.append(fecha_actual.isoformat())
                            fecha_actual += timedelta(days=1)
                    except Exception as e:
                        print(f"Error al procesar fechas de reserva {id_reserva}: {e}")
                        continue
            
            # Eliminar duplicados y ordenar
            fechas_ocupadas = sorted(list(set(fechas_ocupadas)))
            
            return JsonResponse({
                "success": True,
                "fechas_ocupadas": fechas_ocupadas,
                "total_fechas": len(fechas_ocupadas)
            })
            
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)
# =============================
#       CREAR PRERESERVA
# =============================
def iniciar_temporizador_hold(id_hold, duracion, api):
    print(f"[TEMPORIZADOR] HOLD {id_hold} iniciado ({duracion} segundos)")

    segundos = duracion

    while segundos > 0:
        print(f"[TEMPORIZADOR] HOLD {id_hold} → quedan {segundos} segundos")
        time.sleep(1)
        segundos -= 1

    # Tiempo terminado → cancelar HOLD
    try:
        print(f"[TEMPORIZADOR] HOLD {id_hold} EXPIRÓ. Cancelando…")
        api.cancelar_hold(id_hold)
        print(f"[TEMPORIZADOR] HOLD {id_hold} CANCELADO correctamente.")
    except Exception as e:
        print(f"[TEMPORIZADOR] Error al cancelar HOLD {id_hold}: {e}")

def crear_prereserva(request):

    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    # === Datos enviados desde el formulario ===
    id_habitacion = request.POST.get("idHabitacion")
    fecha_inicio = request.POST.get("fechaInicio")
    fecha_fin = request.POST.get("fechaFin")
    numero_huespedes = int(request.POST.get("numeroHuespedes", "1"))

    nombre = request.POST.get("nombre")
    apellido = request.POST.get("apellido")
    correo = request.POST.get("correo")
    tipo_documento = request.POST.get("tipoDocumento")
    documento = request.POST.get("documento")

    precio_actual = float(request.POST.get("precioActual") or 0)
    usuario_id = request.POST.get("usuarioId")

    if not usuario_id:
        return JsonResponse({"error": "Usuario no identificado"}, status=400)

    # === Llamar al servicio REST ===
    api = FuncionesEspecialesGestionRest()

    try:
        # 1) Crear Pre-reserva
        resultado = api.crear_prereserva(
            id_habitacion=id_habitacion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            numero_huespedes=numero_huespedes,
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            tipo_documento=tipo_documento,
            documento=documento,
            duracion_hold_seg=180,
            precio_actual=precio_actual
        )

        # Obtener el ID del HOLD de la respuesta (puede venir con diferentes nombres)
        hold_id = resultado.get("IdHold") or resultado.get("idHold") or resultado.get("holdId")
        
        # Validar que tenemos un hold_id válido
        if not hold_id or hold_id == "":
            # Si no hay hold_id en la respuesta, intentar usar los datos directamente de la respuesta
            reserva_id = resultado.get("IdReserva") or resultado.get("idReserva")
            tiempo_hold = resultado.get("TiempoHold") or resultado.get("tiempoHold") or 180
            fecha_inicio_hold = resultado.get("FechaInicioHold") or resultado.get("fechaInicioHold") or fecha_inicio
            
            # Si tampoco tenemos reserva_id, entonces hay un problema con la respuesta
            if not reserva_id:
                return JsonResponse({
                    "error": "La respuesta del servidor no contiene la información necesaria. Respuesta recibida: " + str(resultado)
                }, status=500)
        else:
            # 2) Obtener información extendida del HOLD usando el ID
            hold_api = HoldGestionRest()
            try:
                hold = hold_api.obtener_hold_por_id(str(hold_id))
                
                if not hold:
                    # Si no se encuentra el HOLD, usar los datos de la respuesta original
                    reserva_id = resultado.get("IdReserva") or resultado.get("idReserva")
                    tiempo_hold = resultado.get("TiempoHold") or resultado.get("tiempoHold") or 180
                    fecha_inicio_hold = resultado.get("FechaInicioHold") or resultado.get("fechaInicioHold") or fecha_inicio
                else:
                    reserva_id = hold.get("IdReserva") or hold.get("idReserva")
                    tiempo_hold = hold.get("TiempoHold") or hold.get("tiempoHold") or 180
                    fecha_inicio_hold = hold.get("FechaInicioHold") or hold.get("fechaInicioHold") or fecha_inicio
            except ValueError as ve:
                # Si el error es que el ID_HOLD es obligatorio, usar los datos de la respuesta original
                reserva_id = resultado.get("IdReserva") or resultado.get("idReserva")
                tiempo_hold = resultado.get("TiempoHold") or resultado.get("tiempoHold") or 180
                fecha_inicio_hold = resultado.get("FechaInicioHold") or resultado.get("fechaInicioHold") or fecha_inicio
                
                if not reserva_id:
                    return JsonResponse({"error": f"Error al obtener el HOLD: {str(ve)}"}, status=400)
            except Exception as e:
                # Si hay otro error al obtener el HOLD, usar los datos de la respuesta original
                reserva_id = resultado.get("IdReserva") or resultado.get("idReserva")
                tiempo_hold = resultado.get("TiempoHold") or resultado.get("tiempoHold") or 180
                fecha_inicio_hold = resultado.get("FechaInicioHold") or resultado.get("fechaInicioHold") or fecha_inicio
                
                if not reserva_id:
                    return JsonResponse({"error": f"Error al obtener información del HOLD: {str(e)}"}, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    # === Redirigir con datos correctos ===
    return redirect(
        f"/usuario/reservas/?uid={usuario_id}"
        f"&reserva={reserva_id}"
        f"&ini={fecha_inicio_hold}"
        f"&t={tiempo_hold}"
    )



# =============================
#       RESERVAS
# =============================
def index_reservas(request):
    # Aquí se puede consumir:
    # https://reca.azurewebsites.net/api/v1/hoteles/hold
    return render(request, 'webapp/reservas/index.html')

# =============================
#       LOGIN Y REGISTER
# =============================
def index_login(request):
    return render(request, "webapp/login/index.html")


def login_post(request):
    if request.method != "POST":
        return redirect("login")

    correo = request.POST.get("correo")
    clave = request.POST.get("clave")

    api = UsuarioInternoGestionRest()

    try:
        respuesta = api.login(correo, clave)

        # Validar respuesta del API
        if not respuesta or "Id" not in respuesta:
            messages.error(request, "Credenciales incorrectas.")
            return redirect("login")

        usuario = {
            "id": respuesta["Id"],
            "correo": respuesta["Correo"],
            "nombre": respuesta.get("Nombre", ""),
            "apellido": respuesta.get("Apellido", ""),
            "rol": respuesta.get("IdRol"),
            "tipo_doc": respuesta.get("TipoDocumento", ""),
            "documento": respuesta.get("Documento", ""),
            "fecha_nac": respuesta.get("FechaNacimiento", ""),
        }

        # → Renderizar con los datos del usuario y establecer cookie
        response = render(request, "webapp/login/index.html", {
            "login_exitoso": True,
            "usuario": usuario,
        })

        # Guardar el rol en una cookie para validación en el servidor
        # Usar httponly=False para que JavaScript pueda leerlas si es necesario
        # Usar samesite='Lax' para compatibilidad
        response.set_cookie('usuario_rol', str(usuario['rol']), max_age=86400, httponly=False, samesite='Lax')  # 24 horas
        response.set_cookie('usuario_id', str(usuario['id']), max_age=86400, httponly=False, samesite='Lax')

        return response

    except Exception as e:
        messages.error(request, f"Error con el servidor: {e}")
        return redirect("login")


def index_register(request):
    return render(request, 'webapp/register/index.html')
def register_post(request):
    if request.method != "POST":
        return redirect("register")

    nombre = request.POST.get("nombre")
    apellido = request.POST.get("apellido")
    correo = request.POST.get("correo")
    clave = request.POST.get("clave")
    tipo_documento = request.POST.get("tipo_documento")
    documento = request.POST.get("documento")

    # Construir DTO que el API espera
    payload = {
        "Id": 0,
        "IdRol": 1,  # Usuario normal
        "Nombre": nombre,
        "Apellido": apellido,
        "Correo": correo,
        "Clave": clave,  # API la encripta
        "Estado": True,
        "TipoDocumento": tipo_documento,
        "Documento": documento,
        "FechaNacimiento": None,
    }

    api = UsuarioInternoGestionRest()

    try:
        nuevo = api.crear(payload)

        if not nuevo:
            messages.error(request, "No se pudo crear la cuenta.")
            return redirect("register")

        messages.success(request, "Cuenta creada correctamente. Ahora puedes iniciar sesión.")
        return redirect("login")

    except Exception as e:
        messages.error(request, f"Error: {e}")
        return redirect("register")


# views_webapp.py



class MisReservasView(View):

    template_name = "webapp/reservas/index.html"

    def get(self, request):
        import time
        start_time = time.time()

        api_reserva = ReservaGestionRest()
        api_habxres = HabxResGestionRest()
        api_habs = HabitacionesGestionRest()
        api_imgs = ImagenHabitacionGestionRest()
        api_hold = HoldGestionRest()

        usuario_id = request.GET.get("uid")
        usuario_correo = None  # Django NO tiene acceso a localStorage
        if not usuario_id:
            return render(request, self.template_name, {
                "reservas": [],
                "error": "No se pudo determinar el usuario logeado."
            })

        # -----------------------------------
        # OPTIMIZACIÓN: Cargar datos en paralelo
        # -----------------------------------
        datos = {
            "reservas_api": None,
            "habxres_list": None,
            "hold_list": None,
            "imgs_list": None,
        }

        def cargar_reservas():
            datos["reservas_api"] = api_reserva.obtener_reservas()

        def cargar_habxres():
            datos["habxres_list"] = api_habxres.obtener_habxres()

        def cargar_hold():
            datos["hold_list"] = api_hold.obtener_hold()

        def cargar_imagenes():
            datos["imgs_list"] = api_imgs.obtener_imagenes()

        # Ejecutar en paralelo
        threads = [
            threading.Thread(target=cargar_reservas),
            threading.Thread(target=cargar_habxres),
            threading.Thread(target=cargar_hold),
            threading.Thread(target=cargar_imagenes),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        reservas_api = datos["reservas_api"]
        habxres_list = datos["habxres_list"]
        hold_list = datos["hold_list"]
        imgs_list = datos["imgs_list"]

        # Filtrar reservas del usuario
        reservas_filtradas = [
            r for r in reservas_api
            if str(r.get("IdUnicoUsuario")) == usuario_id
        ]

        # Crear índices
        idx_habxres = {h["IdReserva"]: h for h in habxres_list}
        idx_hold = {h["IdReserva"]: h for h in hold_list}
        
        # Crear índice de imágenes por habitación (optimización)
        idx_imagenes = {}
        for img in imgs_list:
            if img.get("EstadoImagen"):
                hab_id = img.get("IdHabitacion")
                if hab_id not in idx_imagenes:
                    idx_imagenes[hab_id] = img.get("UrlImagen")

        # Crear índice de habitaciones (cargar solo las necesarias)
        habitaciones_ids = set()
        for r in reservas_filtradas:
            id_res = r.get("IdReserva")
            hxr = idx_habxres.get(id_res, {})
            id_habitacion = hxr.get("IdHabitacion")
            if id_habitacion:
                habitaciones_ids.add(id_habitacion)

        # Cargar habitaciones en paralelo
        idx_habitaciones = {}
        def cargar_habitacion(hab_id):
            try:
                hab_data = api_habs.obtener_por_id(hab_id)
                idx_habitaciones[hab_id] = hab_data
            except:
                idx_habitaciones[hab_id] = {}

        threads_hab = [threading.Thread(target=cargar_habitacion, args=(hab_id,)) for hab_id in habitaciones_ids]
        for t in threads_hab:
            t.start()
        for t in threads_hab:
            t.join()

        reservas_final = []

        # -----------------------------------
        # CONSTRUIR RESERVAS
        # -----------------------------------
        for r in reservas_filtradas:
            id_res = r.get("IdReserva")

            # HABXRES
            hxr = idx_habxres.get(id_res, {})
            id_habitacion = hxr.get("IdHabitacion")

            # HOLD
            hold = idx_hold.get(id_res, {})
            id_hold = hold.get("IdHold")

            # HABITACIÓN (desde índice)
            hab_data = idx_habitaciones.get(id_habitacion, {})
            capacidad_habitacion = hab_data.get("CapacidadHabitacion")

            # IMAGEN (desde índice)
            imagen_final = idx_imagenes.get(id_habitacion) or "https://imageness3realdecuenca.s3.us-east-2.amazonaws.com/Imagen4.png"

            estado_reserva = (r.get("EstadoGeneralReserva") or "Pendiente").strip().upper()

            reservas_final.append({
                "idReserva": id_res,
                "idUsuario": r.get("IdUnicoUsuario"),

                "idHabitacion": id_habitacion,
                "idHold": id_hold,

                "habitacion": hab_data.get("NombreHabitacion") or "",
                "hotel": hab_data.get("NombreHotel") or "",
                "ciudad": hab_data.get("NombreCiudad") or "",
                "pais": hab_data.get("NombrePais") or "",

                "fecha_inicio": (r.get("FechaInicioReserva") or "")[:10],
                "fecha_fin": (r.get("FechaFinalReserva") or "")[:10],
                "huespedes": r.get("NumeroHuespedes") or 1,
                "estado": estado_reserva,

                "subtotal": hxr.get("CostoCalculadoHabxRes") or 0,
                "total_descuentos": hxr.get("DescuentoHabxRes") or 0,
                "total_impuestos": hxr.get("ImpuestosHabxRes") or 0,
                "total": r.get("CostoTotalReserva") or 0,

                "capacidad_escogida": hxr.get("CapacidadReservaHabxRes"),
                "capacidad_habitacion": capacidad_habitacion,
                "imagen": imagen_final,
                "usuario_correo": usuario_correo,
            })

        elapsed = time.time() - start_time
        print(f"[PERF] MisReservasView: {elapsed:.2f}s")

        return render(request, self.template_name, {"reservas": reservas_final})




@method_decorator(csrf_exempt, name="dispatch")
class ConfirmarReservaInternaAjax(View):

    def post(self, request):
        try:
            import json
            data = json.loads(request.body)

            id_habitacion = data.get("idHabitacion")
            id_hold = data.get("idHold")
            id_usuario_str = data.get("idUnicoUsuario")
            fecha_inicio = data.get("fechaInicio")
            fecha_fin = data.get("fechaFin")
            huespedes_str = data.get("numeroHuespedes")

            # Validaciones
            if not id_habitacion:
                return JsonResponse({"ok": False, "error": "idHabitacion es obligatorio"}, status=400)
            if not id_hold:
                return JsonResponse({"ok": False, "error": "idHold es obligatorio"}, status=400)
            if not id_usuario_str:
                return JsonResponse({"ok": False, "error": "idUnicoUsuario es obligatorio"}, status=400)
            if not fecha_inicio:
                return JsonResponse({"ok": False, "error": "fechaInicio es obligatoria"}, status=400)
            if not fecha_fin:
                return JsonResponse({"ok": False, "error": "fechaFin es obligatoria"}, status=400)
            if not huespedes_str:
                return JsonResponse({"ok": False, "error": "numeroHuespedes es obligatorio"}, status=400)

            try:
                id_usuario = int(id_usuario_str)
            except (ValueError, TypeError):
                return JsonResponse({"ok": False, "error": "idUnicoUsuario debe ser un número válido"}, status=400)

            try:
                huespedes = int(huespedes_str)
            except (ValueError, TypeError):
                return JsonResponse({"ok": False, "error": "numeroHuespedes debe ser un número válido"}, status=400)

            if huespedes <= 0:
                return JsonResponse({"ok": False, "error": "numeroHuespedes debe ser mayor que 0"}, status=400)

            api = FuncionesEspecialesGestionRest()

            # 1) Confirmar reserva interna
            # Las fechas ya vienen como strings ISO desde el frontend
            resultado = api.confirmar_reserva_interna(
                id_habitacion=id_habitacion,
                id_hold=id_hold,
                id_unico_usuario=id_usuario,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                numero_huespedes=huespedes
            )


            def obtener_url(filename):
                s3 = boto3.client(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
                return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{filename}"

            id_reserva = resultado.get("IdReserva")
            correo = resultado.get("Correo")

            if not id_reserva or not correo:
                return JsonResponse({"ok": False, "error": "No se pudo obtener idReserva o correo."})

            # 2) Emitir factura interna
            factura = api.emitir_factura_interna(id_reserva=id_reserva, correo=correo)
            id_factura = factura.get("IdFactura")

            # 3) Crear PDF real
            pdf_bytes = generar_pdf_factura(id_factura, {
                "id_reserva": id_reserva,
                "cliente": f"{resultado.get('Nombre')} {resultado.get('Apellido')}",
                "total": resultado.get("CostoTotalReserva")
            })

            # 4) Nombre del archivo tomado de la API
            pdf_filename = f"facturas/carlos/pdf{id_factura}.pdf"

            # 5) Subir a S3
            url_pdf_final = subir_pdf_a_s3(pdf_bytes, pdf_filename)

            return JsonResponse({
                "ok": True,
                "reserva": resultado,
                "factura": id_factura,
                "url_pdf": url_pdf_final
            })

        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)}, status=400)



# views_webapp.py

from django.http import JsonResponse
from django.views import View

from servicios.rest.gestion.FuncionesEspecialesGestionRest import FuncionesEspecialesGestionRest


class CancelarReservaAjax(View):
    """
    Cancela una pre-reserva desde el botón en Mis Reservas.
    """

    def post(self, request):
        try:
            import json
            data = json.loads(request.body)

            id_reserva = data.get("idReserva")
            if not id_reserva:
                return JsonResponse({"ok": False, "error": "idReserva es obligatorio"}, status=400)

            # 1) Buscar el HOLD asociado a esa reserva
            api_hold = HoldGestionRest()
            holds = api_hold.obtener_hold()

            id_hold = None
            for h in holds:
                if str(h.get("IdReserva")) == str(id_reserva):
                    id_hold = h.get("IdHold")
                    break

            if not id_hold:
                return JsonResponse({"ok": False, "error": "No se encontró HOLD asociado"}, status=404)

            # 2) Llamar al microservicio REST
            api = FuncionesEspecialesGestionRest()
            resultado = api.cancelar_prereserva(id_hold)

            return JsonResponse({
                "ok": True,
                "resultado": resultado
            })

        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)}, status=400)


class MisPagosView(View):
    def get(self, request, *args, **kwargs):
        # logica
        #correo, pero realmente no hace nada, solo ejecutamos la api
        # http://mibanca.runasp.net/api/Transacciones/{cuenta_origen}/{cuenta_destino}/{monto}
        # y se ejecuta los dos rest o soap de
        None
def usuario_gestion(request):
    """
    Vista: Gestión del perfil del usuario.
    - Solo renderiza la página.
    - La actualización se realiza vía fetch() desde el HTML (REST PUT).
    """

    # NOTA:
    # No usamos request.session porque ahora manejas todo con localStorage
    # El HTML tomará los valores desde localStorage.

    return render(request, "webapp/usuario/cliente/gestion/index.html")

from django.shortcuts import render

@admin_required
def usuario_gestion_administrador(request):
    """
    Vista principal del panel administrativo.
    Solo accesible para usuarios con rol = 2 (administrador).
    """
    return render(request, "webapp/usuario/administrador/gestion/index.html")

def mis_pagos(request):
    import time
    start_time = time.time()

    usuario_id = request.GET.get("uid")

    if not usuario_id:
        return render(request, "webapp/pagos/index.html", {
            "pagos": [],
            "error": "Debe iniciar sesión para ver sus pagos."
        })

    usuario_id = int(usuario_id)

    api_pagos = PagoGestionRest()
    api_facturas = FacturasGestionRest()
    api_pdf = PdfGestionRest()

    # OPTIMIZACIÓN: Cargar datos en paralelo
    datos = {
        "lista_pagos": None,
        "lista_facturas": None,
        "lista_pdfs": None,
    }

    def cargar_pagos():
        datos["lista_pagos"] = api_pagos.obtener_pagos()

    def cargar_facturas():
        datos["lista_facturas"] = api_facturas.obtener_facturas()

    def cargar_pdfs():
        datos["lista_pdfs"] = api_pdf.obtener_pdfs()

    threads = [
        threading.Thread(target=cargar_pagos),
        threading.Thread(target=cargar_facturas),
        threading.Thread(target=cargar_pdfs),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    try:
        lista_pagos = datos["lista_pagos"]
        lista_facturas = datos["lista_facturas"]
        lista_pdfs = datos["lista_pdfs"]
    except Exception as e:
        return render(request, "webapp/pagos/index.html", {
            "pagos": [],
            "error": f"Error al conectar con el servidor: {e}"
        })

    # Convertir facturas por ID
    facturas_dict = {f["IdFactura"]: f for f in lista_facturas}

    # Convertir pdfs por factura
    pdf_por_factura = {}
    for p in lista_pdfs:
        fid = p.get("IdFactura")
        if fid:
            pdf_por_factura[fid] = p

    # Filtrar pagos del usuario
    pagos_usuario = [
        p for p in lista_pagos if p.get("IdUnicoUsuario") == usuario_id
    ]

    pagos_final = []

    for p in pagos_usuario:
        fid = p.get("IdFactura")

        factura = facturas_dict.get(fid)
        pdf = pdf_por_factura.get(fid)

        estado_pdf = None
        url_pdf = None

        if pdf:
            estado_pdf = pdf.get("EstadoPdf")
            url_pdf = pdf.get("UrlPdf")

        # reparar fecha
        raw_fecha = p.get("FechaEmisionPago")
        fecha = ""
        if raw_fecha and isinstance(raw_fecha, str):
            if "-" in raw_fecha:
                fecha = raw_fecha[:10]
            else:
                fecha = "Fecha no disponible"

        pagos_final.append({
            "id": p.get("IdPago"),
            "factura_id": fid,
            "monto": p.get("MontoTotalPago"),
            "fecha": fecha,
            "estado": "Pagado" if p.get("EstadoPago") else "Pendiente",
            "cuenta_origen": p.get("CuentaOrigenPago"),
            "cuenta_destino": p.get("CuentaDestinoPago"),
            "metodo": p.get("IdMetodoPago"),

            # Datos factura
            "factura": factura,
            "pdf_estado": estado_pdf,
            "pdf_url": url_pdf,
        })

    elapsed = time.time() - start_time
    print(f"[PERF] mis_pagos: {elapsed:.2f}s")

    return render(request, "webapp/pagos/index.html", {"pagos": pagos_final})
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from servicios.rest.gestion.FacturasGestionRest import FacturasGestionRest
from servicios.rest.gestion.PdfGestionRest import PdfGestionRest



from fpdf import FPDF


from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime


def generar_pdf_factura(id_factura: int, datos: dict) -> bytes:
    """
    Genera un PDF desde HTML usando xhtml2pdf (sin reportlab directo).
    Retorna bytes seguros para subir a S3.
    """

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 30px;
            }}
            h1 {{
                color: #333;
            }}
            .line {{
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <h1>Factura #{id_factura}</h1>
        <p class="line">Reserva: {datos.get('id_reserva')}</p>
        <p class="line">Cliente: {datos.get('cliente')}</p>
        <p class="line">Total: ${datos.get('total')}</p>

        <br>
        <p>Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Gracias por su reserva en HOTEL GENÉRICO.</p>
    </body>
    </html>
    """

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        raise Exception("Error al generar PDF vía HTML")

    return result.getvalue()
