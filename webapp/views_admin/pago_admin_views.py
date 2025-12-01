from pprint import pprint

from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import requests
from requests.exceptions import ConnectionError, Timeout, HTTPError

from servicios.soap.gestion.PagoGestionSoap import PagoGestionSoap as PagoGestionRest
from webapp.decorators import admin_required, admin_required_ajax


# ============================================================
# VIEW PRINCIPAL (HTML)
# ============================================================
@method_decorator(admin_required, name='dispatch')
class PagoView(View):
    template_name = "webapp/usuario/administrador/crud/pago/index.html"

    def get(self, request):
        return render(request, self.template_name)


# ============================================================
# LISTA AJAX (paginado 20)
# ============================================================
@method_decorator(admin_required_ajax, name='dispatch')
class PagoListAjaxView(View):
    def get(self, request):
        page = int(request.GET.get("page", 1))
        page_size = 20

        api = PagoGestionRest()

        try:
            data = api.obtener_pagos()

            total = len(data)
            total_pages = (total + page_size - 1) // page_size

            inicio = (page - 1) * page_size
            fin = inicio + page_size

            return JsonResponse({
                "status": "ok",
                "data": data[inicio:fin],
                "page": page,
                "total_pages": total_pages
            })

        except ConnectionError:
            return JsonResponse({"status": "error", "message": "No se pudo conectar con el servidor. Verifique su conexión a internet"}, status=503)
        except Timeout:
            return JsonResponse({"status": "error", "message": "El servidor no responde. Intente nuevamente en unos momentos"}, status=504)
        except HTTPError as e:
            return JsonResponse({"status": "error", "message": f"Error en el servidor. Contacte al administrador"}, status=500)
        except ValueError as ve:
            return JsonResponse({"status": "error", "message": f"Datos inválidos: {str(ve)}"}, status=400)
        except Exception:
            return JsonResponse({"status": "error", "message": "Error al cargar la lista. Intente nuevamente"}, status=500)


# ============================================================
# OBTENER UNO
# ============================================================
@method_decorator(admin_required_ajax, name='dispatch')
class PagoGetAjaxView(View):
    def get(self, request, id_pago):
        api = PagoGestionRest()
        try:
            data = api.obtener_pago_por_id(id_pago)
            return JsonResponse({"status": "ok", "data": data})
        except ConnectionError:
            return JsonResponse({"status": "error", "message": "No se pudo conectar con el servidor"}, status=503)
        except Timeout:
            return JsonResponse({"status": "error", "message": "El servidor no responde. Intente nuevamente"}, status=504)
        except ValueError as ve:
            return JsonResponse({"status": "error", "message": f"Datos inválidos: {str(ve)}"}, status=400)
        except Exception:
            return JsonResponse({"status": "error", "message": "No se pudo obtener el registro. Verifique que el ID sea correcto"}, status=404)


# ============================================================
# CREAR
# ============================================================
@method_decorator([csrf_exempt, admin_required_ajax], name='dispatch')
class PagoCreateAjaxView(View):
    def post(self, request):
        api = PagoGestionRest()
        print("*************************** PAGO ***************************")
        pprint(request.POST)
        try:
            api.crear_pago(
                id_pago=int(request.POST.get("IdPago")),
                id_metodo_pago=int(request.POST.get("IdMetodoPago")),
                id_unico_usuario_externo=request.POST.get("IdUnicoUsuarioExterno") or None,
                id_unico_usuario=int(request.POST.get("IdUnicoUsuario")),
                id_factura=int(request.POST.get("IdFactura")),
                cuenta_origen=request.POST.get("CuentaOrigen"),
                cuenta_destino=request.POST.get("CuentaDestino"),
                monto_total=request.POST.get("MontoTotal"),
                fecha_emision=None,
                estado_pago=request.POST.get("EstadoPago") == "true"
            )
            return JsonResponse({"status": "ok", "message": "Pago creado exitosamente"})
        except ConnectionError:
            return JsonResponse({"status": "error", "message": "No se pudo conectar con el servidor. Verifique su conexión"}, status=503)
        except Timeout:
            return JsonResponse({"status": "error", "message": "El servidor no responde. Intente nuevamente"}, status=504)
        except ValueError as ve:
            return JsonResponse({"status": "error", "message": f"Datos inválidos: {str(ve)}"}, status=400)
        except Exception:
            return JsonResponse({"status": "error", "message": "No se pudo crear el registro. Verifique los datos ingresados"}, status=500)


# ============================================================
# ACTUALIZAR
# ============================================================
@method_decorator([csrf_exempt, admin_required_ajax], name='dispatch')
class PagoUpdateAjaxView(View):
    def post(self, request, id_pago):
        api = PagoGestionRest()
        try:
            # Obtener el estado actual del registro si no se envía
            estado_enviado = request.POST.get("EstadoPago")
            if estado_enviado is not None:
                estado_pago = estado_enviado == "true"
            else:
                # Obtener el estado actual del registro
                registro_actual = api.obtener_pago_por_id(id_pago)
                estado_pago = registro_actual.get("EstadoPago", True) if registro_actual else True
            
            api.actualizar_pago(
                id_pago=int(id_pago),
                id_metodo_pago=int(request.POST.get("IdMetodoPago")),
                id_unico_usuario_externo=request.POST.get("IdUnicoUsuarioExterno") or None,
                id_unico_usuario=int(request.POST.get("IdUnicoUsuario")),
                id_factura=int(request.POST.get("IdFactura")),
                cuenta_origen=request.POST.get("CuentaOrigen"),
                cuenta_destino=request.POST.get("CuentaDestino"),
                monto_total=request.POST.get("MontoTotal"),
                fecha_emision=None,
                estado_pago=estado_pago
            )
            return JsonResponse({"status": "ok", "message": "Pago actualizado exitosamente"})
        except ConnectionError:
            return JsonResponse({"status": "error", "message": "No se pudo conectar con el servidor"}, status=503)
        except Timeout:
            return JsonResponse({"status": "error", "message": "El servidor no responde. Intente nuevamente"}, status=504)
        except ValueError as ve:
            return JsonResponse({"status": "error", "message": f"Datos inválidos: {str(ve)}"}, status=400)
        except Exception:
            return JsonResponse({"status": "error", "message": "No se pudo actualizar el registro. Verifique los datos"}, status=500)


# ============================================================
# ELIMINAR
# ============================================================
@method_decorator([csrf_exempt, admin_required_ajax], name='dispatch')
class PagoDeleteAjaxView(View):
    def post(self, request, id_pago):
        api = PagoGestionRest()
        try:
            api.eliminar_pago(id_pago)
            return JsonResponse({"status": "ok", "message": "Pago eliminado exitosamente"})
        except ConnectionError:
            return JsonResponse({"status": "error", "message": "No se pudo conectar con el servidor"}, status=503)
        except Timeout:
            return JsonResponse({"status": "error", "message": "El servidor no responde. Intente nuevamente"}, status=504)
        except Exception:
            return JsonResponse({"status": "error", "message": "No se pudo eliminar el registro. Puede estar en uso"}, status=500)

@method_decorator(admin_required_ajax, name="dispatch")
class PagoNextIdAjaxView(View):
    """
    Devuelve el siguiente ID disponible para PAGO.
    Endpoint: /admin/pago/next-id/
    Respuesta: {"next": 121}
    """

    def get(self, request):
        api = PagoGestionRest()

        try:
            data = api.obtener_pagos() or []

            if not isinstance(data, list):
                data = [data]

            ids = []
            for p in data:
                raw_id = p.get("IdPago")  # viene del DTO de la API
                # Aseguramos que sea entero
                try:
                    ids.append(int(raw_id))
                except (TypeError, ValueError):
                    continue

            siguiente = max(ids) + 1 if ids else 1

            return JsonResponse({"next": siguiente})
        except Exception:
            # Si algo falla, devolvemos 1 para no romper el front
            return JsonResponse({"next": 1})

