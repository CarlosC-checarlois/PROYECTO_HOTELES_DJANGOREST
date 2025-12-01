import base64
from xml.sax.handler import property_interning_dict
import boto3
from django.conf import settings
import re
from django.shortcuts import render, redirect
from django.contrib import messages
import threading
from datetime import datetime, timedelta
from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta
from urllib.parse import urlencode
# webapp/views.py
import decimal
import requests

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.utils import timezone

from django.views import View

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, redirect

import threading
import time


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from utils.pdf_generator import generar_pdf_factura
from utils.s3_upload import subir_pdf_a_s3
from webapp.decorators import admin_required
import uuid

# ====== SERVICIOS SOAP (USADOS COMO "REST") ======
from servicios.soap.gestion.HoldGestionSoap import HoldGestionSoap as HoldGestionRest
from servicios.soap.integracion.HabitacionesSoap import HabitacionesSoap as HabitacionesRest

from servicios.soap.gestion.TipoHabitacionGestionSoap import TipoHabitacionGestionSoap as TipoHabitacionGestionRest
from servicios.soap.gestion.AmexHabGestionSoap import AmexHabGestionSoap as AmexHabGestionRest
from servicios.soap.gestion.AmenidadGestionSoap import AmenidadGestionSoap as AmenidadesGestionRest

from servicios.soap.gestion.UsuarioInternoGestionSoap import UsuarioInternoGestionSoap as UsuarioInternoGestionRest
from servicios.soap.gestion.PagoGestionSoap import PagoGestionSoap as PagoGestionRest
from servicios.rest.gestion.FuncionesEspecialesGestionRest import FuncionesEspecialesGestionRest

from servicios.soap.gestion.FacturaGestionSoap import FacturaGestionSoap as FacturasGestionRest
from servicios.soap.gestion.PdfGestionSoap import PdfGestionSoap as PdfGestionRest
from servicios.soap.gestion.HabxResGestionSoap import HabxResGestionSoap as HabxResGestionRest

from servicios.soap.gestion.HabitacionGestionSoap import HabitacionesGestionSoap as HabitacionesGestionRest
from servicios.soap.gestion.ReservaGestionSoap import ReservaGestionSoap as ReservaGestionRest
from servicios.soap.gestion.ImagenHabitacionGestionSoap import ImagenHabitacionGestionSoap as ImagenHabitacionGestionRest

def usuario_ya_logueado(request):
    """
    Consideramos "logueado" si hay cookie o sesión con usuario_id.
    """
    if request.COOKIES.get("usuario_id"):
        return True
    if request.session.get("usuario_id"):
        return True
    return False


def buscar_usuario_por_correo(correo: str):
    """
    Busca un usuario interno usando la API REST /usuarios-internos (listar)
    y filtra SOLO por correo.
    """

    if not correo:
        return None

    api_usuarios = UsuarioInternoGestionRest()

    try:
        usuarios = api_usuarios.listar()
    except Exception as e:
        print("[USUARIOS] Error llamando a listar():", e)
        return None

    correo_norm = correo.strip().lower()

    for u in usuarios:
        u_correo = (u.get("Correo") or "").strip().lower()
        if u_correo == correo_norm:
            return u  # 👈 devuelve todo el dict del usuario

    return None


###############################################################
###############################################################
###############################################################
## funciones de renderizacion
def index_inicio(request):
    return render(request, 'webapp/inicio/index.html')


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

        # Si API no devuelve un usuario válido
        if not respuesta or not respuesta.get("Id"):
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

        response = render(request, "webapp/login/index.html", {
            "login_exitoso": True,
            "usuario": usuario,
        })

        response.set_cookie(
            'usuario_rol',
            str(usuario['rol']),
            max_age=86400,
            httponly=False,
            samesite='Lax'
        )
        response.set_cookie(
            'usuario_id',
            str(usuario['id']),
            max_age=86400,
            httponly=False,
            samesite='Lax'
        )

        return response

    except Exception:
        # ✅ MENSAJE ÚNICO PARA CUALQUIER ERROR
        messages.error(request, "Credenciales incorrectas.")
        return redirect("login")

def index_register(request):
    # Si ya está logueado, directo al inicio

    return render(request, "webapp/register/index.html")


def register_post(request):
    if request.method != "POST":
        return redirect("register")

    nombre = (request.POST.get("nombre") or "").strip()
    apellido = (request.POST.get("apellido") or "").strip()
    correo = (request.POST.get("correo") or "").strip()
    clave = (request.POST.get("clave") or "").strip()
    tipo_documento = request.POST.get("tipo_documento") or ""
    documento = (request.POST.get("documento") or "").strip()

    errores = []

    # -----------------------
    # VALIDACIONES BÁSICAS
    # -----------------------
    if not nombre:
        errores.append("El nombre es obligatorio.")
    if not apellido:
        errores.append("El apellido es obligatorio.")
    if not correo:
        errores.append("El correo electrónico es obligatorio.")
    if not clave:
        errores.append("La contraseña es obligatoria.")
    if not documento:
        errores.append("El número de documento es obligatorio.")
    if clave and len(clave) > 40:
        errores.append("La contraseña no puede tener más de 40 caracteres.")

    # si hay errores, los mostramos y no llamamos al API
    if errores:
        for err in errores:
            messages.error(request, err)
        return redirect("register")

    # Documento: solo números y máx. 10 caracteres
    if documento and (not documento.isdigit() or len(documento) > 10):
        errores.append("El número de documento debe contener solo números y máximo 10 dígitos.")

    # -----------------------
    # VALIDACIÓN DE CORREO
    # -----------------------
    email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.com$'
    if correo and not re.match(email_regex, correo):
        errores.append("El correo electrónico debe tener el formato usuario@dominio.com.")

    allowed_domains = {
        "gmail.com",
        "yahoo.com",
        "outlook.com",
        "hotmail.com",
        "live.com",
        "icloud.com",
    }

    if correo and re.match(email_regex, correo):
        try:
            dominio = correo.split("@", 1)[1].lower()
        except IndexError:
            dominio = ""

        if dominio not in allowed_domains:
            errores.append(
                "Solo se permiten correos de dominios generales como "
                "@gmail.com, @yahoo.com, @outlook.com, @hotmail.com, @live.com o @icloud.com."
            )

    # Si hubo errores hasta aquí, no seguimos
    if errores:
        for err in errores:
            messages.error(request, err)
        return redirect("register")

    api = UsuarioInternoGestionRest()

    # =======================
    #  VALIDAR CORREO ÚNICO
    # =======================
    try:
        # 🔥 aquí usamos listar(), que sí existe en tu clase
        usuarios_existentes = api.listar()

        if any(
                (u.get("Correo") or "").lower() == correo.lower()
                for u in usuarios_existentes
        ):
            messages.error(request, "Ya existe una cuenta registrada con ese correo.")
            return redirect("register")

    except Exception as e:
        messages.error(request, f"No se pudo verificar el correo: {e}")
        return redirect("register")

    # -----------------------
    # Construir DTO para el API
    # -----------------------
    payload = {
        "Id": 0,
        "IdRol": 1,  # Usuario normal
        "Nombre": nombre,
        "Apellido": apellido,
        "Correo": correo,
        "Clave": clave,
        "Estado": True,
        "TipoDocumento": tipo_documento,
        "Documento": documento,
        "FechaNacimiento": None,
    }

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


def index_reservas(request):
    return render(request, "webapp/reservas/index.html")


def api_mis_reservas(request):
    correo = request.GET.get("correo")

    if not correo:
        return JsonResponse({"error": "No hay sesión activa"}, status=401)

    usuario = buscar_usuario_por_correo(correo)
    if not usuario:
        return JsonResponse({"error": "Usuario no existe"}, status=404)

    usuario_id = usuario["Id"]

    api = ReservaGestionRest()
    todas = api.obtener_reservas()

    mias = [r for r in todas if str(r.get("IdUnicoUsuario")) == str(usuario_id)]

    return JsonResponse({"reservas": mias})


class MisReservasView(View):
    template_name = "webapp/reservas/index.html"

    def get(self, request):
        start_time = time.time()

        api_reserva = ReservaGestionRest()
        api_habxres = HabxResGestionRest()
        api_habs = HabitacionesGestionRest()
        api_imgs = ImagenHabitacionGestionRest()
        api_hold = HoldGestionRest()
        correo = request.GET.get("correo")
        usuario = buscar_usuario_por_correo(correo)
        if not usuario:
            return render(request, self.template_name, {"reservas": [], "warning": "Cargando..."})
        usuario_id = usuario["Id"]
        usuario_correo = usuario.get("Correo")
        id_reserva_qs = request.GET.get("id_reserva_reserva")
        fecha_inicio_hold_qs = request.GET.get("fecha_inicio_hold_reserva")
        tiempo_hold_qs = request.GET.get("tiempo_hold_reserva")
        id_hold_qs = request.GET.get("id_hold_reserva")

        # 2.a) Si viene id_reserva_reserva → asociamos manualmente la reserva al usuario
        if id_reserva_qs:
            try:
                id_reserva_int = int(id_reserva_qs)

                # Obtener la reserva tal como está en la API
                reserva = api_reserva.obtener_reserva_por_id(id_reserva_int)
                ## RESERVA
                if reserva:

                    dto = {
                        "idReserva": reserva["IdReserva"],
                        "idUnicoUsuario": int(usuario_id),  # 👈 AQUÍ ASOCIAMOS AL USUARIO INTERNO
                        "idUnicoUsuarioExterno": reserva.get("IdUnicoUsuarioExterno"),
                        "costoTotalReserva": reserva.get("CostoTotalReserva"),
                        "fechaRegistroReserva": reserva.get("FechaRegistroReserva"),
                        # Si la reserva no tiene fecha de inicio, usamos el de la pre-reserva
                        "fechaInicioReserva": reserva.get("FechaInicioReserva") or fecha_inicio_hold_qs,
                        "fechaFinalReserva": reserva.get("FechaFinalReserva"),
                        # Si no hay estado, ponemos PRE-RESERVA para que se entienda
                        "estadoGeneralReserva": reserva.get("EstadoGeneralReserva") or "PRE-RESERVA",
                        "estadoReserva": reserva.get("EstadoReserva"),
                    }

                    api_reserva.actualizar_reserva(id_reserva_int, dto)
                    print(f"[RESERVAS] Asociada reserva {id_reserva_int} al usuario {usuario_id}")

                else:
                    print(f"[RESERVAS] No se encontró la reserva {id_reserva_int} para asociar")

            except Exception as e:
                print("[RESERVAS] Error asociando reserva a usuario:", e)

        # =========================================
        # 3) CARGAR TODO EN PARALELO
        # =========================================
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

        reservas_api = datos["reservas_api"] or []
        habxres_list = datos["habxres_list"] or []
        hold_list = datos["hold_list"] or []
        imgs_list = datos["imgs_list"] or []

        # =========================================
        # 4) FILTRAR SOLO RESERVAS DEL USUARIO
        # =========================================
        reservas_filtradas = [
            r for r in reservas_api
            if str(r.get("IdUnicoUsuario")) == str(usuario_id)
        ]

        # =========================================
        # 5) ÍNDICES AUXILIARES
        # =========================================
        # habxres por reserva
        idx_habxres = {h["IdReserva"]: h for h in habxres_list}

        # hold por reserva (si en tu API el HOLD tiene IdReserva)
        idx_hold = {h["IdReserva"]: h for h in hold_list if h.get("IdReserva")}

        # imágenes por habitación
        idx_imagenes = {}
        for img in imgs_list:
            if img.get("EstadoImagen"):
                hab_id = img.get("IdHabitacion")
                if hab_id not in idx_imagenes:
                    idx_imagenes[hab_id] = img.get("UrlImagen")

        # habitaciones a consultar
        habitaciones_ids = set()
        for r in reservas_filtradas:
            id_res = r.get("IdReserva")
            hxr = idx_habxres.get(id_res, {})
            id_habitacion = hxr.get("IdHabitacion")
            if id_habitacion:
                habitaciones_ids.add(id_habitacion)

        # =========================================
        # 6) CARGAR HABITACIONES EN PARALELO
        # =========================================
        idx_habitaciones = {}

        def cargar_habitacion(hab_id):
            try:
                hab_data = api_habs.obtener_por_id(hab_id)
                idx_habitaciones[hab_id] = hab_data
            except Exception as e:
                print(f"[RESERVAS] Error cargando habitación {hab_id}:", e)
                idx_habitaciones[hab_id] = {}

        threads_hab = [
            threading.Thread(target=cargar_habitacion, args=(hab_id,))
            for hab_id in habitaciones_ids
        ]
        for t in threads_hab:
            t.start()
        for t in threads_hab:
            t.join()

        # =========================================
        # 7) ARMAR LA LISTA FINAL DE RESERVAS
        # =========================================
        reservas_final = []

        # -----------------------------------
        # CONSTRUIR RESERVAS
        # -----------------------------------
        for r in reservas_filtradas:
            id_res = r.get("IdReserva")

            # HABXRES
            hxr = idx_habxres.get(id_res, {})
            id_habitacion = hxr.get("IdHabitacion")

            # HOLD (si existe)
            hold = idx_hold.get(id_res, {})
            id_hold = hold.get("IdHold")

            # ====== CÁLCULO DE TIEMPO RESTANTE DEL HOLD ======
            hold_tiempo_total = hold.get("TiempoHold") or hold.get("tiempoHold")
            hold_fecha_inicio_raw = hold.get("FechaInicioHold") or hold.get("fechaInicioHold")

            hold_restante_segundos = None
            hold_expirado = False
            hold_fecha_fin_iso = None

            if hold_fecha_inicio_raw and hold_tiempo_total:
                try:
                    # convertir a datetime
                    inicio_dt = datetime.fromisoformat(str(hold_fecha_inicio_raw))
                    if timezone.is_naive(inicio_dt):
                        inicio_dt = timezone.make_aware(inicio_dt, timezone.get_default_timezone())

                    fin_dt = inicio_dt + timedelta(seconds=int(hold_tiempo_total))
                    ahora = timezone.now()

                    restante = (fin_dt - ahora).total_seconds()
                    hold_restante_segundos = max(0, int(restante))
                    hold_expirado = restante <= 0
                    hold_fecha_fin_iso = fin_dt.isoformat()

                except Exception as e:
                    print("[RESERVAS] Error calculando tiempo restante de HOLD:", e)

            # HABITACIÓN
            hab_data = idx_habitaciones.get(id_habitacion, {})
            capacidad_habitacion = hab_data.get("CapacidadHabitacion")

            # IMAGEN
            imagen_final = (
                    idx_imagenes.get(id_habitacion)
                    or "https://imageness3realdecuenca.s3.us-east-2.amazonaws.com/Imagen4.png"
            )

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

                # CAMPOS NUEVOS DEL HOLD 👇
                "hold_id": id_hold,
                "hold_tiempo_total": hold_tiempo_total,
                "hold_fecha_inicio": hold_fecha_inicio_raw,
                "hold_fecha_fin": hold_fecha_fin_iso,
                "hold_restante_segundos": hold_restante_segundos,
                "hold_expirado": hold_expirado,
            })

        elapsed = time.time() - start_time
        print(f"[PERF] MisReservasView: {elapsed:.2f}s")

        # 👈 SIEMPRE devolvemos un HttpResponse
        return render(request, self.template_name, {"reservas": reservas_final})


###############################################################
###############################################################
###############################################################
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


###############################################################
###############################################################
###############################################################


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


###############################################################
###############################################################
###############################################################


## FUNCIONES PARA GENERAR PRERESERVA
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

    # número de huéspedes
    try:
        numero_huespedes = int(request.POST.get("numeroHuespedes", "1"))
    except ValueError:
        numero_huespedes = 1

    nombre = request.POST.get("nombre")
    apellido = request.POST.get("apellido")
    tipo_documento = request.POST.get("tipoDocumento")
    documento = request.POST.get("documento")
    correo = request.POST.get("correo")  # 👈 asegúrate de que el form envíe este campo

    # ---------- PRECIO: NORMALIZAR STRING ----------
    raw_precio = (request.POST.get("precioActual") or "").strip()

    if not raw_precio:
        precio_actual = 0.0
    else:
        # quitar espacios y símbolo de moneda si viene
        raw_precio = (
            raw_precio
            .replace(" ", "")
            .replace("$", "")
        )
        # cambiar coma por punto: "1,0" → "1.0"
        raw_precio = raw_precio.replace(",", ".")

        try:
            precio_actual = float(raw_precio)
        except ValueError:
            return JsonResponse(
                {"error": f"Precio inválido: {raw_precio}"},
                status=400
            )

    usuario_id = request.POST.get("usuarioId")

    if not usuario_id:
        return JsonResponse({"error": "Usuario no identificado"}, status=400)

    # === Llamar al servicio REST ===
    api = FuncionesEspecialesGestionRest()
    print("************************* SE GENERA LA PRERESERVA *************************")
    print(
        f"""
        id_habitacion: {id_habitacion}
        fecha_inicio: {fecha_inicio}
        fecha_fin: {fecha_fin}
        numero_huespedes: {numero_huespedes}
        nombre: {nombre}
        apellido: {apellido}
        correo: {correo}
        tipo_documento: {tipo_documento}
        documento: {documento}
        duracion_hold_seg: 180
        precio_actual: {precio_actual}
        """
    )
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
            precio_actual=precio_actual,
        )
        print("========== RESPUESTA DE crear_prereserva ==========")
        print(resultado)
        print("===================================================")

        # Obtener el ID del HOLD de la respuesta (puede venir con diferentes nombres)
        hold_id = resultado.get("IdHold") or resultado.get("idHold") or resultado.get("holdId")

        # Variables por defecto
        reserva_id = None
        tiempo_hold = 180
        fecha_inicio_hold = fecha_inicio

        if not hold_id:
            # Si no hay hold_id, usamos los datos que vengan en la misma respuesta
            reserva_id = resultado.get("IdReserva") or resultado.get("idReserva")
            tiempo_hold = resultado.get("TiempoHold") or resultado.get("tiempoHold") or 180
            fecha_inicio_hold = resultado.get("FechaInicioHold") or resultado.get("fechaInicioHold") or fecha_inicio

            if not reserva_id:
                return JsonResponse({
                    "error": "La respuesta del servidor no contiene la información necesaria. "
                             f"Respuesta recibida: {resultado}"
                }, status=500)

        else:
            # 2) Obtener información extendida del HOLD usando el ID
            hold_api = HoldGestionRest()
            try:
                hold = hold_api.obtener_hold_por_id(str(hold_id))

                if not hold:
                    reserva_id = resultado.get("IdReserva") or resultado.get("idReserva")
                    tiempo_hold = resultado.get("TiempoHold") or resultado.get("tiempoHold") or 180
                    fecha_inicio_hold = resultado.get("FechaInicioHold") or resultado.get(
                        "fechaInicioHold") or fecha_inicio
                else:
                    reserva_id = hold.get("IdReserva") or hold.get("idReserva")
                    tiempo_hold = hold.get("TiempoHold") or hold.get("tiempoHold") or 180
                    fecha_inicio_hold = hold.get("FechaInicioHold") or hold.get("fechaInicioHold") or fecha_inicio

            except ValueError as ve:
                reserva_id = resultado.get("IdReserva") or resultado.get("idReserva")
                tiempo_hold = resultado.get("TiempoHold") or resultado.get("tiempoHold") or 180
                fecha_inicio_hold = resultado.get("FechaInicioHold") or resultado.get("fechaInicioHold") or fecha_inicio

                if not reserva_id:
                    return JsonResponse({"error": f"Error al obtener el HOLD: {ve}"}, status=400)

            except Exception as e:
                reserva_id = resultado.get("IdReserva") or resultado.get("idReserva")
                tiempo_hold = resultado.get("TiempoHold") or resultado.get("tiempoHold") or 180
                fecha_inicio_hold = resultado.get("FechaInicioHold") or resultado.get("fechaInicioHold") or fecha_inicio

                if not reserva_id:
                    return JsonResponse({"error": f"Error al obtener información del HOLD: {e}"}, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    programar_cancelacion_hold(hold_id)

    params = urlencode({
        "uid": usuario_id,  # opcional ahora
        "correo": correo,
        "nombre": nombre,
        "apellido": apellido,
        "id_reserva_reserva": reserva_id,
        "fecha_inicio_hold_reserva": fecha_inicio_hold,
        "tiempo_hold_reserva": tiempo_hold,
        "id_hold_reserva": hold_id,
    })

    return redirect(f"/usuario/reservas/?{params}")


## FUNCIONES PARA CONFIRMAR RESERVA
@method_decorator(csrf_exempt, name="dispatch")
class ConfirmarReservaInternaAjax(View):

    def post(self, request):
        try:
            data = json.loads(request.body)

            idHabitacion = data.get("idHabitacion")
            idHold = data.get("idHold")
            idUnicoUsuario = data.get("idUnicoUsuario")
            fechaInicio = data.get("fechaInicio")
            fechaFin = data.get("fechaFin")
            numeroHuespedes = data.get("numeroHuespedes")

            nombre = data.get("nombre")
            apellido = data.get("apellido")
            correo = data.get("correo")
            tipoDocumento = data.get("tipoDocumento")
            documento = data.get("documento")

            # ==========================================
            # 2. VALIDACIONES
            # ==========================================
            required = {
                "idHabitacion": idHabitacion,
                "idHold": idHold,
                "idUnicoUsuario": idUnicoUsuario,
                "fechaInicio": fechaInicio,
                "fechaFin": fechaFin,
                "numeroHuespedes": numeroHuespedes,
                "correo": correo,
            }

            faltantes = [k for k, v in required.items() if not v]

            if faltantes:
                return JsonResponse(
                    {"ok": False, "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"},
                    status=400
                )

            try:
                idUnicoUsuario = int(idUnicoUsuario)
                numeroHuespedes = int(numeroHuespedes)
            except ValueError:
                return JsonResponse(
                    {"ok": False, "error": "idUnicoUsuario o numeroHuespedes no son válidos"},
                    status=400
                )

            if numeroHuespedes <= 0:
                return JsonResponse(
                    {"ok": False, "error": "numeroHuespedes debe ser mayor a 0"},
                    status=400
                )

            # ==========================================
            # 3. CONFIRMAR RESERVA (API REST)
            # ==========================================
            api = FuncionesEspecialesGestionRest()

            resultado = api.confirmar_reserva_interna(
                idHabitacion=idHabitacion,
                idHold=idHold,
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                tipoDocumento=tipoDocumento,
                documento=documento,
                fechaInicio=fechaInicio,
                fechaFin=fechaFin,
                numeroHuespedes=numeroHuespedes,
            )


            # ==========================================
            # 4. VALIDAR RESPUESTA DEL SP
            # ==========================================
            idReserva = resultado.get("IdReserva")

            if not idReserva:
                return JsonResponse(
                    {"ok": False, "error": "La API no devolvió IdReserva"},
                    status=400
                )

            # ==========================================
            # 5. ASOCIAR USUARIO INTERNO
            # ==========================================
            api_reserva = ReservaGestionRest()

            dto = {
                "idReserva": idReserva,
                "idUnicoUsuario": idUnicoUsuario,
                "idUnicoUsuarioExterno": None,
                "costoTotalReserva": resultado.get("CostoTotalReserva"),
                "fechaRegistroReserva": resultado.get("FechaRegistro"),
                "fechaInicioReserva": resultado.get("FechaInicio"),
                "fechaFinalReserva": resultado.get("FechaFin"),
                "estadoGeneralReserva": "CONFIRMADO",
                "estadoReserva": True,
            }

            api_reserva.actualizar_reserva(idReserva, dto)

            print(f"[OK] Reserva {idReserva} asociada al usuario {idUnicoUsuario}")

            # ==========================================
            # 6. EMITIR FACTURA
            # ==========================================
            factura = api.emitir_factura_interna(
                idReserva=idReserva,
                correo=correo,
                nombre=nombre,
                apellido=apellido,
                tipoDocumento=tipoDocumento,
                documento=documento or "",
            )


            # ------------------------
            # 7. GENERAR PDF
            # ------------------------
            id_factura = factura.get("IdFactura")
            if not id_factura:
                return JsonResponse({"ok": False, "error": "Factura sin Id"}, status=400)
            # ==========================================
            # 8. EJECUTAR PAGO EN BANCA EXTERNA
            # ==========================================
            costo = resultado.get("CostoTotalReserva")

            if not costo:
                return JsonResponse({"ok": False, "error": "No se pudo obtener el monto del pago"}, status=400)

            try:
                respuesta_banca = ejecutar_pago_banca_interno(costo)
            except Exception as e:
                return JsonResponse({
                    "ok": False,
                    "error": "La reserva se creó pero el pago falló",
                    "detalle": str(e)
                }, status=502)

            pdf_bytes = generar_pdf_factura_html(
                id_factura,
                {
                    "id_reserva": idReserva,
                    "cliente": f"{nombre} {apellido}",
                    "total": resultado.get("CostoTotalReserva"),
                }
            )

            ruta = f"facturas/carlos/{id_factura}.pdf"
            url_pdf = subir_pdf_a_s3(pdf_bytes, ruta)


            # ==========================================
            # 8. RESPUESTA FINAL
            # ==========================================
            return JsonResponse({
                "ok": True,
                "idReserva": idReserva,
                "idFactura": id_factura,
                "urlFactura": url_pdf,
            })

        except Exception as e:
            print("[ERROR CONFIRMAR]", str(e))
            return JsonResponse(
                {"ok": False, "error": str(e)},
                status=500
            )

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
            print("id_hold = ", id_hold)
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
        # correo, pero realmente no hace nada, solo ejecutamos la api
        # http://mibanca.runasp.net/api/Transacciones/{cuenta_origen}/{cuenta_destino}/{monto}
        # y se ejecuta los dos rest o soap de
        None


###############################################################
###############################################################
###############################################################


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

from servicios.soap.gestion.FacturaGestionSoap import FacturaGestionSoap as FacturasGestionRest
from servicios.soap.gestion.PdfGestionSoap import PdfGestionSoap
from fpdf import FPDF

from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime
from utils.utils_pdf import generar_pdf_factura_html
from utils.s3_upload import subir_pdf_a_s3


@csrf_exempt
def generar_pdf_factura(request):
    """
    Endpoint: POST /api/generar-pdf-reserva/
    Espera un JSON con:
    {
        "idFactura": 188,
        "idReserva": 180,
        "cliente": "Nombre Apellido",
        "total": 99.99
    }
    Genera el PDF, lo sube a S3 y devuelve la URL.
    """
    if request.method != "POST":
        return JsonResponse(
            {"ok": False, "error": "Método no permitido (use POST)"},
            status=405
        )

    # -------- OBTENER JSON DEL BODY --------
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse(
            {"ok": False, "error": "Body debe ser JSON válido"},
            status=400
        )

    id_factura = data.get("idFactura") or data.get("id_factura")
    id_reserva = data.get("idReserva") or data.get("id_reserva")
    cliente = data.get("cliente")
    total = data.get("total")

    # -------- VALIDACIONES --------
    if not id_factura:
        return JsonResponse({"ok": False, "error": "idFactura es obligatorio"}, status=400)
    if not id_reserva:
        return JsonResponse({"ok": False, "error": "idReserva es obligatorio"}, status=400)
    if total is None:
        return JsonResponse({"ok": False, "error": "total es obligatorio"}, status=400)

    try:
        id_factura = int(id_factura)
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "idFactura debe ser numérico"}, status=400)

    # -------- GENERAR PDF EN MEMORIA --------
    try:
        pdf_bytes = generar_pdf_factura_html(
            id_factura,
            {
                "id_reserva": id_reserva,
                "cliente": cliente,
                "total": total,
            }
        )
    except Exception as e:
        return JsonResponse({"ok": False, "error": f"Error al generar PDF: {e}"}, status=500)

    # -------- SUBIR A S3 --------
    try:
        filename = f"facturas/carlos/pdf{id_factura}.pdf"
        url_pdf_final = subir_pdf_a_s3(pdf_bytes, filename)
    except Exception as e:
        return JsonResponse({"ok": False, "error": f"Error al subir PDF a S3: {e}"}, status=500)

    # -------- RESPUESTA OK --------
    return JsonResponse(
        {
            "ok": True,
            "idFactura": id_factura,
            "idReserva": id_reserva,
            "url_pdf": url_pdf_final,
        }
    )


################################################################
################################################################
def programar_cancelacion_hold(id_hold: str):
    """
    Obtiene la información del HOLD desde el API y programa,
    en un thread, la cancelación automática cuando venza.
    """
    if not id_hold:
        return

    try:
        hold_api = HoldGestionRest()
        hold = hold_api.obtener_hold_por_id(id_hold)

        if not hold:
            print(f"[HOLD] No se encontró el HOLD {id_hold}")
            return

        # Los nombres pueden venir con diferentes mayúsculas
        tiempo_hold = hold.get("TiempoHold") or hold.get("tiempoHold")
        fecha_inicio_str = hold.get("FechaInicioHold") or hold.get("fechaInicioHold")

        if tiempo_hold is None or not fecha_inicio_str:
            print(
                f"[HOLD] Datos incompletos para {id_hold}. tiempo_hold={tiempo_hold}, fecha_inicio={fecha_inicio_str}")
            return

        # Parsear la fecha de inicio (ISO 8601)
        fecha_inicio = datetime.fromisoformat(fecha_inicio_str.replace("Z", "+00:00"))
        expiracion = fecha_inicio + timedelta(seconds=int(tiempo_hold))

        # Tiempo restante desde ahora
        ahora = datetime.utcnow().replace(tzinfo=fecha_inicio.tzinfo)
        segundos_restantes = (expiracion - ahora).total_seconds()

        if segundos_restantes <= 0:
            segundos_restantes = 1  # cancelar casi inmediato

        def _cancelar():
            try:
                print(f"[HOLD] Cancelando pre-reserva para HOLD {id_hold}...")
                FuncionesEspecialesGestionRest().cancelar_prereserva(id_hold)
                print(f"[HOLD] HOLD {id_hold} cancelado correctamente.")
            except Exception as e:
                print(f"[HOLD] Error al cancelar HOLD {id_hold}: {e}")

        t = threading.Timer(segundos_restantes, _cancelar)
        t.daemon = True
        t.start()
        print(f"[HOLD] Programada cancelación de {id_hold} en {segundos_restantes:.0f} segundos")

    except Exception as e:
        print(f"[HOLD] Error al programar cancelación para {id_hold}: {e}")


def vista_pago(request):
    """
    Muestra la página de pago (formulario).
    """
    return render(request, "webapp/test/pago.html")
def ejecutar_pago_banca_interno(monto):
    """
    Ejecuta el pago contra la API bancaria y retorna dict resultado.
    Lanza excepción si falla.
    """
    data = {
        "cuenta_origen": settings.CUENTA_USUARIO_ID,
        "cuenta_destino": settings.CUENTA_ADMIN_ID,
        "monto": float(monto),
        "fecha_transaccion": timezone.now().isoformat(),
        "tipo_transaccion": "Pago",
    }

    url = f"{settings.URL_BANCA_APP}/api/Transacciones"
    response = requests.post(url, json=data, timeout=10)
    response.raise_for_status()

    return response.text   # XML o texto
