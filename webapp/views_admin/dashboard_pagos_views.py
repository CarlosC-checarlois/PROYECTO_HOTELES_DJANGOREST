from django.http import JsonResponse
from django.views import View
from servicios.rest.gestion.PagoGestionRest import PagoGestionRest
from datetime import datetime


class DashboardPagosAjaxView(View):
    def get(self, request, uid):

        try:
            api = PagoGestionRest()
            pagos = api.obtener_pagos() or []
        except Exception:
            return JsonResponse({"error": "No se pudo conectar con el servicio de pagos"}, status=500)

        # =============================
        # 1. FILTRAR SOLO USUARIO
        # =============================
        pagos_usuario = [
            p for p in pagos
            if str(p.get("IdUnicoUsuario", "")) == str(uid)
        ]

        # =============================
        # 2. LIMPIAR DATOS
        # =============================
        data = []

        for p in pagos_usuario:

            try:
                cuenta = str(p.get("CuentaOrigenPago") or "").strip()
            except:
                cuenta = ""

            try:
                monto = float(p.get("MontoTotalPago") or 0)
            except:
                monto = 0.0

            try:
                estado = "Pagado" if bool(p.get("EstadoPago")) else "Pendiente"
            except:
                estado = "Pendiente"

            try:
                fecha_raw = p.get("FechaModificacionPago") or ""
            except:
                fecha_raw = ""

            fecha = None
            if fecha_raw:
                try:
                    fecha = datetime.fromisoformat(str(fecha_raw)).strftime("%Y-%m-%d")
                except:
                    fecha = None

            data.append({
                "cuenta": cuenta if cuenta else "Desconocida",
                "monto": monto,
                "fecha": fecha,
                "estado": estado
            })

        # =============================
        # 3. METRICAS DASHBOARD
        # =============================
        total_pagado = sum(
            p["monto"]
            for p in data
            if p.get("estado") == "Pagado"
        )

        cantidad = len(data)

        # =============================
        # 4. CUENTAS ÚNICAS
        # =============================
        cuentas = sorted({
            p.get("cuenta", "Desconocida")
            for p in data
            if p.get("cuenta")
        })

        # =============================
        # 5. SCATTER (GROUP BY)
        # =============================
        scatter_map = {}

        for p in data:
            cuenta = p.get("cuenta")
            monto = p.get("monto", 0)

            if not cuenta:
                cuenta = "Desconocida"

            scatter_map[cuenta] = scatter_map.get(cuenta, 0) + monto

        scatter_data = [
            {"x": cuenta, "y": round(total, 2)}
            for cuenta, total in scatter_map.items()
        ]

        # =============================
        # 6. LINEA TEMPORAL
        # =============================
        serie = []

        for p in data:
            if p.get("fecha"):
                serie.append({
                    "fecha": p["fecha"],
                    "monto": p["monto"]
                })

        serie = sorted(serie, key=lambda x: x["fecha"])

        # =============================
        # 7. TREEMAP
        # =============================
        treemap = []

        contador = {}

        for p in data:
            cuenta = p.get("cuenta") or "Desconocida"
            contador[cuenta] = contador.get(cuenta, 0) + 1

            treemap.append({
                "cuenta": cuenta,
                "pago": f"Transacción {contador[cuenta]}",
                "value": round(p.get("monto", 0), 2)
            })

        # =============================
        # 8. RESPUESTA FINAL SEGURA
        # =============================
        return JsonResponse({
            "dashboard": {
                "total_pagado": round(total_pagado, 2),
                "cantidad": cantidad
            },
            "cuentas": cuentas,
            "scatter": scatter_data,
            "line": serie,
            "treemap": treemap
        })
