# =============================
# HABITACIONES CRUD - ADM VIEWS
# =============================

from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import time
import logging
from requests.exceptions import ConnectionError, Timeout, HTTPError

from servicios.soap.gestion.HabitacionGestionSoap import HabitacionesGestionSoap as HabitacionesGestionRest
from webapp.decorators import admin_required, admin_required_ajax

logger = logging.getLogger(__name__)


# ============================================================
# VIEW HTML PRINCIPAL
# ============================================================
@method_decorator(admin_required, name='dispatch')
class HabitacionesView(View):
    template_name = "webapp/usuario/administrador/crud/habitaciones/index.html"

    def get(self, request):
        return render(request, self.template_name)


# ============================================================
# LISTAR CON PAGINACIÓN (CON LÍMITE DURO)
# ============================================================
@method_decorator(admin_required_ajax, name='dispatch')
class HabitacionesListAjaxView(View):

    PAGE_SIZE = 20
    MAX_PAGES = 50  # 👉 Máximo de páginas que vamos a exponer (50 * 20 = 1000 registros)

    def get(self, request):
        api = HabitacionesGestionRest()

        try:
            start_time = time.time()

            # página solicitada
            try:
                page = int(request.GET.get("page", 1))
            except ValueError:
                page = 1
            if page < 1:
                page = 1

            # Traer datos desde la API
            data = api.obtener_habitaciones()
            if not isinstance(data, list):
                data = []

            total_real = len(data)  # cuántos vienen realmente de la API

            # ---- LÍMITE DURO DE REGISTROS ----
            max_records = self.PAGE_SIZE * self.MAX_PAGES   # 1000
            truncated = False

            if total_real > max_records:
                truncated = True
                data = data[:max_records]  # solo trabajamos con los primeros 1000

            total = len(data)  # puede ser <= total_real
            total_pages = (total + self.PAGE_SIZE - 1) // self.PAGE_SIZE

            # Si piden página más grande que la disponible, ajustar
            if page > total_pages:
                page = total_pages or 1

            start = (page - 1) * self.PAGE_SIZE
            end = start + self.PAGE_SIZE
            paginados = data[start:end]

            elapsed = time.time() - start_time
            logger.info(
                f"[HAB LIST] page={page}/{total_pages}{'+' if truncated else ''} "
                f"registros_page={len(paginados)} total_real={total_real} "
                f"procesado_en={elapsed:.2f}s"
            )

            return JsonResponse({
                "status": "ok",
                "data": paginados,
                "page": page,
                "total_pages": total_pages,      # hasta 50 máx
                "total_records": total_real,     # lo que realmente hay en la API
                "truncated": truncated           # True si hubo recorte
            })

        except ConnectionError:
            return JsonResponse(
                {"status": "error", "message": "No se pudo conectar al servidor"},
                status=503
            )
        except Timeout:
            return JsonResponse(
                {"status": "error", "message": "Timeout del servidor"},
                status=504
            )
        except HTTPError:
            return JsonResponse(
                {"status": "error", "message": "Error en el servidor externo"},
                status=500
            )
        except Exception as e:
            logger.error(e)
            return JsonResponse(
                {"status": "error", "message": "Error interno"},
                status=500
            )

# ============================================================
# OBTENER UNO
# ============================================================
@method_decorator(admin_required_ajax, name='dispatch')
class HabitacionesGetAjaxView(View):

    def get(self, request, id_habitacion):
        api = HabitacionesGestionRest()
        try:
            data = api.obtener_por_id(id_habitacion)
            return JsonResponse({"status": "ok", "data": data})

        except ConnectionError:
            return JsonResponse({"status": "error", "message": "No se pudo conectar"}, status=503)
        except Timeout:
            return JsonResponse({"status": "error", "message": "Timeout del servidor"}, status=504)
        except Exception:
            return JsonResponse({"status": "error", "message": "Registro no encontrado"}, status=404)


# ============================================================
# CREAR
# ============================================================
@method_decorator([csrf_exempt, admin_required_ajax], name='dispatch')
class HabitacionesCreateAjaxView(View):

    def post(self, request):

        ids = {
            "IdHabitacion": "ID Habitación",
            "IdTipoHabitacion": "Tipo de habitación",
            "IdCiudad": "Ciudad",
            "IdHotel": "Hotel",
            "NombreHabitacion": "Nombre"
        }

        for key, label in ids.items():
            if not request.POST.get(key):
                return JsonResponse({"status": "error", "message": f"{label} es requerido"}, status=400)

        try:
            api = HabitacionesGestionRest()

            api.crear_habitacion(
                request.POST.get("IdHabitacion"),
                int(request.POST.get("IdTipoHabitacion")),
                int(request.POST.get("IdCiudad")),
                int(request.POST.get("IdHotel")),
                request.POST.get("NombreHabitacion"),
                request.POST.get("PrecioNormalHabitacion") or None,
                request.POST.get("PrecioActualHabitacion") or None,
                request.POST.get("CapacidadHabitacion") or None,
                request.POST.get("EstadoHabitacion") or None,
                request.POST.get("EstadoActivoHabitacion") == "true"
            )

            return JsonResponse({"status": "ok", "message": "Habitación creada correctamente"})

        except ValueError as ve:
            return JsonResponse({"status": "error", "message": f"Error de datos: {str(ve)}"}, status=400)
        except ConnectionError:
            return JsonResponse({"status": "error", "message": "No se pudo conectar"}, status=503)
        except Timeout:
            return JsonResponse({"status": "error", "message": "Timeout del servidor"}, status=504)
        except Exception as e:
            logger.error(e)
            return JsonResponse({"status": "error", "message": "Error al crear"}, status=500)


# ============================================================
# ACTUALIZAR
# ============================================================
@method_decorator([csrf_exempt, admin_required_ajax], name='dispatch')
class HabitacionesUpdateAjaxView(View):

    def post(self, request, id_habitacion):

        campos = ["IdTipoHabitacion", "IdCiudad", "IdHotel", "NombreHabitacion"]

        for campo in campos:
            if not request.POST.get(campo):
                return JsonResponse({"status": "error", "message": f"{campo} es obligatorio"}, status=400)

        try:
            api = HabitacionesGestionRest()

            estado_raw = request.POST.get("EstadoActivoHabitacion")

            if estado_raw:
                estado = estado_raw.lower() == "true"
            else:
                registro = api.obtener_por_id(id_habitacion)
                estado = registro.get("EstadoActivoHabitacion", True) if registro else True

            api.actualizar_habitacion(
                id_habitacion,
                int(request.POST.get("IdTipoHabitacion")),
                int(request.POST.get("IdCiudad")),
                int(request.POST.get("IdHotel")),
                request.POST.get("NombreHabitacion"),
                request.POST.get("PrecioNormalHabitacion") or None,
                request.POST.get("PrecioActualHabitacion") or None,
                request.POST.get("CapacidadHabitacion") or None,
                request.POST.get("EstadoHabitacion") or None,
                estado
            )

            return JsonResponse({"status": "ok", "message": "Habitación actualizada"})

        except ValueError as ve:
            return JsonResponse({"status": "error", "message": f"Datos inválidos: {str(ve)}"}, status=400)
        except ConnectionError:
            return JsonResponse({"status": "error", "message": "No se pudo conectar"}, status=503)
        except Timeout:
            return JsonResponse({"status": "error", "message": "Timeout del servidor"}, status=504)
        except Exception as e:
            logger.error(e)
            return JsonResponse({"status": "error", "message": "No se pudo actualizar"}, status=500)


# ============================================================
# ELIMINAR
# ============================================================
@method_decorator([csrf_exempt, admin_required_ajax], name='dispatch')
class HabitacionesDeleteAjaxView(View):

    def post(self, request, id_habitacion):

        api = HabitacionesGestionRest()

        try:
            api.eliminar_habitacion(id_habitacion)
            return JsonResponse({"status": "ok", "message": "Habitación eliminada"})

        except ConnectionError:
            return JsonResponse({"status": "error", "message": "No se pudo conectar"}, status=503)
        except Timeout:
            return JsonResponse({"status": "error", "message": "Timeout del servidor"}, status=504)
        except Exception:
            return JsonResponse({"status": "error", "message": "No se pudo eliminar"}, status=500)


# ============================================================
# OBTENER SIGUIENTE ID (CUALQUIER PREFIJO DE 4 CARACTERES)
# ============================================================
@method_decorator(admin_required_ajax, name='dispatch')
class HabitacionesNextIdAjaxView(View):
    """
    Calcula el siguiente ID de habitación basado en el ID numérico más alto
    encontrado, manteniendo su prefijo de 4 caracteres.
    """

    def get(self, request):
        api = HabitacionesGestionRest()

        try:
            data = api.obtener_habitaciones()

            if not isinstance(data, list):
                data = []

            max_number = 0
            # Inicializamos best_prefix a None o cadena vacía, y el prefijo por defecto final
            best_prefix = ""
            suffix_length = 6  # Longitud por defecto del sufijo (ej. 000001)

            # 2. Iterar y encontrar el ID numérico máximo
            for habitacion in data:
                id_habitacion = habitacion.get("IdHabitacion")

                # a. Ignorar si no es una cadena válida o es demasiado corta (mínimo 5 caracteres: 4 prefijo + 1 sufijo)
                if not isinstance(id_habitacion, str) or len(id_habitacion) < 5:
                    continue

                # b. Extraer el prefijo (primeros 4) y el sufijo (resto)
                prefix = id_habitacion[:4]
                num_str = id_habitacion[4:]

                try:
                    # c. Intentar convertir a entero.
                    current_number = int(num_str)

                    # d. Actualizar el máximo y guardar el prefijo asociado
                    if current_number > max_number:
                        max_number = current_number
                        best_prefix = prefix  # Almacenar el prefijo del registro más grande
                        suffix_length = len(num_str)  # Almacenar la longitud del sufijo encontrado

                except ValueError:
                    # e. Si la conversión falla (dato basura), ignorar
                    continue

            # 3. Calcular el siguiente ID
            next_number = max_number + 1

            # Formatear el sufijo
            next_id_suffix = str(next_number).zfill(suffix_length)
            next_id = f"{best_prefix}{next_id_suffix}"

            return JsonResponse({
                "status": "ok",
                "next_id": next_id
            })

        except ConnectionError:
            return JsonResponse({"status": "error", "message": "No se pudo conectar para generar el ID"}, status=503)
        except Exception as e:
            logger.error(f"Error al generar siguiente ID: {e}")
            # Si hay un error, devolvemos un ID inicial de respaldo
            return JsonResponse({"status": "error", "message": "Error al generar ID"},
                                status=500)


