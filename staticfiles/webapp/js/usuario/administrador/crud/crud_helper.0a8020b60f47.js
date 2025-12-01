/* ============================================================
   🔔 TOAST MODERNO ANIMADO
   ============================================================ */
function crudNotify(type, msg) {
    const container = document.getElementById("crud-toast-container");
    if (!container) {
        console.error("No existe #crud-toast-container en el DOM");
        return;
    }

    const toast = document.createElement("div");
    toast.classList.add("crud-toast", `crud-toast-${type}`);

    const icons = {
        success: "✅",
        error: "❌",
        warning: "⚠️",
        info: "ℹ️",
    };

    toast.innerHTML = `<span class="crud-toast-icon">${icons[type] || "ℹ️"}</span>
                       <span class="crud-toast-text">${msg}</span>`;

    container.appendChild(toast);

    // Auto-cerrar luego de 3.5s
    setTimeout(() => closeToast(toast), 3500);

    // Click para cerrar de inmediato
    toast.onclick = () => closeToast(toast);
}

function closeToast(toast) {
    toast.style.animation = "toastFadeOut 0.4s forwards";
    setTimeout(() => toast.remove(), 400);
}

/* ============================================================
   📄 Cargar tabla CON PAGINACIÓN (GLOBAL)
   ============================================================ */
function crudLoadTable(
    url,
    rowBuilder,
    tableSelector = "#tablaListado",
    paginationSelector = null,
    currentPage = 1
) {

    $.ajax({
        url,
        method: "GET",
        success: function (resp) {

            const tbody = document.querySelector(`${tableSelector} tbody`);

            if (!tbody) {
                console.error(`No se encontró tbody para ${tableSelector}`);
                return;
            }

            tbody.innerHTML = "";

            // ------------------------------
            // Cargar filas
            // ------------------------------
            (resp.data || []).forEach(item => {
                tbody.insertAdjacentHTML("beforeend", rowBuilder(item));
            });

            // ------------------------------
            // PAGINACIÓN UNIVERSAL
            // ------------------------------
            if (paginationSelector && resp.total_pages) {

                const cont = document.querySelector(paginationSelector);
                if (!cont) return;

                // Recarga universal
                const reload = typeof window.__crudReload === "function"
                    ? "window.__crudReload"
                    : "console.error('No se definió window.__crudReload')";

                let html = "";

                // Botón ANTERIOR
                html += `
                    <button class="btn btn-secondary btn-sm"
                            onclick="${reload}(${resp.page - 1})"
                            ${resp.page <= 1 ? "disabled" : ""}>
                        ◀ Anterior
                    </button>
                `;

                // Página actual
                html += `
                    <span class="fw-bold">
                        Página ${resp.page} de ${resp.total_pages}
                    </span>
                `;

                // Botón SIGUIENTE
                html += `
                    <button class="btn btn-secondary btn-sm"
                            onclick="${reload}(${resp.page + 1})"
                            ${resp.page >= resp.total_pages ? "disabled" : ""}>
                        Siguiente ▶
                    </button>
                `;

                cont.innerHTML = html;
            }
        },
        error: function () {
            crudNotify("error", "No se pudo cargar la información.");
        }
    });
}

/* ============================================================
   🔢 Generar nuevo ID
   ============================================================ */
function crudGenerateNewId(url, inputSelector, key = "Id") {
    $.get(url, function (resp) {
        const lista = resp.data || [];
        const nuevoId = lista.length === 0
            ? 1
            : Math.max.apply(null, lista.map(r => r[key])) + 1;

        $(inputSelector).val(nuevoId);
    });
}

/* ============================================================
   🟩 Crear registro
   ============================================================ */
function crudCreate(url, data, onSuccess) {
    $.post(url, data)
        .done(resp => {
            crudNotify("success", resp.message || "Creado correctamente.");
            if (onSuccess) onSuccess(resp);
        })
        .fail(xhr => {
            crudNotify("error", xhr.responseJSON?.message || "Error al crear.");
        });
}

/* ============================================================
   🟦 Actualizar registro
   ============================================================ */
function crudUpdate(url, data, onSuccess) {
    $.post(url, data)
        .done(resp => {
            crudNotify("success", resp.message || "Actualizado correctamente.");
            if (onSuccess) onSuccess(resp);
        })
        .fail(xhr => {
            crudNotify("error", xhr.responseJSON?.message || "Error al actualizar.");
        });
}

/* ============================================================
   🟥 Eliminar registro (solo hace la llamada)
   ============================================================ */
function crudDelete(url, onSuccess) {
    $.post(url)
        .done(resp => {
            crudNotify("success", resp.message || "Eliminado correctamente.");
            if (onSuccess) onSuccess(resp);
        })
        .fail(xhr => {
            crudNotify("error", xhr.responseJSON?.message || "Error al eliminar.");
        });
}

/* ============================================================
   ✅ Modal de confirmación reutilizable (sin alert/confirm)
   ============================================================ */
function crudConfirm(message) {
    return new Promise(function (resolve) {

        // Si ya hay uno abierto, lo quitamos
        const old = document.querySelector(".crud-confirm-backdrop");
        if (old) old.remove();

        const backdrop = document.createElement("div");
        backdrop.className = "crud-confirm-backdrop";

        const modal = document.createElement("div");
        modal.className = "crud-confirm-modal";

        modal.innerHTML = `
            <div class="crud-confirm-icon">⚠️</div>
            <div class="crud-confirm-message">${message}</div>
            <div class="crud-confirm-actions">
                <button type="button" class="btn btn-secondary crud-confirm-cancel">
                    Cancelar
                </button>
                <button type="button" class="btn btn-danger crud-confirm-ok">
                    Sí, eliminar
                </button>
            </div>
        `;

        backdrop.appendChild(modal);
        document.body.appendChild(backdrop);

        function close(result) {
            backdrop.classList.add("crud-confirm-hide");
            setTimeout(() => backdrop.remove(), 200);
            resolve(result);
        }

        backdrop.addEventListener("click", function (e) {
            if (e.target === backdrop) {
                close(false);
            }
        });

        modal.querySelector(".crud-confirm-cancel")
            .addEventListener("click", () => close(false));

        modal.querySelector(".crud-confirm-ok")
            .addEventListener("click", () => close(true));
    });
}
