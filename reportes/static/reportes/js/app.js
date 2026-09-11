/*
================================================================================
INTERFAZ SPA - APP 'REPORTES' (ESQUEMA ONE-TRAX)
================================================================================
Vanilla JS, sin frameworks (igual que mychapala/app.js), organizada en
módulos independientes por pestaña: Pozos, Sistemas de Fluido, Intervalos
(con tubería instalada y cierre volumétrico), Productos, Reportes Diarios
(con muestras, matriz de propiedades selectivas e inventario/uso).

Cada módulo consume solo su porción de la API REST (api/pozos/, api/
sistemas-fluido/, api/intervalos/, api/productos/, api/reportes-diarios/,
api/propiedades-catalogo/, api/muestras/, api/inventario-items/,
api/uso-material/) — así se pueden extender o reemplazar por separado sin
tocar el resto (geometría del pozo, equipos, comentarios quedan para más
adelante, según la estrategia del proyecto).
================================================================================
*/

(function () {
  "use strict";

  const API = window.REPORTES_API_BASE || "/reportes/api/";

  // ============================================================================
  // UTILIDADES
  // ============================================================================

  async function apiGet(path) {
    const res = await fetch(API + path);
    return res.json();
  }

  async function apiSend(path, method, body) {
    const res = await fetch(API + path, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    let data;
    try {
      data = await res.json();
    } catch (e) {
      data = { success: false, error: "Respuesta inválida del servidor." };
    }
    return data;
  }

  function fmt(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback ?? "—";
    return value;
  }

  function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    const div = document.createElement("div");
    div.textContent = String(str);
    return div.innerHTML;
  }

  function formDataToObject(form) {
    const fd = new FormData(form);
    const obj = {};
    fd.forEach((value, key) => { obj[key] = value; });
    // Los checkboxes desmarcados no aparecen en FormData: se recorren aparte
    // para que siempre viajen explícitos como booleano (el backend los espera).
    form.querySelectorAll('input[type="checkbox"]').forEach((el) => {
      if (el.name) obj[el.name] = el.checked;
    });
    return obj;
  }

  function toggle(el, show) {
    if (!el) return;
    el.classList.toggle("hidden", !show);
  }

  function showError(elId, message) {
    const el = document.getElementById(elId);
    if (el) el.textContent = message || "";
  }

  // ============================================================================
  // NAVEGACIÓN ENTRE PESTAÑAS
  // ============================================================================

  function initTabs() {
    const buttons = document.querySelectorAll(".tab-btn");
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        buttons.forEach((b) => b.classList.remove("active"));
        document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById("panel-" + btn.dataset.tab).classList.add("active");
      });
    });
  }

  // ============================================================================
  // MÓDULO: POZOS
  // ============================================================================

  const PozosModule = {
    async init() {
      document.getElementById("btn-nuevo-pozo").addEventListener("click", () => {
        toggle(document.getElementById("form-pozo-card"), true);
      });
      document.getElementById("btn-cancelar-pozo").addEventListener("click", () => {
        toggle(document.getElementById("form-pozo-card"), false);
        document.getElementById("form-pozo").reset();
      });
      document.getElementById("form-pozo").addEventListener("submit", async (ev) => {
        ev.preventDefault();
        showError("error-pozo", "");
        const data = formDataToObject(ev.target);
        const resp = await apiSend("pozos/", "POST", data);
        if (!resp.success) {
          showError("error-pozo", resp.error || "No se pudo guardar el pozo.");
          return;
        }
        ev.target.reset();
        toggle(document.getElementById("form-pozo-card"), false);
        await this.cargar();
        await IntervalosModule.cargarPozos();
        await FosasPerdidasModule.cargarPozos();
        await ReportesModule.cargarPozos();
      });
      await this.cargar();
    },

    async cargar() {
      const resp = await apiGet("pozos/");
      const tbody = document.getElementById("tabla-pozos");
      if (!resp.success) {
        tbody.innerHTML = `<tr><td colspan="7">Error al cargar pozos.</td></tr>`;
        return;
      }
      if (resp.pozos.length === 0) {
        tbody.innerHTML = `<tr><td colspan="11">Sin pozos registrados todavía.</td></tr>`;
        return;
      }
      tbody.innerHTML = resp.pozos.map((p) => `
        <tr>
          <td>${escapeHtml(fmt(p.numero_logit))}</td>
          <td>${escapeHtml(p.nombre)}</td>
          <td>${escapeHtml(p.operador)}</td>
          <td>${escapeHtml(fmt(p.ubicacion))}</td>
          <td>${escapeHtml(fmt(p.campo_area))}</td>
          <td>${escapeHtml(fmt(p.nombre_taladro))}</td>
          <td>${escapeHtml(fmt(p.fecha_spud))}</td>
          <td>${escapeHtml(p.unit_set_display)}${p.tiene_reportes ? ' <span class="badge badge-closed" title="Bloqueado: el pozo ya tiene reportes diarios">🔒</span>' : ""}</td>
          <td>${p.es_offshore ? "Sí" + (p.usa_riser ? " (riser)" : "") : "No"}</td>
          <td>${p.total_intervalos}</td>
          <td><button class="btn btn-danger btn-small" data-eliminar-pozo="${p.id}">Eliminar</button></td>
        </tr>
      `).join("");

      tbody.querySelectorAll("[data-eliminar-pozo]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          if (!confirm("¿Eliminar este pozo? Esta acción no se puede deshacer.")) return;
          const resp = await apiSend("pozos/" + btn.dataset.eliminarPozo + "/", "DELETE");
          if (!resp.success) {
            alert(resp.error || "No se pudo eliminar el pozo.");
            return;
          }
          await this.cargar();
          await IntervalosModule.cargarPozos();
          await FosasPerdidasModule.cargarPozos();
          await ReportesModule.cargarPozos();
        });
      });
    },
  };

  // ============================================================================
  // MÓDULO: SISTEMAS DE FLUIDO
  // ============================================================================

  const SistemasModule = {
    lista: [],

    async init() {
      document.getElementById("btn-nuevo-sistema").addEventListener("click", () => {
        toggle(document.getElementById("form-sistema-card"), true);
      });
      document.getElementById("btn-cancelar-sistema").addEventListener("click", () => {
        toggle(document.getElementById("form-sistema-card"), false);
        document.getElementById("form-sistema").reset();
      });
      document.getElementById("form-sistema").addEventListener("submit", async (ev) => {
        ev.preventDefault();
        showError("error-sistema", "");
        const data = formDataToObject(ev.target);
        const resp = await apiSend("sistemas-fluido/", "POST", data);
        if (!resp.success) {
          showError("error-sistema", resp.error || "No se pudo guardar el sistema de fluido.");
          return;
        }
        ev.target.reset();
        toggle(document.getElementById("form-sistema-card"), false);
        await this.cargar();
        await IntervalosModule.poblarSelectSistemas();
      });
      await this.cargar();
    },

    async cargar() {
      const resp = await apiGet("sistemas-fluido/");
      const tbody = document.getElementById("tabla-sistemas");
      if (!resp.success) {
        tbody.innerHTML = `<tr><td colspan="4">Error al cargar sistemas de fluido.</td></tr>`;
        return;
      }
      this.lista = resp.sistemas;
      if (this.lista.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4">Sin sistemas de fluido registrados todavía.</td></tr>`;
        return;
      }
      tbody.innerHTML = this.lista.map((s) => `
        <tr>
          <td>${escapeHtml(s.nombre)}</td>
          <td>${escapeHtml(s.categoria_display)}</td>
          <td>${escapeHtml(fmt(s.descripcion))}</td>
          <td><button class="btn btn-danger btn-small" data-eliminar-sistema="${s.id}">Eliminar</button></td>
        </tr>
      `).join("");

      tbody.querySelectorAll("[data-eliminar-sistema]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          if (!confirm("¿Eliminar este sistema de fluido?")) return;
          const resp = await apiSend("sistemas-fluido/" + btn.dataset.eliminarSistema + "/", "DELETE");
          if (!resp.success) {
            alert(resp.error || "No se pudo eliminar (puede estar en uso por un intervalo).");
            return;
          }
          await this.cargar();
          await IntervalosModule.poblarSelectSistemas();
        });
      });
    },
  };

  // ============================================================================
  // MÓDULO: INTERVALOS (+ TUBERÍA INSTALADA + CIERRE VOLUMÉTRICO)
  // ============================================================================

  const IntervalosModule = {
    pozoActual: null,
    pitsPozoActual: [],

    async init() {
      const selectPozo = document.getElementById("select-pozo-intervalos");
      await this.cargarPozos();
      selectPozo.addEventListener("change", async () => {
        this.pozoActual = selectPozo.value || null;
        toggle(document.getElementById("intervalos-contenido"), !!this.pozoActual);
        if (this.pozoActual) await this.cargarIntervalos();
      });

      document.getElementById("btn-nuevo-intervalo").addEventListener("click", () => {
        toggle(document.getElementById("form-intervalo-card"), true);
      });

      // Top Of Liner / Sidetrack solo es obligatorio (y se muestra) si el tipo
      // es Liner o si se marca "Es Side Track" — igual que en el manual.
      const tipoSelect = document.getElementById("intervalo-tipo-select");
      const sidetrackCheck = document.getElementById("intervalo-sidetrack-check");
      const topeLabel = document.getElementById("intervalo-tope-label");
      const actualizarVisibilidadTope = () => {
        const requiereTope = tipoSelect.value === "liner" || sidetrackCheck.checked;
        toggle(topeLabel, requiereTope);
        topeLabel.querySelector("input").required = requiereTope;
      };
      tipoSelect.addEventListener("change", actualizarVisibilidadTope);
      sidetrackCheck.addEventListener("change", actualizarVisibilidadTope);
      document.getElementById("btn-cancelar-intervalo").addEventListener("click", () => {
        toggle(document.getElementById("form-intervalo-card"), false);
        document.getElementById("form-intervalo").reset();
      });
      document.getElementById("form-intervalo").addEventListener("submit", async (ev) => {
        ev.preventDefault();
        showError("error-intervalo", "");
        const data = formDataToObject(ev.target);
        data.pozo_id = this.pozoActual;
        const resp = await apiSend("intervalos/", "POST", data);
        if (!resp.success) {
          showError("error-intervalo", resp.error || "No se pudo guardar el intervalo.");
          return;
        }
        ev.target.reset();
        toggle(document.getElementById("form-intervalo-card"), false);
        await this.cargarIntervalos();
        await PozosModule.cargar();
      });

      await this.poblarSelectSistemas();
    },

    async cargarPozos() {
      const resp = await apiGet("pozos/");
      const select = document.getElementById("select-pozo-intervalos");
      const valorActual = select.value;
      select.innerHTML = '<option value="">-- Selecciona un pozo --</option>' +
        (resp.success ? resp.pozos : []).map((p) => `<option value="${p.id}">${escapeHtml(p.nombre)}</option>`).join("");
      if (valorActual) select.value = valorActual;
    },

    async poblarSelectSistemas() {
      const resp = await apiGet("sistemas-fluido/");
      const select = document.querySelector('#form-intervalo select[name="sistema_fluido_id"]');
      if (!select) return;
      select.innerHTML = '<option value="">-- Selecciona --</option>' +
        (resp.success ? resp.sistemas : []).map(
          (s) => `<option value="${s.id}">${escapeHtml(s.nombre)} (${escapeHtml(s.categoria_display)})</option>`
        ).join("");
    },

    async cargarIntervalos() {
      const resp = await apiGet("intervalos/?pozo=" + this.pozoActual);
      const contenedor = document.getElementById("lista-intervalos");
      if (!resp.success) {
        contenedor.innerHTML = `<p>Error al cargar intervalos.</p>`;
        return;
      }
      if (resp.intervalos.length === 0) {
        contenedor.innerHTML = `<p>Este pozo todavía no tiene intervalos.</p>`;
        return;
      }
      const respPits = await apiGet("pits/?pozo=" + this.pozoActual);
      this.pitsPozoActual = (respPits.success ? respPits.pits : []).filter((p) => p.es_transaccional);

      contenedor.innerHTML = resp.intervalos.map((i) => this.renderIntervaloCard(i)).join("");
      resp.intervalos.forEach((i) => this.wireIntervaloCard(i));
    },

    opcionesPitsCierre() {
      return '<option value="">-- Ninguna (si Vol. no fluido = 0) --</option>' +
        (this.pitsPozoActual || []).map((p) => `<option value="${p.id}">${escapeHtml(p.descripcion)}</option>`).join("");
    },

    renderIntervaloCard(i) {
      const badge = i.esta_cerrado
        ? `<span class="badge badge-closed">Cerrado</span>`
        : `<span class="badge badge-open">Abierto</span>`;

      const cierreInfo = i.cierre ? `
        <div class="intervalo-meta">
          <strong>Cierre volumétrico:</strong>
          Vol. final ${i.cierre.volumen_final} bbl · Vol. no fluido (Left in Hole) ${i.cierre.perdida_left_in_hole} bbl
          ${i.cierre.fosa_origen_nombre ? ` desde ${escapeHtml(i.cierre.fosa_origen_nombre)}` : ""} ·
          por ${escapeHtml(i.cierre.usuario)}
        </div>
      ` : "";

      const formCierre = !i.esta_cerrado ? `
        <div class="inline-form" data-form-cierre="${i.id}">
          <label>Prof. final (ft)<input type="number" step="0.01" name="profundidad_final" /></label>
          <label>Vol. final (bbl)<input type="number" step="0.01" name="volumen_final" required /></label>
          <label>Vol. no fluido / Left in Hole (bbl)<input type="number" step="0.01" name="volumen_no_fluido" value="0" required /></label>
          <label>Fosa origen (si hay Vol. no fluido)<select name="fosa_origen_id">${this.opcionesPitsCierre()}</select></label>
          <label>Usuario<input type="text" name="usuario" required /></label>
          <button class="btn btn-primary btn-small" data-cerrar-intervalo="${i.id}">Cerrar Intervalo</button>
        </div>
        <p class="hint">Si Vol. no fluido &gt; 0, se descarga automáticamente como pérdida "Left in Hole" desde la fosa indicada, y el balance del último reporte (Not Accounted) debe quedar en 0.00 para poder cerrar.</p>
        <p class="form-error" id="error-cierre-${i.id}"></p>
      ` : "";

      const formTuberia = !i.esta_cerrado ? `
        <div class="inline-form" data-form-tuberia="${i.id}">
          <label>Tipo
            <select name="tipo">
              <option value="revestidor">Revestidor</option>
              <option value="liner">Liner</option>
              <option value="otro">Otro</option>
            </select>
          </label>
          <label>Longitud / Depth (ft)<input type="number" step="0.01" name="longitud" required /></label>
          <label>TVD (ft)<input type="number" step="0.01" name="profundidad_tvd" placeholder="opcional" /></label>
          <label>Casing OD (in)<input type="number" step="0.001" name="diametro_externo" required /></label>
          <label>Casing ID (in)<input type="number" step="0.001" name="diametro_interno" required /></label>
          <button class="btn btn-secondary btn-small" data-agregar-tuberia="${i.id}">+ Agregar Tramo</button>
        </div>
        <p class="form-error" id="error-tuberia-${i.id}"></p>
      ` : "";

      const sidetrackTag = i.es_sidetrack ? ` · <span class="tab-tag">Side Track</span>` : "";

      return `
        <div class="intervalo-card" data-intervalo-id="${i.id}">
          <div class="intervalo-card-header">
            <h4>Intervalo ${i.numero} — ${escapeHtml(i.sistema_fluido_nombre)} (${escapeHtml(i.categoria_sistema_display)})</h4>
            ${badge}
          </div>
          <div class="intervalo-meta">
            ${escapeHtml(i.modo_operativo_display)} · ${escapeHtml(i.tipo_display)}${sidetrackTag}
          </div>
          <div class="intervalo-meta">
            Prof. inicial: ${i.profundidad_inicial} ft · Prof. final: ${fmt(i.profundidad_final)} ft ·
            Diámetro: ${i.diametro} in · Start Volume: ${fmt(i.volumen_inicial)} bbl
            ${i.profundidad_tope_liner_sidetrack !== null ? ` · Top Of Liner/Sidetrack: ${i.profundidad_tope_liner_sidetrack} ft` : ""}
          </div>
          ${cierreInfo}
          <div class="subsection">
            <strong>Tubería instalada (${i.total_tuberias})</strong>
            <table class="mini-table" data-tabla-tuberias="${i.id}">
              <thead><tr><th>Tipo</th><th>Depth (MD)</th><th>TVD</th><th>Casing OD</th><th>Casing ID</th><th></th></tr></thead>
              <tbody><tr><td colspan="6">Cargando…</td></tr></tbody>
            </table>
            ${formTuberia}
          </div>
          <div class="subsection">
            ${formCierre}
          </div>
        </div>
      `;
    },

    async wireIntervaloCard(intervalo) {
      const card = document.querySelector(`.intervalo-card[data-intervalo-id="${intervalo.id}"]`);
      if (!card) return;

      await this.cargarTuberias(intervalo.id);

      const formTuberia = card.querySelector(`[data-form-tuberia="${intervalo.id}"]`);
      if (formTuberia) {
        formTuberia.querySelector("[data-agregar-tuberia]").addEventListener("click", async () => {
          showError("error-tuberia-" + intervalo.id, "");
          const payload = { intervalo_id: intervalo.id };
          formTuberia.querySelectorAll("input, select").forEach((el) => { payload[el.name] = el.value; });
          const resp = await apiSend("tuberias/", "POST", payload);
          if (!resp.success) {
            showError("error-tuberia-" + intervalo.id, resp.error || "No se pudo agregar el tramo.");
            return;
          }
          formTuberia.querySelectorAll("input").forEach((el) => { el.value = ""; });
          await this.cargarTuberias(intervalo.id);
        });
      }

      const formCierre = card.querySelector(`[data-form-cierre="${intervalo.id}"]`);
      if (formCierre) {
        formCierre.querySelector("[data-cerrar-intervalo]").addEventListener("click", async () => {
          showError("error-cierre-" + intervalo.id, "");
          const payload = {};
          formCierre.querySelectorAll("input, select").forEach((el) => { payload[el.name] = el.value; });
          if (!confirm("¿Cerrar este intervalo? Esta acción no se puede deshacer y quedará bloqueado para edición.")) return;
          const resp = await apiSend("intervalos/" + intervalo.id + "/cerrar/", "POST", payload);
          if (!resp.success) {
            showError("error-cierre-" + intervalo.id, resp.error || "No se pudo cerrar el intervalo.");
            return;
          }
          await this.cargarIntervalos();
        });
      }
    },

    async cargarTuberias(intervaloId) {
      const resp = await apiGet("tuberias/?intervalo=" + intervaloId);
      const tabla = document.querySelector(`[data-tabla-tuberias="${intervaloId}"] tbody`);
      if (!tabla) return;
      if (!resp.success || resp.tuberias.length === 0) {
        tabla.innerHTML = `<tr><td colspan="6">Sin tramos registrados.</td></tr>`;
        return;
      }
      tabla.innerHTML = resp.tuberias.map((t) => `
        <tr>
          <td>${escapeHtml(t.tipo_display)}</td>
          <td>${t.longitud} ft</td>
          <td>${fmt(t.profundidad_tvd, "—")}${t.profundidad_tvd !== null ? " ft" : ""}</td>
          <td>${t.diametro_externo} in</td>
          <td>${t.diametro_interno} in</td>
          <td><button class="btn btn-danger btn-small" data-eliminar-tuberia="${t.id}">Eliminar</button></td>
        </tr>
      `).join("");

      tabla.querySelectorAll("[data-eliminar-tuberia]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const resp = await apiSend("tuberias/" + btn.dataset.eliminarTuberia + "/", "DELETE");
          if (!resp.success) {
            alert(resp.error || "No se pudo eliminar el tramo.");
            return;
          }
          await this.cargarTuberias(intervaloId);
        });
      });
    },
  };

  // ============================================================================
  // MÓDULO: FOSAS Y PÉRDIDAS (Pit Setup & Loss Setup — manual resumido, Paso 3)
  // ============================================================================
  // Catálogos maestros por pozo. Todavía no se conectan a ninguna transacción
  // diaria (eso es Volume Accounting, Paso 6, pendiente).

  const FosasPerdidasModule = {
    pozoActual: null,

    async init() {
      const selectPozo = document.getElementById("select-pozo-fosas");
      await this.cargarPozos();
      selectPozo.addEventListener("change", async () => {
        this.pozoActual = selectPozo.value || null;
        toggle(document.getElementById("fosas-perdidas-contenido"), !!this.pozoActual);
        if (this.pozoActual) {
          await this.cargarPits();
          await this.cargarCategoriasPerdida();
        }
      });

      document.getElementById("btn-nuevo-pit").addEventListener("click", () => {
        toggle(document.getElementById("form-pit-card"), true);
      });
      document.getElementById("btn-cancelar-pit").addEventListener("click", () => {
        toggle(document.getElementById("form-pit-card"), false);
        document.getElementById("form-pit").reset();
      });
      document.getElementById("form-pit").addEventListener("submit", async (ev) => {
        ev.preventDefault();
        showError("error-pit", "");
        const data = formDataToObject(ev.target);
        data.pozo_id = this.pozoActual;
        const resp = await apiSend("pits/", "POST", data);
        if (!resp.success) {
          showError("error-pit", resp.error || "No se pudo guardar la fosa.");
          return;
        }
        ev.target.reset();
        toggle(document.getElementById("form-pit-card"), false);
        await this.cargarPits();
      });

      document.getElementById("btn-nueva-categoria-perdida").addEventListener("click", () => {
        toggle(document.getElementById("form-categoria-perdida-card"), true);
      });
      document.getElementById("btn-cancelar-categoria-perdida").addEventListener("click", () => {
        toggle(document.getElementById("form-categoria-perdida-card"), false);
        document.getElementById("form-categoria-perdida").reset();
      });
      document.getElementById("form-categoria-perdida").addEventListener("submit", async (ev) => {
        ev.preventDefault();
        showError("error-categoria-perdida", "");
        const data = formDataToObject(ev.target);
        data.pozo_id = this.pozoActual;
        const resp = await apiSend("categorias-perdida/", "POST", data);
        if (!resp.success) {
          showError("error-categoria-perdida", resp.error || "No se pudo guardar la categoría.");
          return;
        }
        ev.target.reset();
        toggle(document.getElementById("form-categoria-perdida-card"), false);
        await this.cargarCategoriasPerdida();
      });
    },

    async cargarPozos() {
      const resp = await apiGet("pozos/");
      const select = document.getElementById("select-pozo-fosas");
      const valorActual = select.value;
      select.innerHTML = '<option value="">-- Selecciona un pozo --</option>' +
        (resp.success ? resp.pozos : []).map((p) => `<option value="${p.id}">${escapeHtml(p.nombre)}</option>`).join("");
      if (valorActual) select.value = valorActual;
    },

    async cargarPits() {
      const resp = await apiGet("pits/?pozo=" + this.pozoActual);
      const tbody = document.getElementById("tabla-pits");
      if (!resp.success) {
        tbody.innerHTML = `<tr><td colspan="5">Error al cargar fosas.</td></tr>`;
        return;
      }
      if (resp.pits.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5">Este pozo todavía no tiene fosas registradas.</td></tr>`;
        return;
      }
      tbody.innerHTML = resp.pits.map((p) => `
        <tr>
          <td>${escapeHtml(p.descripcion)}</td>
          <td>${escapeHtml(p.tipo_display)}</td>
          <td>${p.capacidad}</td>
          <td>${p.es_transaccional ? "Sí" : "No (no transaccional)"}</td>
          <td><button class="btn btn-danger btn-small" data-eliminar-pit="${p.id}">Eliminar</button></td>
        </tr>
      `).join("");

      tbody.querySelectorAll("[data-eliminar-pit]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          if (!confirm("¿Eliminar esta fosa?")) return;
          const resp = await apiSend("pits/" + btn.dataset.eliminarPit + "/", "DELETE");
          if (!resp.success) {
            alert(resp.error || "No se pudo eliminar la fosa.");
            return;
          }
          await this.cargarPits();
        });
      });
    },

    async cargarCategoriasPerdida() {
      const resp = await apiGet("categorias-perdida/?pozo=" + this.pozoActual);
      const tbody = document.getElementById("tabla-categorias-perdida");
      if (!resp.success) {
        tbody.innerHTML = `<tr><td colspan="5">Error al cargar categorías de pérdida.</td></tr>`;
        return;
      }
      if (resp.categorias.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5">Este pozo todavía no tiene categorías de pérdida registradas.</td></tr>`;
        return;
      }
      tbody.innerHTML = resp.categorias.map((c) => `
        <tr>
          <td>${escapeHtml(c.nombre)}</td>
          <td>${escapeHtml(c.modo_operativo_display)}</td>
          <td>${escapeHtml(c.dominio_display)}</td>
          <td>${escapeHtml(fmt(c.descripcion))}</td>
          <td><button class="btn btn-danger btn-small" data-eliminar-categoria-perdida="${c.id}">Eliminar</button></td>
        </tr>
      `).join("");

      tbody.querySelectorAll("[data-eliminar-categoria-perdida]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          if (!confirm("¿Eliminar esta categoría de pérdida?")) return;
          const resp = await apiSend("categorias-perdida/" + btn.dataset.eliminarCategoriaPerdida + "/", "DELETE");
          if (!resp.success) {
            alert(resp.error || "No se pudo eliminar la categoría.");
            return;
          }
          await this.cargarCategoriasPerdida();
        });
      });
    },
  };

  // ============================================================================
  // MÓDULO: PRODUCTOS
  // ============================================================================

  const ProductosModule = {
    async init() {
      document.getElementById("btn-nuevo-producto").addEventListener("click", () => {
        toggle(document.getElementById("form-producto-card"), true);
      });
      document.getElementById("btn-cancelar-producto").addEventListener("click", () => {
        toggle(document.getElementById("form-producto-card"), false);
        document.getElementById("form-producto").reset();
      });
      document.getElementById("form-producto").addEventListener("submit", async (ev) => {
        ev.preventDefault();
        showError("error-producto", "");
        const data = formDataToObject(ev.target);
        const resp = await apiSend("productos/", "POST", data);
        if (!resp.success) {
          showError("error-producto", resp.error || "No se pudo guardar el producto.");
          return;
        }
        ev.target.reset();
        toggle(document.getElementById("form-producto-card"), false);
        await this.cargar();
        await ReportesModule.poblarSelectProductos();
      });
      await this.cargar();
    },

    async cargar() {
      const resp = await apiGet("productos/");
      const tbody = document.getElementById("tabla-productos");
      if (!resp.success) {
        tbody.innerHTML = `<tr><td colspan="6">Error al cargar productos.</td></tr>`;
        return;
      }
      if (resp.productos.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6">Sin productos registrados todavía.</td></tr>`;
        return;
      }
      tbody.innerHTML = resp.productos.map((p) => `
        <tr>
          <td>${escapeHtml(p.codigo)}</td>
          <td>${escapeHtml(p.nombre)}</td>
          <td>${escapeHtml(p.presentacion)}</td>
          <td>$${p.precio_unitario}</td>
          <td>${p.gravedad_especifica}</td>
          <td><button class="btn btn-danger btn-small" data-eliminar-producto="${p.id}">Eliminar</button></td>
        </tr>
      `).join("");

      tbody.querySelectorAll("[data-eliminar-producto]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          if (!confirm("¿Eliminar este producto?")) return;
          const resp = await apiSend("productos/" + btn.dataset.eliminarProducto + "/", "DELETE");
          if (!resp.success) {
            alert(resp.error || "No se pudo eliminar el producto.");
            return;
          }
          await this.cargar();
          await ReportesModule.poblarSelectProductos();
        });
      });
    },
  };

  // ============================================================================
  // MÓDULO: EQUIPOS (catálogo)
  // ============================================================================

  const EquiposModule = {
    lista: [],

    async init() {
      document.getElementById("btn-nuevo-equipo").addEventListener("click", () => {
        toggle(document.getElementById("form-equipo-card"), true);
      });
      document.getElementById("btn-cancelar-equipo").addEventListener("click", () => {
        toggle(document.getElementById("form-equipo-card"), false);
        document.getElementById("form-equipo").reset();
      });
      document.getElementById("form-equipo").addEventListener("submit", async (ev) => {
        ev.preventDefault();
        showError("error-equipo", "");
        const data = formDataToObject(ev.target);
        const resp = await apiSend("equipos/", "POST", data);
        if (!resp.success) {
          showError("error-equipo", resp.error || "No se pudo guardar el equipo.");
          return;
        }
        ev.target.reset();
        toggle(document.getElementById("form-equipo-card"), false);
        await this.cargar();
        await ReportesModule.poblarSelectEquipos();
      });
      await this.cargar();
    },

    async cargar() {
      const resp = await apiGet("equipos/");
      const tbody = document.getElementById("tabla-equipos");
      if (!resp.success) {
        tbody.innerHTML = `<tr><td colspan="4">Error al cargar equipos.</td></tr>`;
        return;
      }
      this.lista = resp.equipos;
      if (this.lista.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4">Sin equipos registrados todavía.</td></tr>`;
        return;
      }
      tbody.innerHTML = this.lista.map((e) => `
        <tr>
          <td>${escapeHtml(e.codigo)}</td>
          <td>${escapeHtml(e.nombre)}</td>
          <td>$${e.costo_diario}</td>
          <td><button class="btn btn-danger btn-small" data-eliminar-equipo="${e.id}">Eliminar</button></td>
        </tr>
      `).join("");

      tbody.querySelectorAll("[data-eliminar-equipo]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          if (!confirm("¿Eliminar este equipo?")) return;
          const resp = await apiSend("equipos/" + btn.dataset.eliminarEquipo + "/", "DELETE");
          if (!resp.success) {
            alert(resp.error || "No se pudo eliminar el equipo.");
            return;
          }
          await this.cargar();
          await ReportesModule.poblarSelectEquipos();
        });
      });
    },
  };

  // ============================================================================
  // MÓDULO: REPORTES DIARIOS (+ MUESTRAS + MATRIZ DE PROPIEDADES + INVENTARIO/USO)
  // ============================================================================

  const ReportesModule = {
    pozoActual: null,
    intervaloActual: null,
    productos: [],
    equipos: [],
    tuberiasIntervaloActual: [],

    async init() {
      const selectPozo = document.getElementById("select-pozo-reportes");
      const selectIntervalo = document.getElementById("select-intervalo-reportes");

      await this.cargarPozos();
      await this.poblarSelectProductos();
      await this.poblarSelectEquipos();

      selectPozo.addEventListener("change", async () => {
        this.pozoActual = selectPozo.value || null;
        selectIntervalo.disabled = !this.pozoActual;
        selectIntervalo.innerHTML = '<option value="">-- Selecciona un intervalo --</option>';
        toggle(document.getElementById("reportes-contenido"), false);
        if (this.pozoActual) {
          const resp = await apiGet("intervalos/?pozo=" + this.pozoActual);
          if (resp.success) {
            selectIntervalo.innerHTML += resp.intervalos.map(
              (i) => `<option value="${i.id}">Intervalo ${i.numero} (${i.estado_display})</option>`
            ).join("");
          }
        }
      });

      selectIntervalo.addEventListener("change", async () => {
        this.intervaloActual = selectIntervalo.value || null;
        toggle(document.getElementById("reportes-contenido"), !!this.intervaloActual);
        document.getElementById("detalle-reporte").innerHTML = "";
        if (this.intervaloActual) await this.cargarReportes();
      });

      document.getElementById("btn-nuevo-reporte").addEventListener("click", () => {
        toggle(document.getElementById("form-reporte-card"), true);
      });
      document.getElementById("btn-cancelar-reporte").addEventListener("click", () => {
        toggle(document.getElementById("form-reporte-card"), false);
        document.getElementById("form-reporte").reset();
      });
      document.getElementById("form-reporte").addEventListener("submit", async (ev) => {
        ev.preventDefault();
        showError("error-reporte", "");
        const data = formDataToObject(ev.target);
        data.intervalo_id = this.intervaloActual;
        const resp = await apiSend("reportes-diarios/", "POST", data);
        if (!resp.success) {
          showError("error-reporte", resp.error || "No se pudo guardar el reporte.");
          return;
        }
        ev.target.reset();
        toggle(document.getElementById("form-reporte-card"), false);
        await this.cargarReportes();
      });
    },

    async cargarPozos() {
      const resp = await apiGet("pozos/");
      const select = document.getElementById("select-pozo-reportes");
      select.innerHTML = '<option value="">-- Selecciona un pozo --</option>' +
        (resp.success ? resp.pozos : []).map((p) => `<option value="${p.id}">${escapeHtml(p.nombre)}</option>`).join("");
    },

    async poblarSelectProductos() {
      const resp = await apiGet("productos/");
      this.productos = resp.success ? resp.productos : [];
    },

    async poblarSelectEquipos() {
      const resp = await apiGet("equipos/");
      this.equipos = resp.success ? resp.equipos : [];
    },

    async cargarReportes() {
      const resp = await apiGet("reportes-diarios/?intervalo=" + this.intervaloActual);
      const contenedor = document.getElementById("lista-reportes");
      if (!resp.success) {
        contenedor.innerHTML = `<p>Error al cargar reportes.</p>`;
        return;
      }
      if (resp.reportes.length === 0) {
        contenedor.innerHTML = `<p>Este intervalo todavía no tiene reportes diarios.</p>`;
        return;
      }
      contenedor.innerHTML = `
        <table>
          <thead><tr><th>N° Reporte</th><th>Fecha</th><th>Actividad</th><th>Peso Lodo</th><th>Muestras</th><th></th></tr></thead>
          <tbody>
            ${resp.reportes.map((r) => `
              <tr>
                <td>${r.numero_reporte}</td>
                <td>${escapeHtml(r.fecha)}</td>
                <td>${escapeHtml(fmt(r.actividad))}</td>
                <td>${fmt(r.peso_lodo)}</td>
                <td>${r.total_muestras}</td>
                <td><button class="btn btn-secondary btn-small" data-ver-reporte="${r.id}">Ver detalle</button></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;
      contenedor.querySelectorAll("[data-ver-reporte]").forEach((btn) => {
        btn.addEventListener("click", () => this.abrirDetalleReporte(btn.dataset.verReporte));
      });
    },

    async abrirDetalleReporte(reporteId) {
      const respReporte = await apiGet("reportes-diarios/" + reporteId + "/");
      if (!respReporte.success) return;
      const reporte = respReporte.reporte;

      const respIntervalo = await apiGet("intervalos/" + this.intervaloActual + "/");
      const intervalo = respIntervalo.success ? respIntervalo.intervalo : null;
      const categoria = intervalo ? intervalo.categoria_sistema : "";

      const respPropiedades = await apiGet("propiedades-catalogo/?categoria=" + categoria);
      const propiedades = respPropiedades.success ? respPropiedades.propiedades : [];

      const respPits = await apiGet("pits/?pozo=" + this.pozoActual);
      const pits = (respPits.success ? respPits.pits : []).filter((p) => p.es_transaccional);

      const modoOperativo = intervalo ? intervalo.modo_operativo : "";
      const respCategorias = await apiGet("categorias-perdida/?pozo=" + this.pozoActual + "&modo_operativo=" + modoOperativo);
      const categoriasPerdida = respCategorias.success ? respCategorias.categorias : [];

      const respTuberias = await apiGet("tuberias/?intervalo=" + this.intervaloActual);
      this.tuberiasIntervaloActual = respTuberias.success ? respTuberias.tuberias : [];

      const opcionesPits = (permitirVacio = true) =>
        (permitirVacio ? '<option value="">-- Selecciona --</option>' : "") +
        pits.map((p) => `<option value="${p.id}">${escapeHtml(p.descripcion)}</option>`).join("");

      const opcionesCategoriasPerdida = () =>
        '<option value="">-- Selecciona --</option>' +
        categoriasPerdida.map((c) => `<option value="${c.id}">${escapeHtml(c.nombre)} (${escapeHtml(c.dominio_display)})</option>`).join("");

      const contenedor = document.getElementById("detalle-reporte");
      contenedor.innerHTML = `
        <div class="card">
          <h3>Reporte ${reporte.numero_reporte} — ${escapeHtml(reporte.fecha)}</h3>
          <div class="intervalo-meta">
            Default Interval: Intervalo ${reporte.intervalo_numero} · Default Fluid System: ${escapeHtml(reporte.sistema_fluido_nombre)}
          </div>

          <div class="subsection">
            <strong>Distribución de Tiempo <span class="hint">(Daily -&gt; General — Time Distribution)</span></strong>
            <table class="mini-table" id="tabla-distribucion-tiempo">
              <thead><tr><th>Actividad</th><th>Horas</th><th></th></tr></thead>
              <tbody><tr><td colspan="3">Cargando…</td></tr></tbody>
            </table>
            <div class="inline-form">
              <label style="flex:1 1 220px">Actividad<input type="text" id="dt-actividad" placeholder='Ej. "Rotary Drilling"' /></label>
              <label>Horas<input type="number" step="0.25" min="0.01" max="24" id="dt-horas" /></label>
              <button class="btn btn-secondary btn-small" id="btn-agregar-distribucion-tiempo">+ Agregar</button>
            </div>
            <div class="intervalo-meta" id="dt-resumen">
              Total: ${fmt(reporte.horas_totales_distribucion)} hrs de 24.00
              <strong class="${reporte.tiempo_cuadrado ? "tag-ok" : "tag-alerta"}">${reporte.tiempo_cuadrado ? "✓ Cuadrado" : "⚠ No cuadra"}</strong>
            </div>
            <p class="form-error" id="error-distribucion-tiempo"></p>
          </div>

          <div class="subsection">
            <strong>Geometría de Hoyo y Sarta <span class="hint">(Daily -&gt; Geometry)</span></strong>
            <div class="geometria-real-layout">
              <div class="geometria-real-datos">
                <div class="inline-form" id="geometria-hoyo-form">
                  <label>Bit Depth (ft)<input type="number" step="0.01" id="geo-bit-depth" value="${reporte.bit_depth ?? ""}" /></label>
                  <label>Bit Size (in)<input type="number" step="0.001" id="geo-bit-size" value="${reporte.bit_size ?? ""}" /></label>
                  <label>% Washout<input type="number" step="0.01" id="geo-washout" value="${reporte.porcentaje_washout ?? "0"}" /></label>
                  <button class="btn btn-secondary btn-small" id="btn-guardar-geometria-hoyo">Guardar</button>
                </div>
                <div class="intervalo-meta" id="geo-hole-size-info">
                  Hole Size: ${fmt(reporte.hole_size, "—")}${reporte.hole_size !== null ? " in" : ""} ·
                  Diámetro de confinamiento vigente: ${reporte.diametro_confinamiento} in
                </div>
                <p class="form-error" id="error-geometria-hoyo"></p>

                <strong>Sarta de Perforación (Drill String Geometry)</strong>
                <table class="mini-table" id="tabla-sarta">
                  <thead><tr><th>Tipo</th><th>Longitud (ft)</th><th>Pipe OD</th><th>Pipe ID</th><th>Cap. interna (bbl)</th><th>Vol. anular (bbl)</th><th></th></tr></thead>
                  <tbody><tr><td colspan="7">Cargando…</td></tr></tbody>
                </table>
                <div class="inline-form">
                  <label>Tipo
                    <select id="sarta-tipo">
                      <option value="drill_pipe">Drill Pipe (principal, longitud automática)</option>
                      <option value="heavy_weight">Heavy Weight</option>
                      <option value="drill_collar">Drill Collar</option>
                      <option value="sub">Sub</option>
                    </select>
                  </label>
                  <label id="sarta-longitud-label">Longitud (ft)<input type="number" step="0.01" id="sarta-longitud" /></label>
                  <label>Pipe OD (in)<input type="number" step="0.001" id="sarta-od" /></label>
                  <label>Pipe ID (in)<input type="number" step="0.001" id="sarta-id" /></label>
                  <button class="btn btn-secondary btn-small" id="btn-agregar-tramo-sarta">+ Agregar Tramo</button>
                </div>
                <p class="hint">El tramo "Drill Pipe" principal no lleva longitud manual: se calcula como Bit Depth − suma de los demás tramos (BHA). Como máximo un tramo puede ser el principal. El orden de la tabla (arriba = superficie) es el que usa el esquema para apilar los tramos.</p>
                <p class="form-error" id="error-sarta"></p>
              </div>

              <div class="card geometria-real-dibujo">
                <h4>Esquema (dinámico, según los datos ingresados)</h4>
                <div id="geo-svg-real-wrap"><p class="hint">Ingresa Bit Depth y al menos un tramo de sarta para ver el esquema.</p></div>
                <p class="hint geometria-real-leyenda">
                  <span class="leyenda-swatch" style="background:#e7d4b5;border-color:#b8985f"></span> Hoyo abierto
                  <span class="leyenda-swatch" style="background:#9ca3af;border-color:#4b5563"></span> Revestidor
                  <span class="leyenda-swatch" style="background:#374151;border-color:#111827"></span> Sarta
                </p>
              </div>
            </div>
          </div>

          <div class="subsection">
            <strong>Contabilidad Volumétrica <span class="hint">(Daily -&gt; Volume Accounting)</span></strong>

            <div class="inline-form" id="volume-accounting-form">
              <label>Vol. Debajo de la Mecha (bbl)<input type="number" step="0.01" id="va-volumen-debajo-mecha" value="${reporte.volumen_debajo_mecha ?? "0"}" /></label>
              <label>Volume Not Fluids (bbl)<input type="number" step="0.01" id="va-volumen-no-fluido" value="${reporte.volumen_no_fluido ?? "0"}" /></label>
              <button class="btn btn-secondary btn-small" id="btn-guardar-volume-accounting">Guardar</button>
            </div>
            <p class="form-error" id="error-volume-accounting"></p>
            <div class="intervalo-meta" id="va-resumen-hoyo">
              Vol. Anular: ${fmt(reporte.volumen_anular_total)} bbl · Vol. Sarta: ${fmt(reporte.volumen_sarta_total)} bbl ·
              <strong>Total Hole Volume: ${fmt(reporte.volumen_total_hoyo)} bbl</strong> · Fluid Volume: ${fmt(reporte.volumen_fluido)} bbl
            </div>
            <div class="intervalo-meta" id="va-reconciliacion">
              Volumen Teórico (fosas): ${fmt(reporte.volumen_teorico_fosas)} bbl · Volumen Medido (fosas): ${fmt(reporte.volumen_medido_fosas)} bbl ·
              <strong class="${reporte.balance_cuadrado ? "tag-ok" : "tag-alerta"}">Not Accounted: ${fmt(reporte.volumen_no_contabilizado)} bbl${reporte.balance_cuadrado ? " ✓" : ""}</strong>
            </div>

            <strong>Lecturas de Fosa (Volumen Medido)</strong>
            <table class="mini-table" id="tabla-lecturas-fosa">
              <thead><tr><th>Fosa</th><th>Volumen medido (bbl)</th><th></th></tr></thead>
              <tbody><tr><td colspan="3">Cargando…</td></tr></tbody>
            </table>
            <div class="inline-form">
              <label>Fosa<select id="lectura-fosa-select">${opcionesPits()}</select></label>
              <label>Volumen medido (bbl)<input type="number" step="0.0001" id="lectura-volumen" /></label>
              <button class="btn btn-secondary btn-small" id="btn-guardar-lectura-fosa">Guardar Lectura</button>
            </div>
            <p class="form-error" id="error-lectura-fosa"></p>

            <strong>Transacciones de Fosa</strong>
            <table class="mini-table" id="tabla-transacciones-fosa">
              <thead><tr><th>Tipo</th><th>Origen</th><th>Destino</th><th>Producto / Categoría</th><th>Volumen (bbl)</th><th>Hora</th><th></th></tr></thead>
              <tbody><tr><td colspan="7">Cargando…</td></tr></tbody>
            </table>
            <div class="inline-form">
              <label>Tipo
                <select id="trx-tipo">
                  <option value="add_chemicals">Add Chemicals</option>
                  <option value="loss">Loss</option>
                  <option value="transfer">Transfer</option>
                </select>
              </label>
              <label id="trx-origen-label">Fosa origen<select id="trx-fosa-origen">${opcionesPits()}</select></label>
              <label id="trx-destino-label">Fosa destino<select id="trx-fosa-destino">${opcionesPits()}</select></label>
              <label id="trx-producto-label">Producto<select id="trx-producto">${this.opcionesProductos()}</select></label>
              <label id="trx-cantidad-label">Cant. usada (empaques)<input type="number" step="0.01" id="trx-cantidad" /></label>
              <label id="trx-dilucion-label"><input type="checkbox" id="trx-dilucion" /> Is Dilution</label>
              <label id="trx-categoria-label">Categoría de pérdida<select id="trx-categoria">${opcionesCategoriasPerdida()}</select></label>
              <label id="trx-volumen-label">Volumen (bbl)<input type="number" step="0.0001" id="trx-volumen" /></label>
              <button class="btn btn-secondary btn-small" id="btn-agregar-transaccion">+ Registrar Transacción</button>
            </div>
            <p class="hint">En Add Chemicals el volumen se calcula automáticamente a partir del producto (cantidad × gravedad específica) — no se ingresa a mano.</p>
            <p class="form-error" id="error-transaccion"></p>
          </div>

          <div class="subsection">
            <strong>Muestras de fluido</strong>
            <div id="muestras-lista"></div>
            <div class="inline-form">
              <label>Identificador<input type="text" id="nueva-muestra-id" placeholder='Ej. "TK 2 20:00"' /></label>
              <button class="btn btn-secondary btn-small" id="btn-agregar-muestra">+ Agregar Muestra</button>
            </div>
            <p class="form-error" id="error-muestra"></p>
          </div>

          <div class="subsection">
            <strong>Inventario del día</strong>
            <div id="inventario-lista"></div>
            <div class="inline-form">
              <label>Producto
                <select id="inv-producto">${this.opcionesProductos()}</select>
              </label>
              <label>Cant. inicial<input type="number" step="0.01" id="inv-cantidad-inicial" /></label>
              <label>Entrada<input type="number" step="0.01" id="inv-cantidad-entrada" value="0" /></label>
              <button class="btn btn-secondary btn-small" id="btn-agregar-inventario">+ Registrar</button>
            </div>
            <p class="form-error" id="error-inventario"></p>
          </div>

          <div class="subsection">
            <strong>Uso de material</strong>
            <div id="uso-lista"></div>
            <div class="inline-form">
              <label>Producto
                <select id="uso-producto">${this.opcionesProductos()}</select>
              </label>
              <label>Cantidad usada<input type="number" step="0.01" id="uso-cantidad" /></label>
              <button class="btn btn-secondary btn-small" id="btn-agregar-uso">+ Registrar Uso</button>
            </div>
            <p class="form-error" id="error-uso"></p>
          </div>

          <div class="subsection">
            <strong>Uso de equipos</strong>
            <div id="uso-equipo-lista"></div>
            <div class="inline-form">
              <label>Equipo
                <select id="uso-equipo-select">${this.opcionesEquipos()}</select>
              </label>
              <label>Horas usadas<input type="number" step="0.01" id="uso-equipo-horas" /></label>
              <button class="btn btn-secondary btn-small" id="btn-agregar-uso-equipo">+ Registrar Uso de Equipo</button>
            </div>
            <p class="form-error" id="error-uso-equipo"></p>
          </div>

          <div class="subsection">
            <strong>Comentarios</strong>
            <div id="comentarios-lista"></div>
            <div class="inline-form">
              <label>Autor<input type="text" id="comentario-autor" /></label>
              <label style="flex:1 1 260px">Comentario<input type="text" id="comentario-texto" /></label>
              <button class="btn btn-secondary btn-small" id="btn-agregar-comentario">+ Agregar Comentario</button>
            </div>
            <p class="form-error" id="error-comentario"></p>
          </div>
        </div>
      `;

      document.getElementById("btn-agregar-muestra").addEventListener("click", async () => {
        showError("error-muestra", "");
        const identificador = document.getElementById("nueva-muestra-id").value.trim();
        if (!identificador) {
          showError("error-muestra", "Escribe un identificador para la muestra.");
          return;
        }
        const resp = await apiSend("muestras/", "POST", { reporte_id: reporteId, identificador });
        if (!resp.success) {
          showError("error-muestra", resp.error || "No se pudo agregar la muestra.");
          return;
        }
        document.getElementById("nueva-muestra-id").value = "";
        await this.cargarMuestras(reporteId, propiedades);
      });

      document.getElementById("btn-agregar-inventario").addEventListener("click", async () => {
        showError("error-inventario", "");
        const payload = {
          reporte_id: reporteId,
          producto_id: document.getElementById("inv-producto").value,
          cantidad_inicial: document.getElementById("inv-cantidad-inicial").value,
          cantidad_entrada: document.getElementById("inv-cantidad-entrada").value || "0",
        };
        const resp = await apiSend("inventario-items/", "POST", payload);
        if (!resp.success) {
          showError("error-inventario", resp.error || "No se pudo registrar el inventario.");
          return;
        }
        document.getElementById("inv-cantidad-inicial").value = "";
        document.getElementById("inv-cantidad-entrada").value = "0";
        await this.cargarInventario(reporteId);
      });

      document.getElementById("btn-agregar-uso").addEventListener("click", async () => {
        showError("error-uso", "");
        const payload = {
          reporte_id: reporteId,
          producto_id: document.getElementById("uso-producto").value,
          cantidad_usada: document.getElementById("uso-cantidad").value,
        };
        const resp = await apiSend("uso-material/", "POST", payload);
        if (!resp.success) {
          showError("error-uso", resp.error || "No se pudo registrar el uso.");
          return;
        }
        document.getElementById("uso-cantidad").value = "";
        await this.cargarInventario(reporteId);
        await this.cargarUso(reporteId);
      });

      document.getElementById("btn-agregar-uso-equipo").addEventListener("click", async () => {
        showError("error-uso-equipo", "");
        const payload = {
          reporte_id: reporteId,
          equipo_id: document.getElementById("uso-equipo-select").value,
          horas_usadas: document.getElementById("uso-equipo-horas").value,
        };
        const resp = await apiSend("uso-equipo/", "POST", payload);
        if (!resp.success) {
          showError("error-uso-equipo", resp.error || "No se pudo registrar el uso del equipo.");
          return;
        }
        document.getElementById("uso-equipo-horas").value = "";
        await this.cargarUsoEquipo(reporteId);
      });

      document.getElementById("btn-agregar-comentario").addEventListener("click", async () => {
        showError("error-comentario", "");
        const texto = document.getElementById("comentario-texto").value.trim();
        if (!texto) {
          showError("error-comentario", "Escribe un comentario.");
          return;
        }
        const payload = {
          reporte_id: reporteId,
          texto,
          autor: document.getElementById("comentario-autor").value.trim(),
        };
        const resp = await apiSend("comentarios/", "POST", payload);
        if (!resp.success) {
          showError("error-comentario", resp.error || "No se pudo agregar el comentario.");
          return;
        }
        document.getElementById("comentario-texto").value = "";
        await this.cargarComentarios(reporteId);
      });

      // --- Geometría de Hoyo y Sarta (Paso 5) ---
      const sartaTipoSelect = document.getElementById("sarta-tipo");
      const sartaLongitudLabel = document.getElementById("sarta-longitud-label");
      const actualizarVisibilidadLongitudSarta = () => {
        const esPrincipal = sartaTipoSelect.value === "drill_pipe";
        toggle(sartaLongitudLabel, !esPrincipal);
        sartaLongitudLabel.querySelector("input").required = !esPrincipal;
      };
      sartaTipoSelect.addEventListener("change", actualizarVisibilidadLongitudSarta);
      actualizarVisibilidadLongitudSarta();

      document.getElementById("btn-guardar-geometria-hoyo").addEventListener("click", async () => {
        showError("error-geometria-hoyo", "");
        const payload = {
          bit_depth: document.getElementById("geo-bit-depth").value,
          bit_size: document.getElementById("geo-bit-size").value,
          porcentaje_washout: document.getElementById("geo-washout").value || "0",
        };
        const resp = await apiSend("reportes-diarios/" + reporteId + "/", "PUT", payload);
        if (!resp.success) {
          showError("error-geometria-hoyo", resp.error || "No se pudo guardar la geometría del hoyo.");
          return;
        }
        const info = document.getElementById("geo-hole-size-info");
        info.textContent =
          "Hole Size: " + fmt(resp.reporte.hole_size, "—") + (resp.reporte.hole_size !== null ? " in" : "") +
          " · Diámetro de confinamiento vigente: " + resp.reporte.diametro_confinamiento + " in";
        await this.cargarSarta(reporteId);
        await this.actualizarResumenVolumen(reporteId);
      });

      document.getElementById("btn-agregar-tramo-sarta").addEventListener("click", async () => {
        showError("error-sarta", "");
        const esPrincipal = sartaTipoSelect.value === "drill_pipe";
        const payload = {
          reporte_id: reporteId,
          tipo: sartaTipoSelect.value,
          es_principal: esPrincipal,
          diametro_externo: document.getElementById("sarta-od").value,
          diametro_interno: document.getElementById("sarta-id").value,
        };
        if (!esPrincipal) payload.longitud = document.getElementById("sarta-longitud").value;
        const resp = await apiSend("tramos-sarta/", "POST", payload);
        if (!resp.success) {
          showError("error-sarta", resp.error || "No se pudo agregar el tramo de sarta.");
          return;
        }
        document.getElementById("sarta-longitud").value = "";
        document.getElementById("sarta-od").value = "";
        document.getElementById("sarta-id").value = "";
        await this.cargarSarta(reporteId);
        await this.actualizarResumenVolumen(reporteId);
      });

      // --- Contabilidad Volumétrica (Paso 6) ---
      document.getElementById("btn-guardar-volume-accounting").addEventListener("click", async () => {
        showError("error-volume-accounting", "");
        const payload = {
          volumen_debajo_mecha: document.getElementById("va-volumen-debajo-mecha").value || "0",
          volumen_no_fluido: document.getElementById("va-volumen-no-fluido").value || "0",
        };
        const resp = await apiSend("reportes-diarios/" + reporteId + "/", "PUT", payload);
        if (!resp.success) {
          showError("error-volume-accounting", resp.error || "No se pudo guardar la contabilidad volumétrica.");
          return;
        }
        this.pintarResumenVolumen(resp.reporte);
      });

      const trxTipoSelect = document.getElementById("trx-tipo");
      const actualizarVisibilidadTransaccion = () => {
        const tipo = trxTipoSelect.value;
        toggle(document.getElementById("trx-origen-label"), tipo === "loss" || tipo === "transfer");
        toggle(document.getElementById("trx-destino-label"), tipo === "add_chemicals" || tipo === "transfer");
        toggle(document.getElementById("trx-producto-label"), tipo === "add_chemicals");
        toggle(document.getElementById("trx-cantidad-label"), tipo === "add_chemicals");
        toggle(document.getElementById("trx-dilucion-label"), tipo === "add_chemicals");
        toggle(document.getElementById("trx-categoria-label"), tipo === "loss");
        toggle(document.getElementById("trx-volumen-label"), tipo === "loss" || tipo === "transfer");
      };
      trxTipoSelect.addEventListener("change", actualizarVisibilidadTransaccion);
      actualizarVisibilidadTransaccion();

      document.getElementById("btn-agregar-transaccion").addEventListener("click", async () => {
        showError("error-transaccion", "");
        const tipo = trxTipoSelect.value;
        const payload = { reporte_id: reporteId, tipo };
        if (tipo === "add_chemicals") {
          payload.fosa_destino_id = document.getElementById("trx-fosa-destino").value;
          payload.producto_id = document.getElementById("trx-producto").value;
          payload.cantidad_usada = document.getElementById("trx-cantidad").value;
          payload.es_dilucion = document.getElementById("trx-dilucion").checked;
        } else if (tipo === "loss") {
          payload.fosa_origen_id = document.getElementById("trx-fosa-origen").value;
          payload.categoria_perdida_id = document.getElementById("trx-categoria").value;
          payload.volumen = document.getElementById("trx-volumen").value;
        } else {
          payload.fosa_origen_id = document.getElementById("trx-fosa-origen").value;
          payload.fosa_destino_id = document.getElementById("trx-fosa-destino").value;
          payload.volumen = document.getElementById("trx-volumen").value;
        }
        const resp = await apiSend("transacciones-fosa/", "POST", payload);
        if (!resp.success) {
          showError("error-transaccion", resp.error || "No se pudo registrar la transacción.");
          return;
        }
        document.getElementById("trx-cantidad").value = "";
        document.getElementById("trx-volumen").value = "";
        document.getElementById("trx-dilucion").checked = false;
        await this.cargarTransaccionesFosa(reporteId);
        await this.actualizarResumenVolumen(reporteId);
      });

      document.getElementById("btn-guardar-lectura-fosa").addEventListener("click", async () => {
        showError("error-lectura-fosa", "");
        const fosaId = document.getElementById("lectura-fosa-select").value;
        if (!fosaId) {
          showError("error-lectura-fosa", "Selecciona una fosa.");
          return;
        }
        const payload = {
          reporte_id: reporteId,
          fosa_id: fosaId,
          volumen_medido: document.getElementById("lectura-volumen").value,
        };
        const resp = await apiSend("lecturas-fosa/", "POST", payload);
        if (!resp.success) {
          showError("error-lectura-fosa", resp.error || "No se pudo guardar la lectura.");
          return;
        }
        document.getElementById("lectura-volumen").value = "";
        await this.cargarLecturasFosa(reporteId);
        await this.actualizarResumenVolumen(reporteId);
      });

      // --- Distribución de Tiempo (Paso 4) ---
      document.getElementById("btn-agregar-distribucion-tiempo").addEventListener("click", async () => {
        showError("error-distribucion-tiempo", "");
        const actividad = document.getElementById("dt-actividad").value.trim();
        if (!actividad) {
          showError("error-distribucion-tiempo", "Escribe una actividad.");
          return;
        }
        const payload = {
          reporte_id: reporteId,
          actividad,
          horas: document.getElementById("dt-horas").value,
        };
        const resp = await apiSend("distribucion-tiempo/", "POST", payload);
        if (!resp.success) {
          showError("error-distribucion-tiempo", resp.error || "No se pudo agregar la actividad.");
          return;
        }
        document.getElementById("dt-actividad").value = "";
        document.getElementById("dt-horas").value = "";
        await this.cargarDistribucionTiempo(reporteId);
      });

      await this.cargarSarta(reporteId);
      await this.cargarLecturasFosa(reporteId);
      await this.cargarTransaccionesFosa(reporteId);
      await this.cargarDistribucionTiempo(reporteId);
      await this.cargarMuestras(reporteId, propiedades);
      await this.cargarInventario(reporteId);
      await this.cargarUso(reporteId);
      await this.cargarUsoEquipo(reporteId);
      await this.cargarComentarios(reporteId);
    },

    async cargarSarta(reporteId) {
      const resp = await apiGet("tramos-sarta/?reporte=" + reporteId);
      const tabla = document.getElementById("tabla-sarta");
      const tramos = resp.success ? resp.tramos : [];

      if (tabla) {
        const tbody = tabla.querySelector("tbody");
        if (tramos.length === 0) {
          tbody.innerHTML = `<tr><td colspan="7">Sin tramos de sarta registrados.</td></tr>`;
        } else {
          tbody.innerHTML = tramos.map((t) => `
            <tr>
              <td>${escapeHtml(t.tipo_display)}${t.es_principal ? ' <span class="tab-tag">auto</span>' : ""}</td>
              <td>${fmt(t.longitud)}</td>
              <td>${t.diametro_externo}</td>
              <td>${t.diametro_interno}</td>
              <td>${fmt(t.capacidad_interna_bbl)}</td>
              <td>${fmt(t.volumen_anular_bbl)}</td>
              <td><button class="btn btn-danger btn-small" data-eliminar-tramo-sarta="${t.id}">Eliminar</button></td>
            </tr>
          `).join("");

          tbody.querySelectorAll("[data-eliminar-tramo-sarta]").forEach((btn) => {
            btn.addEventListener("click", async () => {
              const resp = await apiSend("tramos-sarta/" + btn.dataset.eliminarTramoSarta + "/", "DELETE");
              if (!resp.success) {
                alert(resp.error || "No se pudo eliminar el tramo.");
                return;
              }
              await this.cargarSarta(reporteId);
            });
          });
        }
      }

      const respReporte = await apiGet("reportes-diarios/" + reporteId + "/");
      if (respReporte.success) {
        this.renderEsquemaSarta(respReporte.reporte, this.tuberiasIntervaloActual, tramos);
      }
    },

    renderEsquemaSarta(reporte, tuberias, tramos) {
      const wrap = document.getElementById("geo-svg-real-wrap");
      if (!wrap) return;

      const bitDepth = parseFloat(reporte.bit_depth);
      if (!bitDepth || bitDepth <= 0) {
        wrap.innerHTML = `<p class="hint">Ingresa Bit Depth y al menos un tramo de sarta para ver el esquema.</p>`;
        return;
      }

      // Mismo criterio simplificado que ReporteDiario.diametro_confinamiento en
      // el backend: se usa una sola tubería de referencia (la más profunda), no
      // un apilado de múltiples revestidores.
      let ultimaTuberia = null;
      (tuberias || []).forEach((t) => {
        if (!ultimaTuberia || parseFloat(t.longitud) > parseFloat(ultimaTuberia.longitud)) ultimaTuberia = t;
      });
      const profZapata = ultimaTuberia ? Math.min(parseFloat(ultimaTuberia.longitud), bitDepth) : 0;
      const holeSize = parseFloat(reporte.hole_size);
      const odHoyo = !isNaN(holeSize) ? holeSize : (ultimaTuberia ? parseFloat(ultimaTuberia.diametro_interno) : 0);
      const odRevestidor = ultimaTuberia ? parseFloat(ultimaTuberia.diametro_externo) : 0;
      const idRevestidor = ultimaTuberia ? parseFloat(ultimaTuberia.diametro_interno) : 0;

      // Tramos de sarta apilados de superficie hacia abajo, en el orden de la
      // tabla (columna "orden"), acumulando longitud.
      let acumulado = 0;
      const segmentos = [...(tramos || [])]
        .sort((a, b) => a.orden - b.orden)
        .map((t) => {
          const longitud = parseFloat(t.longitud) || 0;
          const desde = acumulado;
          acumulado += longitud;
          return { desde, hasta: acumulado, od: parseFloat(t.diametro_externo) || 0, id: parseFloat(t.diametro_interno) || 0 };
        });

      const width = 260, height = 480, margenSuperior = 16, margenInferior = 16;
      const altoDibujo = height - margenSuperior - margenInferior;
      const centroX = width / 2;

      const maxDiametro = Math.max(odHoyo, odRevestidor, ...segmentos.map((s) => s.od), 1);
      const anchoMaxPx = width * 0.42;
      const escalaDiametro = anchoMaxPx / (maxDiametro / 2);
      const profTotalSegura = Math.max(bitDepth, 1);
      const escalaProfundidad = altoDibujo / profTotalSegura;

      const y = (depth) => margenSuperior + Math.min(Math.max(depth, 0), profTotalSegura) * escalaProfundidad;

      const rect = (diametro, desde, hasta, fill, stroke) => {
        if (!diametro || diametro <= 0) return "";
        const anchoPx = diametro * escalaDiametro;
        const x = centroX - anchoPx / 2;
        const yTop = y(desde), yBottom = y(hasta);
        const alto = Math.max(yBottom - yTop, 0);
        return `<rect x="${x.toFixed(1)}" y="${yTop.toFixed(1)}" width="${anchoPx.toFixed(1)}" height="${alto.toFixed(1)}" fill="${fill}" stroke="${stroke}" stroke-width="1" />`;
      };

      let svg = "";
      // Hoyo abierto: de la zapata (o de superficie si no hay tubería) al Bit Depth.
      svg += rect(odHoyo, profZapata, bitDepth, "#e7d4b5", "#b8985f");
      // Revestidor: de superficie a la zapata.
      if (ultimaTuberia) {
        svg += rect(odRevestidor, 0, profZapata, "#9ca3af", "#4b5563");
        svg += rect(idRevestidor, 0, profZapata, "#f3f4f6", "#9ca3af");
      }
      // Sarta: cada tramo apilado, OD sólido con ID hueco.
      segmentos.forEach((s) => {
        svg += rect(s.od, s.desde, s.hasta, "#374151", "#111827");
        svg += rect(s.id, s.desde, s.hasta, "#ffffff", "#6b7280");
      });

      if (ultimaTuberia) {
        svg += `<line x1="6" y1="${y(profZapata).toFixed(1)}" x2="${width - 6}" y2="${y(profZapata).toFixed(1)}" stroke="#dc2626" stroke-width="1" stroke-dasharray="4 3" />`;
        svg += `<text x="${width - 6}" y="${(y(profZapata) - 3).toFixed(1)}" font-size="9" text-anchor="end" fill="#dc2626">Zapata @ ${profZapata.toFixed(0)} ft</text>`;
      }
      svg += `<text x="${width - 6}" y="${(y(bitDepth) - 3).toFixed(1)}" font-size="9" text-anchor="end" fill="#374151">Bit Depth @ ${bitDepth.toFixed(0)} ft</text>`;
      svg += `<line x1="${centroX}" y1="${margenSuperior}" x2="${centroX}" y2="${y(bitDepth)}" stroke="#d1d5db" stroke-width="1" stroke-dasharray="2 2" />`;

      wrap.innerHTML = `<svg viewBox="0 0 ${width} ${height}" width="100%" height="${height}" xmlns="http://www.w3.org/2000/svg">${svg}</svg>`;
    },

    pintarResumenVolumen(reporte) {
      const resumen = document.getElementById("va-resumen-hoyo");
      if (resumen) {
        resumen.innerHTML =
          `Vol. Anular: ${fmt(reporte.volumen_anular_total)} bbl · Vol. Sarta: ${fmt(reporte.volumen_sarta_total)} bbl · ` +
          `<strong>Total Hole Volume: ${fmt(reporte.volumen_total_hoyo)} bbl</strong> · Fluid Volume: ${fmt(reporte.volumen_fluido)} bbl`;
      }
      const reconciliacion = document.getElementById("va-reconciliacion");
      if (reconciliacion) {
        reconciliacion.innerHTML =
          `Volumen Teórico (fosas): ${fmt(reporte.volumen_teorico_fosas)} bbl · Volumen Medido (fosas): ${fmt(reporte.volumen_medido_fosas)} bbl · ` +
          `<strong class="${reporte.balance_cuadrado ? "tag-ok" : "tag-alerta"}">Not Accounted: ${fmt(reporte.volumen_no_contabilizado)} bbl${reporte.balance_cuadrado ? " ✓" : ""}</strong>`;
      }
    },

    async actualizarResumenVolumen(reporteId) {
      const resp = await apiGet("reportes-diarios/" + reporteId + "/");
      if (resp.success) this.pintarResumenVolumen(resp.reporte);
    },

    async cargarLecturasFosa(reporteId) {
      const resp = await apiGet("lecturas-fosa/?reporte=" + reporteId);
      const tabla = document.getElementById("tabla-lecturas-fosa");
      if (!tabla) return;
      const tbody = tabla.querySelector("tbody");
      if (!resp.success || resp.lecturas.length === 0) {
        tbody.innerHTML = `<tr><td colspan="3">Sin lecturas registradas todavía.</td></tr>`;
        return;
      }
      tbody.innerHTML = resp.lecturas.map((l) => `
        <tr>
          <td>${escapeHtml(l.fosa_nombre)}</td>
          <td>${l.volumen_medido}</td>
          <td><button class="btn btn-danger btn-small" data-eliminar-lectura="${l.id}">Eliminar</button></td>
        </tr>
      `).join("");
      tbody.querySelectorAll("[data-eliminar-lectura]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const resp = await apiSend("lecturas-fosa/" + btn.dataset.eliminarLectura + "/", "DELETE");
          if (!resp.success) {
            alert(resp.error || "No se pudo eliminar la lectura.");
            return;
          }
          await this.cargarLecturasFosa(reporteId);
          await this.actualizarResumenVolumen(reporteId);
        });
      });
    },

    async cargarTransaccionesFosa(reporteId) {
      const resp = await apiGet("transacciones-fosa/?reporte=" + reporteId);
      const tabla = document.getElementById("tabla-transacciones-fosa");
      if (!tabla) return;
      const tbody = tabla.querySelector("tbody");
      if (!resp.success || resp.transacciones.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7">Sin transacciones registradas todavía.</td></tr>`;
        return;
      }
      tbody.innerHTML = resp.transacciones.map((t) => `
        <tr>
          <td>${escapeHtml(t.tipo_display)}${t.es_dilucion ? ' <span class="tab-tag">dilución</span>' : ""}</td>
          <td>${t.fosa_origen_nombre ? escapeHtml(t.fosa_origen_nombre) : "—"}</td>
          <td>${t.fosa_destino_nombre ? escapeHtml(t.fosa_destino_nombre) : "—"}</td>
          <td>${t.producto_nombre ? escapeHtml(t.producto_nombre) : (t.categoria_perdida_nombre ? escapeHtml(t.categoria_perdida_nombre) : "—")}</td>
          <td>${t.volumen}</td>
          <td>${escapeHtml(fmt(t.hora_registro))}</td>
          <td><button class="btn btn-danger btn-small" data-eliminar-transaccion="${t.id}">Eliminar</button></td>
        </tr>
      `).join("");
      tbody.querySelectorAll("[data-eliminar-transaccion]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const resp = await apiSend("transacciones-fosa/" + btn.dataset.eliminarTransaccion + "/", "DELETE");
          if (!resp.success) {
            alert(resp.error || "No se pudo eliminar la transacción.");
            return;
          }
          await this.cargarTransaccionesFosa(reporteId);
          await this.actualizarResumenVolumen(reporteId);
        });
      });
    },

    async cargarDistribucionTiempo(reporteId) {
      const resp = await apiGet("distribucion-tiempo/?reporte=" + reporteId);
      const tabla = document.getElementById("tabla-distribucion-tiempo");
      if (!tabla) return;
      const tbody = tabla.querySelector("tbody");
      if (!resp.success || resp.distribucion.length === 0) {
        tbody.innerHTML = `<tr><td colspan="3">Sin actividades registradas todavía.</td></tr>`;
      } else {
        tbody.innerHTML = resp.distribucion.map((d) => `
          <tr>
            <td>${escapeHtml(d.actividad)}</td>
            <td>${d.horas}</td>
            <td><button class="btn btn-danger btn-small" data-eliminar-distribucion="${d.id}">Eliminar</button></td>
          </tr>
        `).join("");
        tbody.querySelectorAll("[data-eliminar-distribucion]").forEach((btn) => {
          btn.addEventListener("click", async () => {
            const resp = await apiSend("distribucion-tiempo/" + btn.dataset.eliminarDistribucion + "/", "DELETE");
            if (!resp.success) {
              alert(resp.error || "No se pudo eliminar la actividad.");
              return;
            }
            await this.cargarDistribucionTiempo(reporteId);
          });
        });
      }

      const respReporte = await apiGet("reportes-diarios/" + reporteId + "/");
      const resumen = document.getElementById("dt-resumen");
      if (respReporte.success && resumen) {
        const r = respReporte.reporte;
        resumen.innerHTML =
          `Total: ${fmt(r.horas_totales_distribucion)} hrs de 24.00 ` +
          `<strong class="${r.tiempo_cuadrado ? "tag-ok" : "tag-alerta"}">${r.tiempo_cuadrado ? "✓ Cuadrado" : "⚠ No cuadra"}</strong>`;
      }
    },

    opcionesProductos() {
      return '<option value="">-- Selecciona --</option>' +
        this.productos.map((p) => `<option value="${p.id}">${escapeHtml(p.codigo)} - ${escapeHtml(p.nombre)}</option>`).join("");
    },

    opcionesEquipos() {
      return '<option value="">-- Selecciona --</option>' +
        this.equipos.map((e) => `<option value="${e.id}">${escapeHtml(e.codigo)} - ${escapeHtml(e.nombre)}</option>`).join("");
    },

    async cargarMuestras(reporteId, propiedades) {
      const resp = await apiGet("muestras/?reporte=" + reporteId);
      const contenedor = document.getElementById("muestras-lista");
      if (!contenedor) return;
      if (!resp.success || resp.muestras.length === 0) {
        contenedor.innerHTML = `<p>Sin muestras registradas todavía.</p>`;
        return;
      }
      contenedor.innerHTML = resp.muestras.map((m) => this.renderMuestra(m, propiedades)).join("");
      resp.muestras.forEach((m) => this.wireMuestra(m, propiedades));
    },

    renderMuestra(muestra, propiedades) {
      const valoresPorPropiedad = {};
      (muestra.valores || []).forEach((v) => { valoresPorPropiedad[v.propiedad_id] = v.valor; });

      const campos = propiedades.map((prop) => `
        <label>
          ${escapeHtml(prop.nombre)} ${prop.unidad ? `(${escapeHtml(prop.unidad)})` : ""}
          <input type="number" step="0.0001" data-propiedad-id="${prop.id}"
                 value="${valoresPorPropiedad[prop.id] !== undefined ? valoresPorPropiedad[prop.id] : ""}" />
        </label>
      `).join("");

      return `
        <div class="muestra-block" data-muestra-id="${muestra.id}">
          <div class="intervalo-card-header">
            <strong>${escapeHtml(muestra.identificador)}</strong>
            <button class="btn btn-danger btn-small" data-eliminar-muestra="${muestra.id}">Eliminar</button>
          </div>
          <div class="matriz-propiedades" data-matriz="${muestra.id}">
            ${campos || "<p>No hay propiedades habilitadas para el sistema de fluido de este intervalo.</p>"}
          </div>
          ${propiedades.length ? `<button class="btn btn-primary btn-small" style="margin-top:8px" data-guardar-matriz="${muestra.id}">Guardar Valores</button>` : ""}
          <p class="form-error" id="error-matriz-${muestra.id}"></p>
        </div>
      `;
    },

    wireMuestra(muestra, propiedades) {
      const bloque = document.querySelector(`.muestra-block[data-muestra-id="${muestra.id}"]`);
      if (!bloque) return;

      const btnEliminar = bloque.querySelector("[data-eliminar-muestra]");
      btnEliminar.addEventListener("click", async () => {
        if (!confirm("¿Eliminar esta muestra y sus valores?")) return;
        const resp = await apiSend("muestras/" + muestra.id + "/", "DELETE");
        if (!resp.success) {
          alert(resp.error || "No se pudo eliminar la muestra.");
          return;
        }
        await this.cargarMuestras(muestra.reporte_id, propiedades);
      });

      const btnGuardar = bloque.querySelector("[data-guardar-matriz]");
      if (btnGuardar) {
        btnGuardar.addEventListener("click", async () => {
          showError("error-matriz-" + muestra.id, "");
          const valores = [];
          bloque.querySelectorAll("[data-propiedad-id]").forEach((input) => {
            if (input.value !== "") {
              valores.push({ propiedad_id: input.dataset.propiedadId, valor: input.value });
            }
          });
          const resp = await apiSend("muestras/" + muestra.id + "/valores/", "POST", { valores });
          if (!resp.success) {
            showError("error-matriz-" + muestra.id, resp.error || "No se pudieron guardar los valores.");
            return;
          }
          btnGuardar.textContent = "Guardado ✓";
          setTimeout(() => { btnGuardar.textContent = "Guardar Valores"; }, 1500);
        });
      }
    },

    async cargarInventario(reporteId) {
      const resp = await apiGet("inventario-items/?reporte=" + reporteId);
      const contenedor = document.getElementById("inventario-lista");
      if (!contenedor) return;
      if (!resp.success || resp.items.length === 0) {
        contenedor.innerHTML = `<p>Sin inventario registrado todavía.</p>`;
        return;
      }
      contenedor.innerHTML = `
        <table class="mini-table">
          <thead><tr><th>Producto</th><th>Inicial</th><th>Entrada</th><th>Final</th><th>Libraje Final</th></tr></thead>
          <tbody>
            ${resp.items.map((i) => `
              <tr>
                <td>${escapeHtml(i.producto_nombre)}</td>
                <td>${i.cantidad_inicial}</td>
                <td>${i.cantidad_entrada}</td>
                <td>${i.cantidad_final}</td>
                <td>${i.libraje_final}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;
    },

    async cargarUso(reporteId) {
      const resp = await apiGet("uso-material/?reporte=" + reporteId);
      const contenedor = document.getElementById("uso-lista");
      if (!contenedor) return;
      if (!resp.success || resp.usos.length === 0) {
        contenedor.innerHTML = `<p>Sin usos registrados todavía.</p>`;
        return;
      }
      contenedor.innerHTML = `
        <table class="mini-table">
          <thead><tr><th>Producto</th><th>Cant. usada</th><th>Libraje</th><th>Subtotal $</th><th>Hora</th><th></th></tr></thead>
          <tbody>
            ${resp.usos.map((u) => `
              <tr>
                <td>${escapeHtml(u.producto_nombre)}</td>
                <td>${u.cantidad_usada}</td>
                <td>${u.libraje_usado}</td>
                <td>$${u.subtotal_costo}</td>
                <td>${escapeHtml(fmt(u.hora_registro))}</td>
                <td><button class="btn btn-danger btn-small" data-eliminar-uso="${u.id}">Eliminar</button></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;
      contenedor.querySelectorAll("[data-eliminar-uso]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const resp = await apiSend("uso-material/" + btn.dataset.eliminarUso + "/", "DELETE");
          if (!resp.success) {
            alert(resp.error || "No se pudo eliminar el uso.");
            return;
          }
          await this.cargarInventario(reporteId);
          await this.cargarUso(reporteId);
        });
      });
    },

    async cargarUsoEquipo(reporteId) {
      const resp = await apiGet("uso-equipo/?reporte=" + reporteId);
      const contenedor = document.getElementById("uso-equipo-lista");
      if (!contenedor) return;
      if (!resp.success || resp.usos.length === 0) {
        contenedor.innerHTML = `<p>Sin uso de equipos registrado todavía.</p>`;
        return;
      }
      contenedor.innerHTML = `
        <table class="mini-table">
          <thead><tr><th>Equipo</th><th>Horas</th><th>Costo diario</th><th>Subtotal $</th><th></th></tr></thead>
          <tbody>
            ${resp.usos.map((u) => `
              <tr>
                <td>${escapeHtml(u.equipo_nombre)}</td>
                <td>${u.horas_usadas}</td>
                <td>$${u.costo_diario}</td>
                <td>$${u.subtotal_costo}</td>
                <td><button class="btn btn-danger btn-small" data-eliminar-uso-equipo="${u.id}">Eliminar</button></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;
      contenedor.querySelectorAll("[data-eliminar-uso-equipo]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const resp = await apiSend("uso-equipo/" + btn.dataset.eliminarUsoEquipo + "/", "DELETE");
          if (!resp.success) {
            alert(resp.error || "No se pudo eliminar el uso del equipo.");
            return;
          }
          await this.cargarUsoEquipo(reporteId);
        });
      });
    },

    async cargarComentarios(reporteId) {
      const resp = await apiGet("comentarios/?reporte=" + reporteId);
      const contenedor = document.getElementById("comentarios-lista");
      if (!contenedor) return;
      if (!resp.success || resp.comentarios.length === 0) {
        contenedor.innerHTML = `<p>Sin comentarios todavía.</p>`;
        return;
      }
      contenedor.innerHTML = resp.comentarios.map((c) => `
        <div class="comentario-item">
          <div class="comentario-meta">
            <strong>${escapeHtml(fmt(c.autor, "Sin autor"))}</strong>
            <span>${escapeHtml(fmt(c.fecha_hora))}</span>
            <button class="btn btn-danger btn-small" data-eliminar-comentario="${c.id}">Eliminar</button>
          </div>
          <p>${escapeHtml(c.texto)}</p>
        </div>
      `).join("");
      contenedor.querySelectorAll("[data-eliminar-comentario]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const resp = await apiSend("comentarios/" + btn.dataset.eliminarComentario + "/", "DELETE");
          if (!resp.success) {
            alert(resp.error || "No se pudo eliminar el comentario.");
            return;
          }
          await this.cargarComentarios(reporteId);
        });
      });
    },
  };

  // ============================================================================
  // ARRANQUE
  // ============================================================================

  document.addEventListener("DOMContentLoaded", async () => {
    initTabs();
    await PozosModule.init();
    await SistemasModule.init();
    await IntervalosModule.init();
    await FosasPerdidasModule.init();
    await ProductosModule.init();
    await EquiposModule.init();
    await ReportesModule.init();
  });
})();
