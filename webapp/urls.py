from django.urls import path
from webapp import views as views_webapp
from webapp.views_admin.amenidades_admin_ajax_views import (
    AmenidadesView,
    AmenidadesListAjaxView,
    AmenidadesCreateAjaxView,
    AmenidadesGetAjaxView,
    AmenidadesUpdateAjaxView,
    AmenidadesDeleteAjaxView,
    AmenidadesNextIdAjaxView
)

from webapp.views_admin.amexhab_admin_ajax_views import (
    AmexHabView,
    AmexHabListAjaxView,
    AmexHabGetAjaxView,
    AmexHabCreateAjaxView,
    AmexHabUpdateAjaxView,
    AmexHabDeleteAjaxView,
    HabitacionSearchAjaxView
)
from webapp.views_admin.ciudad_admin_ajax_views import (
    CiudadView,
    CiudadListAjaxView,
    CiudadGetAjaxView,
    CiudadCreateAjaxView,
    CiudadUpdateAjaxView,
    CiudadDeleteAjaxView
)
from webapp.views_admin.descuento_admin_ajax_views import (
    DescuentoView,
    DescuentoListAjaxView,
    DescuentoGetAjaxView,
    DescuentoCreateAjaxView,
    DescuentoUpdateAjaxView,
    DescuentoDeleteAjaxView,
    DescuentoNextIdAjaxView
)
# ---- DESXHABXRES ----
from webapp.views_admin.desxhabxres_views import (
    DesxHabxResView,
    DesxHabxResListAjaxView,
    DesxHabxResGetAjaxView,
    DesxHabxResCreateAjaxView,
    DesxHabxResUpdateAjaxView,
    DesxHabxResDeleteAjaxView
)

from django.urls import path
from webapp.views_admin.habitaciones_admin_views import (
    HabitacionesView,
    HabitacionesListAjaxView,
    HabitacionesGetAjaxView,
    HabitacionesCreateAjaxView,
    HabitacionesUpdateAjaxView,
    HabitacionesDeleteAjaxView,
    HabitacionesNextIdAjaxView
)

from webapp.views_admin.habxres_admin_views import (
    HabxResView,
    HabxResListAjaxView,
    HabxResGetAjaxView,
    HabxResCreateAjaxView,
    HabxResUpdateAjaxView,
    HabxResDeleteAjaxView,
    HabxResSearchAjaxView,
    HabxResNextIdAjaxView
)

from django.urls import path
from webapp.views_admin.hold_admin_views import (
    HoldView,
    HoldListAjaxView,
    HoldGetAjaxView,
    HoldCreateAjaxView,
    HoldUpdateAjaxView,
    HoldDeleteAjaxView,
    HoldNextIdAjaxView
)
from webapp.views_admin.hotel_admin_views import (
    HotelView,
    HotelListAjaxView,
    HotelGetAjaxView,
    HotelCreateAjaxView,
    HotelUpdateAjaxView,
    HotelDeleteAjaxView,
    HotelNextIdAjaxView
)

from webapp.views_admin.imagen_habitacion_admin_views import (
    ImagenHabitacionView,
    ImagenHabitacionListAjaxView,
    ImagenHabitacionGetAjaxView,
    ImagenHabitacionCreateAjaxView,
    ImagenHabitacionUpdateAjaxView,
    ImagenHabitacionDeleteAjaxView,
    ImagenHabitacionUploadAjaxView
)

from django.urls import path
from webapp.views_admin.metodo_pago_admin_views import (
    MetodoPagoView,
    MetodoPagoListAjaxView,
    MetodoPagoGetAjaxView,
    MetodoPagoCreateAjaxView,
    MetodoPagoUpdateAjaxView,
    MetodoPagoDeleteAjaxView,
    MetodoPagoSearchAjaxView
)

from django.urls import path
from webapp.views_admin.pago_admin_views import (
    PagoView,
    PagoListAjaxView,
    PagoGetAjaxView,
    PagoCreateAjaxView,
    PagoUpdateAjaxView,
    PagoDeleteAjaxView,
    PagoNextIdAjaxView
)
from django.urls import path
from webapp.views_admin.pais_admin_views import (
    PaisView,
    PaisListAjaxView,
    PaisGetAjaxView,
    PaisCreateAjaxView,
    PaisUpdateAjaxView,
    PaisDeleteAjaxView,
    PaisNextIdAjaxView
)

from django.urls import path

from webapp.views_admin.pdf_admin_views import (
    PdfView,
    PdfListAjaxView,
    PdfGetAjaxView,
    PdfCreateAjaxView,
    PdfUpdateAjaxView,
    PdfDeleteAjaxView,
    PdfUploadAjaxView,
    PdfNextIdAjaxView
)

from webapp.views_admin.reserva_admin_views import (
    ReservaView,
    ReservaListAjaxView,
    ReservaGetAjaxView,
    ReservaCreateAjaxView,
    ReservaUpdateAjaxView,
    ReservaDeleteAjaxView,
    ReservaSearchAjaxView,
    ReservaNextIdAjaxView
)
from webapp.views_admin.rol_admin_views import (
    RolView,
    RolListAjaxView,
    RolGetAjaxView,
    RolCreateAjaxView,
    RolUpdateAjaxView,
    RolDeleteAjaxView,
    RolNextIdAjaxView
)
from webapp.views_admin.habitacion_tipo_admin_views import (
    TipoHabitacionView,
    TipoHabitacionListAjaxView,
    TipoHabitacionGetAjaxView,
    TipoHabitacionCreateAjaxView,
    TipoHabitacionUpdateAjaxView,
    TipoHabitacionDeleteAjaxView,
    TipoHabitacionNextIdAjaxView
)

from webapp.views_admin.usuario_interno_admin_views import (
    UsuarioInternoView,
    UsuarioInternoListAjaxView,
    UsuarioInternoGetAjaxView,
    UsuarioInternoCreateAjaxView,
    UsuarioInternoUpdateAjaxView,
    UsuarioInternoDeleteAjaxView,
    UsuarioInternoSearchAjaxView
)
from webapp.views_admin.views_factura_admin import (
    FacturaView,
    FacturaListAjaxView,
    FacturaGetAjaxView,
    FacturaCreateAjaxView,
    FacturaUpdateAjaxView,
    FacturaDeleteAjaxView,
    FacturaSearchAjaxView,
)

urlpatterns = [

    # ===============================
    # INICIO
    # ===============================
    path("", views_webapp.index_inicio, name="inicio"),

    # ===============================
    # HABITACIONES
    # ===============================
    path("habitaciones/", views_webapp.HabitacionesView.as_view(), name="habitaciones"),
    path("habitaciones/ajax/", views_webapp.HabitacionesAjaxView.as_view(), name="habitaciones_ajax"),
    path("habitaciones/detalle/<str:id>/", views_webapp.detalle_habitacion, name="habitacion_detalle"),
    path("api/fechas-ocupadas/<str:id_habitacion>/", views_webapp.FechasOcupadasAjaxView.as_view(),
         name="fechas_ocupadas"),

    # ===============================
    # AUTENTICACIÓN
    # ===============================
    path("login/", views_webapp.index_login, name="login"),
    path("login/post/", views_webapp.login_post, name="login_post"),

    path("register/", views_webapp.index_register, name="register"),
    path("register/post/", views_webapp.register_post, name="register_post"),

    # ===============================
    # PERFIL DEL CLIENTE (READ-ONLY)
    # ===============================
    path("usuario/perfil/", views_webapp.usuario_gestion, name="usuario_perfil"),

    # ===============================
    # RESERVAS DEL CLIENTE
    # ===============================
    path("usuario/reservas/", views_webapp.MisReservasView.as_view(), name="usuario_reservas"),
    path("usuario/prereserva/", views_webapp.crear_prereserva, name="crear_prereserva"),
    path("usuario/confirmar-reserva/", views_webapp.ConfirmarReservaInternaAjax.as_view(),
         name="confirmar_reserva_interna"),
    path("usuario/cancelar-reserva/", views_webapp.CancelarReservaAjax.as_view(), name="cancelar_reserva"),

    # ===============================
    # PAGOS DEL CLIENTE
    # ===============================
    path("usuario/pagos/", views_webapp.mis_pagos, name="usuario_pagos"),

    # ===============================
    # PANEL ADMINISTRATIVO
    # ===============================
    path("admin/", views_webapp.usuario_gestion_administrador, name="admin_dashboard"),
    # ===============================
    # PANEL ADMINISTRATIVO - CRUDS
    # ===============================

    # ===============================
    # ===============================
    # ===============================

    path("admin/amenidades/", AmenidadesView.as_view(), name="amenidades_index"),

    path("admin/amenidades/", AmenidadesView.as_view(), name="amenidades_index"),

    # AJAX ENDPOINTS
    path("admin/amenidades/list/", AmenidadesListAjaxView.as_view(), name="amenidades_list_ajax"),
    path("admin/amenidades/create/", AmenidadesCreateAjaxView.as_view(), name="amenidades_create_ajax"),
    path("admin/amenidades/get/<int:id>/", AmenidadesGetAjaxView.as_view(), name="amenidades_get_ajax"),
    path("admin/amenidades/update/<int:id>/", AmenidadesUpdateAjaxView.as_view(), name="amenidades_update_ajax"),
    path("admin/amenidades/delete/<int:id>/", AmenidadesDeleteAjaxView.as_view(), name="amenidades_delete_ajax"),
    path("admin/amenidades/next-id/", AmenidadesNextIdAjaxView.as_view(), name="amenidades_next_id"),

    # ===============================
    # ===============================
    # ===============================
    path("admin/amexhab/", AmexHabView.as_view(), name="amexhab_index"),

    path("admin/amexhab/list/", AmexHabListAjaxView.as_view(), name="amexhab_list_ajax"),

    path("admin/amexhab/get/<str:id_habitacion>/<int:id_amenidad>/",
         AmexHabGetAjaxView.as_view(), name="amexhab_get_ajax"),

    path("admin/amexhab/create/", AmexHabCreateAjaxView.as_view(), name="amexhab_create_ajax"),

    path("admin/amexhab/update/<str:id_habitacion>/<int:id_amenidad>/",
         AmexHabUpdateAjaxView.as_view(), name="amexhab_update_ajax"),

    path("admin/amexhab/delete/<str:id_habitacion>/<int:id_amenidad>/",
         AmexHabDeleteAjaxView.as_view(), name="amexhab_delete_ajax"),
    #############################
    #############################
    #############################

    path("admin/ciudad/", CiudadView.as_view(), name="ciudad_index"),

    path("admin/ciudad/list/", CiudadListAjaxView.as_view(), name="ciudad_list_ajax"),
    path("admin/ciudad/get/<int:id_ciudad>/", CiudadGetAjaxView.as_view(), name="ciudad_get_ajax"),
    path("admin/ciudad/create/", CiudadCreateAjaxView.as_view(), name="ciudad_create_ajax"),
    path("admin/ciudad/update/<int:id_ciudad>/", CiudadUpdateAjaxView.as_view(), name="ciudad_update_ajax"),
    path("admin/ciudad/delete/<int:id_ciudad>/", CiudadDeleteAjaxView.as_view(), name="ciudad_delete_ajax"),
    #############################
    #############################
    #############################

    path("admin/descuento/", DescuentoView.as_view(), name="descuento_index"),
    path("admin/descuento/list/", DescuentoListAjaxView.as_view(), name="descuento_list_ajax"),
    path("admin/descuento/get/<int:id_descuento>/", DescuentoGetAjaxView.as_view(), name="descuento_get_ajax"),
    path("admin/descuento/create/", DescuentoCreateAjaxView.as_view(), name="descuento_create_ajax"),
    path("admin/descuento/update/<int:id_descuento>/", DescuentoUpdateAjaxView.as_view(), name="descuento_update_ajax"),
    path("admin/descuento/delete/<int:id_descuento>/", DescuentoDeleteAjaxView.as_view(), name="descuento_delete_ajax"),
    path("admin/descuento/next-id/", DescuentoNextIdAjaxView.as_view(), name="descuento_next_id"),

    #############################
    #############################
    #############################
    path("admin/desxhabxres/", DesxHabxResView.as_view(), name="admin_desxhabxres"),

    path("admin/desxhabxres/list/", DesxHabxResListAjaxView.as_view()),
    path("admin/desxhabxres/get/<int:id_descuento>/<int:id_habxres>/", DesxHabxResGetAjaxView.as_view()),
    path("admin/desxhabxres/create/", DesxHabxResCreateAjaxView.as_view()),
    path("admin/desxhabxres/update/<int:id_descuento>/<int:id_habxres>/", DesxHabxResUpdateAjaxView.as_view()),
    path("admin/desxhabxres/delete/<int:id_descuento>/<int:id_habxres>/", DesxHabxResDeleteAjaxView.as_view()),
    #############################
    #############################
    #############################
    path("admin/habitaciones/", HabitacionesView.as_view(), name="admin_habitaciones"),
    path("admin/habitaciones/list/", HabitacionesListAjaxView.as_view()),
    path("admin/habitaciones/get/<str:id_habitacion>/", HabitacionesGetAjaxView.as_view()),
    path("admin/habitaciones/create/", HabitacionesCreateAjaxView.as_view()),
    path("admin/habitaciones/update/<str:id_habitacion>/", HabitacionesUpdateAjaxView.as_view()),
    path("admin/habitaciones/delete/<str:id_habitacion>/", HabitacionesDeleteAjaxView.as_view()),
    path("admin/habitaciones/search/", HabitacionSearchAjaxView.as_view(), name="habitaciones_search"),
    path("admin/habitaciones/next-id/", HabitacionesNextIdAjaxView.as_view()),
    #############################
    #############################
    #############################
    path("admin/habxres/", HabxResView.as_view(), name="admin_habxres"),
    path("admin/habxres/list/", HabxResListAjaxView.as_view()),
    path("admin/habxres/get/<int:id_habxres>/", HabxResGetAjaxView.as_view()),
    path("admin/habxres/create/", HabxResCreateAjaxView.as_view()),
    path("admin/habxres/update/<int:id_habxres>/", HabxResUpdateAjaxView.as_view()),
    path("admin/habxres/delete/<int:id_habxres>/", HabxResDeleteAjaxView.as_view()),
    path("admin/habxres/search/", HabxResSearchAjaxView.as_view(), name="habxres_search"),
    path("admin/habxres/next-id/", HabxResNextIdAjaxView.as_view(), name="habxres_next_id"),  # <-- nueva

    #############################
    #############################
    #############################
    path("admin/hold/", HoldView.as_view(), name="admin_hold"),

    path("admin/hold/list/", HoldListAjaxView.as_view()),
    path("admin/hold/get/<str:id_hold>/", HoldGetAjaxView.as_view()),
    path("admin/hold/create/", HoldCreateAjaxView.as_view()),
    path("admin/hold/update/<str:id_hold>/", HoldUpdateAjaxView.as_view()),
    path("admin/hold/delete/<str:id_hold>/", HoldDeleteAjaxView.as_view()),
    path("admin/hold/next-id/", HoldNextIdAjaxView.as_view(), name="hold_next_id"),

    #############################
    #############################
    #############################
    path("admin/hotel/", HotelView.as_view(), name="admin_hotel"),

    path("admin/hotel/list/", HotelListAjaxView.as_view()),
    path("admin/hotel/get/<int:id_hotel>/", HotelGetAjaxView.as_view()),
    path("admin/hotel/create/", HotelCreateAjaxView.as_view()),
    path("admin/hotel/update/<int:id_hotel>/", HotelUpdateAjaxView.as_view()),
    path("admin/hotel/delete/<int:id_hotel>/", HotelDeleteAjaxView.as_view()),
    path("admin/hotel/next-id/", HotelNextIdAjaxView.as_view(), name="hotel_next_id"),

    #############################
    #############################
    #############################
    path("admin/imagen-habitacion/", ImagenHabitacionView.as_view(), name="admin_imagen_habitacion"),

    path("admin/imagen-habitacion/list/", ImagenHabitacionListAjaxView.as_view()),
    path("admin/imagen-habitacion/get/<int:id_imagen>/", ImagenHabitacionGetAjaxView.as_view()),
    path("admin/imagen-habitacion/create/", ImagenHabitacionCreateAjaxView.as_view()),
    path("admin/imagen-habitacion/update/<int:id_imagen>/", ImagenHabitacionUpdateAjaxView.as_view()),
    path("admin/imagen-habitacion/delete/<int:id_imagen>/", ImagenHabitacionDeleteAjaxView.as_view()),
    path(
        "admin/imagen-habitacion/upload/",
        ImagenHabitacionUploadAjaxView.as_view(),
        name="imagen_habitacion_upload",
    ),
    #############################
    #############################
    #############################

    path("admin/metodo-pago/", MetodoPagoView.as_view(), name="admin_metodo_pago"),

    path("admin/metodo-pago/list/", MetodoPagoListAjaxView.as_view()),
    path("admin/metodo-pago/get/<int:id_metodo>/", MetodoPagoGetAjaxView.as_view()),
    path("admin/metodo-pago/create/", MetodoPagoCreateAjaxView.as_view()),
    path("admin/metodo-pago/update/<int:id_metodo>/", MetodoPagoUpdateAjaxView.as_view()),
    path("admin/metodo-pago/delete/<int:id_metodo>/", MetodoPagoDeleteAjaxView.as_view()),
    path(
        "admin/metodo-pago/search/",
        MetodoPagoSearchAjaxView.as_view(),
        name="metodo_pago_search"
    ),
    #############################
    #############################
    #############################
    path("admin/pago/", PagoView.as_view(), name="admin_pago"),

    path("admin/pago/list/", PagoListAjaxView.as_view()),
    path("admin/pago/get/<int:id_pago>/", PagoGetAjaxView.as_view()),
    path("admin/pago/create/", PagoCreateAjaxView.as_view()),
    path("admin/pago/update/<int:id_pago>/", PagoUpdateAjaxView.as_view()),
    path("admin/pago/delete/<int:id_pago>/", PagoDeleteAjaxView.as_view()),
    path("admin/pago/next-id/", PagoNextIdAjaxView.as_view(), name="pago_next_id"),

    #############################
    #############################
    #############################
    path("admin/pais/", PaisView.as_view(), name="admin_pais"),
    path("admin/pais/list/", PaisListAjaxView.as_view()),
    path("admin/pais/get/<int:id_pais>/", PaisGetAjaxView.as_view()),
    path("admin/pais/create/", PaisCreateAjaxView.as_view()),
    path("admin/pais/update/<int:id_pais>/", PaisUpdateAjaxView.as_view()),
    path("admin/pais/delete/<int:id_pais>/", PaisDeleteAjaxView.as_view()),
    path("admin/pais/next-id/", PaisNextIdAjaxView.as_view(), name="pais_next_id"),

    #############################
    #############################
    #############################
    path("admin/pdf/", PdfView.as_view(), name="admin_pdf"),

    path("admin/pdf/list/", PdfListAjaxView.as_view()),
    path("admin/pdf/get/<int:id_pdf>/", PdfGetAjaxView.as_view()),
    path("admin/pdf/create/", PdfCreateAjaxView.as_view()),
    path("admin/pdf/update/<int:id_pdf>/", PdfUpdateAjaxView.as_view()),
    path("admin/pdf/delete/<int:id_pdf>/", PdfDeleteAjaxView.as_view()),
    path("admin/pdf/next-id/", PdfNextIdAjaxView.as_view(), name="pdf_next_id"),

    path("admin/pdf/upload/", PdfUploadAjaxView.as_view(), name="pdf_upload"),  # <— nuevo
    #############################
    #############################
    #############################
    path("admin/reservas/", ReservaView.as_view(), name="admin_reservas"),
    path("admin/reservas/list/", ReservaListAjaxView.as_view()),
    path("admin/reservas/get/<int:id_reserva>/", ReservaGetAjaxView.as_view()),
    path("admin/reservas/create/", ReservaCreateAjaxView.as_view()),
    path("admin/reservas/update/<int:id_reserva>/", ReservaUpdateAjaxView.as_view()),
    path("admin/reservas/delete/<int:id_reserva>/", ReservaDeleteAjaxView.as_view()),
    path("admin/reservas/search/", ReservaSearchAjaxView.as_view(), name="reservas_search"),
    path("admin/reservas/next-id/", ReservaNextIdAjaxView.as_view(), name="admin_reserva_next_id"),  # <-- NUEVA

    #############################
    #############################
    #############################
    path("admin/rol/", RolView.as_view()),
    path("admin/rol/list/", RolListAjaxView.as_view()),
    path("admin/rol/get/<int:id_rol>/", RolGetAjaxView.as_view()),
    path("admin/rol/create/", RolCreateAjaxView.as_view()),
    path("admin/rol/update/<int:id_rol>/", RolUpdateAjaxView.as_view()),
    path("admin/rol/delete/<int:id_rol>/", RolDeleteAjaxView.as_view()),
path("admin/rol/next-id/", RolNextIdAjaxView.as_view(), name="rol_next_id"),

    #############################
    ###################generar-pdf-reserva##########
    #############################
    path("admin/tipos-habitacion/", TipoHabitacionView.as_view()),
    path("admin/tipos-habitacion/list/", TipoHabitacionListAjaxView.as_view()),
    path("admin/tipos-habitacion/get/<int:id_tipo>/", TipoHabitacionGetAjaxView.as_view()),
    path("admin/tipos-habitacion/create/", TipoHabitacionCreateAjaxView.as_view()),
    path("admin/tipos-habitacion/update/<int:id_tipo>/", TipoHabitacionUpdateAjaxView.as_view()),
    path("admin/tipos-habitacion/delete/<int:id_tipo>/", TipoHabitacionDeleteAjaxView.as_view()),
    path("admin/tipos-habitacion/next-id/", TipoHabitacionNextIdAjaxView.as_view(), name="tipohab_next_id"),

    #############################
    #############################
    #############################
    path("admin/usuarios-internos/", UsuarioInternoView.as_view()),
    path("admin/usuarios-internos/list/", UsuarioInternoListAjaxView.as_view()),
    path("admin/usuarios-internos/get/<int:id_usuario>/", UsuarioInternoGetAjaxView.as_view()),
    path("admin/usuarios-internos/create/", UsuarioInternoCreateAjaxView.as_view()),
    path("admin/usuarios-internos/update/<int:id_usuario>/", UsuarioInternoUpdateAjaxView.as_view()),
    path("admin/usuarios-internos/delete/<int:id_usuario>/", UsuarioInternoDeleteAjaxView.as_view()),
    path(
        "admin/usuario-interno/search/",
        UsuarioInternoSearchAjaxView.as_view(),
        name="usuario_interno_search",
    ),
    path("api/generar-pdf-reserva/", views_webapp.generar_pdf_factura, name="generar_pdf_reserva"),
    #############################
    #############################
    #############################
    path("admin/factura/", FacturaView.as_view(), name="factura_admin"),
    path("admin/factura/list/", FacturaListAjaxView.as_view(), name="factura_list"),
    path("admin/factura/get/<int:id_factura>/", FacturaGetAjaxView.as_view(), name="factura_get"),
    path("admin/factura/create/", FacturaCreateAjaxView.as_view(), name="factura_create"),
    path("admin/factura/update/<int:id_factura>/", FacturaUpdateAjaxView.as_view(), name="factura_update"),
    path("admin/factura/delete/<int:id_factura>/", FacturaDeleteAjaxView.as_view(), name="factura_delete"),

    path("admin/factura/search/", FacturaSearchAjaxView.as_view(), name="facturas_search"),

]
