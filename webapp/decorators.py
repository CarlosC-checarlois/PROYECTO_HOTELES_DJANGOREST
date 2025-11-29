from functools import wraps
from django.shortcuts import redirect
from django.http import JsonResponse


def admin_required(view_func):
    """
    Decorador para proteger vistas que requieren rol de administrador (rol=2).
    Redirige al inicio si no tiene permisos.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Obtener el rol y usuario_id desde las cookies
        rol = request.COOKIES.get('usuario_rol')
        usuario_id = request.COOKIES.get('usuario_id')
        
        # Debug: verificar todas las cookies
        # print(f"DEBUG - Todas las cookies: {request.COOKIES}")
        # print(f"DEBUG - usuario_rol: {rol}, usuario_id: {usuario_id}")

        # Si no hay usuario_id, no está logueado
        if not usuario_id:
            return redirect('inicio')

        # Si no hay rol o no es administrador (rol debe ser "2" como string)
        if not rol or str(rol) != "2":
            return redirect('inicio')

        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required_ajax(view_func):
    """
    Decorador para proteger vistas AJAX que requieren rol de administrador.
    Retorna JSON con error 403 si no tiene permisos.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Obtener el rol y usuario_id desde las cookies
        rol = request.COOKIES.get('usuario_rol')
        usuario_id = request.COOKIES.get('usuario_id')
        
        # Debug: verificar todas las cookies
        # print(f"DEBUG AJAX - Todas las cookies: {request.COOKIES}")
        # print(f"DEBUG AJAX - usuario_rol: {rol}, usuario_id: {usuario_id}")

        # Si no hay usuario_id, no está logueado
        if not usuario_id:
            return JsonResponse({
                "status": "error",
                "message": "Debe iniciar sesión para acceder a este recurso"
            }, status=403)

        # Si no hay rol o no es administrador (rol debe ser "2" como string)
        if not rol or str(rol) != "2":
            return JsonResponse({
                "status": "error",
                "message": "No tiene permisos para acceder a este recurso"
            }, status=403)

        return view_func(request, *args, **kwargs)

    return wrapper
