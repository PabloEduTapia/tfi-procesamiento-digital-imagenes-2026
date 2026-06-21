/**
 * app.js — Interacción del frontend de Visión Cromática.
 *
 * Responsabilidad de este archivo: manejar el formulario, enviar la imagen
 * al endpoint /procesar de Flask y mostrar los resultados.
 * No hace ningún procesamiento de imagen: eso vive en el servidor (core/).
 */

const form = document.getElementById("form-procesar");
const inputImagen = document.getElementById("input-imagen");
const zonaCarga = document.getElementById("zona-carga");
const zonaCargaContenido = document.getElementById("zona-carga__contenido");
const inputSeveridad = document.getElementById("input-severidad");
const valorSeveridad = document.getElementById("valor-severidad");
const botonProcesar = document.getElementById("boton-procesar");
const mensajeError = document.getElementById("mensaje-error");
const panelResultados = document.getElementById("panel-resultados");
const panelVacio = document.getElementById("panel-vacio");

const imgOriginal = document.getElementById("img-original");
const imgSimulada = document.getElementById("img-simulada");
const imgCorregida = document.getElementById("img-corregida");

// ── Selector de vista: grilla vs comparación con slider ──────────────────────
const botonVistaGrilla = document.getElementById("boton-vista-grilla");
const botonVistaComparar = document.getElementById("boton-vista-comparar");
const vistaGrilla = document.getElementById("vista-grilla");
const vistaComparar = document.getElementById("vista-comparar");

botonVistaGrilla.addEventListener("click", () => cambiarVista("grilla"));
botonVistaComparar.addEventListener("click", () => cambiarVista("comparar"));

function cambiarVista(nombre) {
  const esGrilla = nombre === "grilla";
  botonVistaGrilla.classList.toggle("activo", esGrilla);
  botonVistaComparar.classList.toggle("activo", !esGrilla);
  botonVistaGrilla.setAttribute("aria-selected", String(esGrilla));
  botonVistaComparar.setAttribute("aria-selected", String(!esGrilla));
  vistaGrilla.classList.toggle("oculta", !esGrilla);
  vistaComparar.classList.toggle("activa", !esGrilla);

  if (!esGrilla) {
    // el contenedor recién obtiene su tamaño real al dejar de estar oculto
    requestAnimationFrame(() => moverDivisor(0.5));
  }
}

window.addEventListener("resize", () => {
  if (vistaComparar.classList.contains("activa")) {
    const linea = comparadorLinea.style.left || "50%";
    moverDivisor(parseFloat(linea) / 100);
  }
});

// ── Lightbox: ampliar cualquier imagen de la grilla con un clic ─────────────
const lightbox = document.getElementById("lightbox");
const lightboxImg = document.getElementById("lightbox-img");
const lightboxCerrar = document.getElementById("lightbox-cerrar");

document.querySelectorAll(".resultado__marco").forEach((marco) => {
  marco.addEventListener("click", () => {
    const img = marco.querySelector("img");
    if (img && img.src) abrirLightbox(img.src, img.alt);
  });
});

function abrirLightbox(src, alt) {
  lightboxImg.src = src;
  lightboxImg.alt = alt;
  lightbox.hidden = false;
}

function cerrarLightbox() {
  lightbox.hidden = true;
  lightboxImg.src = "";
}

lightboxCerrar.addEventListener("click", cerrarLightbox);
lightbox.addEventListener("click", (e) => {
  if (e.target === lightbox) cerrarLightbox();
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !lightbox.hidden) cerrarLightbox();
});

// ── Comparador deslizable ────────────────────────────────────────────────────
const mapaImagenes = {}; // se llena con las 3 imágenes una vez procesadas: { original, simulada, corregida }

const selectIzq = document.getElementById("select-comparar-izq");
const selectDer = document.getElementById("select-comparar-der");
const comparadorImgIzq = document.getElementById("comparador-img-izq");
const comparadorImgDer = document.getElementById("comparador-img-der");
const comparadorFrente = document.getElementById("comparador-frente");
const comparadorLinea = document.getElementById("comparador-linea");
const comparador = document.getElementById("comparador");
const etiquetaIzq = document.getElementById("etiqueta-izq");
const etiquetaDer = document.getElementById("etiqueta-der");

const NOMBRES_VISIBLES = { original: "Original", simulada: "Simulada", corregida: "Corregida" };

function actualizarComparador() {
  const claveIzq = selectIzq.value;
  const claveDer = selectDer.value;
  comparadorImgIzq.src = mapaImagenes[claveIzq] || "";
  comparadorImgDer.src = mapaImagenes[claveDer] || "";
  etiquetaIzq.textContent = NOMBRES_VISIBLES[claveIzq];
  etiquetaDer.textContent = NOMBRES_VISIBLES[claveDer];
}

selectIzq.addEventListener("change", actualizarComparador);
selectDer.addEventListener("change", actualizarComparador);

function moverDivisor(posicionXRelativa) {
  const porcentaje = Math.min(100, Math.max(0, posicionXRelativa * 100));
  const anchoReal = comparador.getBoundingClientRect().width;
  comparador.style.setProperty("--ancho-comparador", `${anchoReal}px`);
  comparadorFrente.style.width = `${porcentaje}%`;
  comparadorLinea.style.left = `${porcentaje}%`;
}

function calcularPosicionRelativa(clienteX) {
  const rect = comparador.getBoundingClientRect();
  return (clienteX - rect.left) / rect.width;
}

let arrastrando = false;

comparadorLinea.addEventListener("pointerdown", (e) => {
  arrastrando = true;
  comparadorLinea.setPointerCapture(e.pointerId);
});

comparadorLinea.addEventListener("pointermove", (e) => {
  if (!arrastrando) return;
  moverDivisor(calcularPosicionRelativa(e.clientX));
});

comparadorLinea.addEventListener("pointerup", () => { arrastrando = false; });

// También permite hacer clic en cualquier parte del comparador para saltar ahí
comparador.addEventListener("click", (e) => {
  if (e.target === comparadorLinea || comparadorLinea.contains(e.target)) return;
  moverDivisor(calcularPosicionRelativa(e.clientX));
});

// posición inicial del divisor: 50%
moverDivisor(0.5);

// ── Severidad: actualizar el número mientras se arrastra el slider ──────────
inputSeveridad.addEventListener("input", () => {
  valorSeveridad.textContent = inputSeveridad.value;
});

// ── Selección de archivo por clic ────────────────────────────────────────────
zonaCarga.addEventListener("click", () => inputImagen.click());

zonaCarga.addEventListener("keydown", (evento) => {
  if (evento.key === "Enter" || evento.key === " ") {
    evento.preventDefault();
    inputImagen.click();
  }
});

inputImagen.addEventListener("change", () => {
  if (inputImagen.files && inputImagen.files[0]) {
    mostrarPreviaArchivo(inputImagen.files[0]);
  }
});

// ── Arrastrar y soltar ───────────────────────────────────────────────────────
["dragenter", "dragover"].forEach((evt) => {
  zonaCarga.addEventListener(evt, (e) => {
    e.preventDefault();
    zonaCarga.classList.add("zona-carga--arrastrando");
  });
});

["dragleave", "drop"].forEach((evt) => {
  zonaCarga.addEventListener(evt, (e) => {
    e.preventDefault();
    zonaCarga.classList.remove("zona-carga--arrastrando");
  });
});

zonaCarga.addEventListener("drop", (evento) => {
  const archivos = evento.dataTransfer.files;
  if (archivos && archivos[0]) {
    inputImagen.files = archivos;
    mostrarPreviaArchivo(archivos[0]);
  }
});

function mostrarPreviaArchivo(archivo) {
  const lector = new FileReader();
  lector.onload = (e) => {
    zonaCargaContenido.innerHTML = `
      <img class="zona-carga__previa" src="${e.target.result}" alt="Previsualización de la imagen elegida">
      <p class="zona-carga__detalle">${archivo.name}</p>
    `;
  };
  lector.readAsDataURL(archivo);
}

// ── Envío del formulario ─────────────────────────────────────────────────────
form.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  ocultarError();

  if (!inputImagen.files || !inputImagen.files[0]) {
    mostrarError("Elegí una imagen antes de procesar.");
    return;
  }

  const datos = new FormData(form);

  ponerCargando(true);

  try {
    const respuesta = await fetch("/procesar", {
      method: "POST",
      body: datos,
    });

    const cuerpo = await respuesta.json();

    if (!respuesta.ok) {
      mostrarError(cuerpo.error || "No se pudo procesar la imagen.");
      return;
    }

    mostrarResultados(cuerpo);
  } catch (error) {
    mostrarError("No se pudo conectar con el servidor. Intentá de nuevo.");
  } finally {
    ponerCargando(false);
  }
});

function ponerCargando(estaCargando) {
  botonProcesar.disabled = estaCargando;
  botonProcesar.classList.toggle("boton-procesar--cargando", estaCargando);
}

function mostrarError(texto) {
  mensajeError.textContent = texto;
  mensajeError.hidden = false;
}

function ocultarError() {
  mensajeError.hidden = true;
  mensajeError.textContent = "";
}

function mostrarResultados(datos) {
  imgOriginal.src = datos.original;
  imgSimulada.src = datos.simulada;
  imgCorregida.src = datos.corregida;

  mapaImagenes.original = datos.original;
  mapaImagenes.simulada = datos.simulada;
  mapaImagenes.corregida = datos.corregida;
  actualizarComparador();

  panelVacio.hidden = true;
  panelResultados.hidden = false;
  panelResultados.scrollIntoView({ behavior: "smooth", block: "nearest" });
}
