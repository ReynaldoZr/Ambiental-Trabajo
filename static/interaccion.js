"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const otraMision = document.querySelector("[data-mision-url]");
  if (otraMision) {
    let cargando = false;
    otraMision.addEventListener("click", async (evento) => {
      if (evento.ctrlKey || evento.metaKey || evento.shiftKey || evento.altKey) return;
      evento.preventDefault();
      if (cargando) return;
      cargando = true;
      otraMision.setAttribute("aria-busy", "true");
      try {
        const respuesta = await fetch(otraMision.dataset.misionUrl);
        if (!respuesta.ok) throw new Error("No se pudo cargar la misión");
        const mision = await respuesta.json();
        const texto = document.querySelector(".texto-mision");
        texto.querySelector("h1").textContent = mision.titulo;
        texto.querySelector("p").textContent = mision.mensaje;
        if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
          texto.animate([{ opacity: .4, transform: "translateY(6px)" }, { opacity: 1, transform: "none" }], 240);
        }
      } catch {
        window.location.assign(otraMision.href);
      } finally {
        cargando = false;
        otraMision.removeAttribute("aria-busy");
      }
    });
  }

  const avance = document.querySelector("[data-avance-reto]");
  if (avance) {
    const formulario = avance.closest("form");
    const barra = avance.querySelector("progress");
    const contador = avance.querySelector("span");
    const preguntas = [...formulario.querySelectorAll("[data-pregunta]")];
    const anterior = formulario.querySelector("[data-anterior]");
    const siguiente = formulario.querySelector("[data-siguiente]");
    const enviar = formulario.querySelector("[type=submit]");
    let paso = 0;
    const mostrarPaso = (enfocar = false) => {
      preguntas.forEach((pregunta, indice) => {
        pregunta.hidden = indice !== paso;
      });
      anterior.hidden = paso === 0;
      siguiente.hidden = paso === preguntas.length - 1;
      enviar.hidden = !siguiente.hidden;
      if (enfocar) {
        const titulo = preguntas[paso].querySelector("legend");
        titulo.tabIndex = -1;
        titulo.focus();
      }
    };
    anterior.addEventListener("click", () => {
      paso -= 1;
      mostrarPaso(true);
    });
    siguiente.addEventListener("click", () => {
      if (!preguntas[paso].querySelector("input").reportValidity()) return;
      paso += 1;
      mostrarPaso(true);
    });
    const actualizar = () => {
      barra.value = formulario.querySelectorAll("input[type=radio]:checked").length;
      contador.textContent = `${barra.value}/${barra.max}`;
    };
    formulario.addEventListener("change", actualizar);
    window.addEventListener("pageshow", actualizar);
    actualizar();
    mostrarPaso();
    avance.hidden = false;
  }

  const filtros = document.querySelector("[data-filtros]");
  if (filtros) {
    const publicaciones = [...document.querySelectorAll("[data-publicacion]")];
    const botones = [...filtros.querySelectorAll("button")];
    const vacio = document.querySelector("[data-filtro-vacio]");
    botones.forEach((boton) => {
      boton.addEventListener("click", () => {
        botones.forEach((opcion) => opcion.setAttribute("aria-pressed", String(opcion === boton)));
        publicaciones.forEach((tarjeta) => {
          tarjeta.hidden = Boolean(boton.dataset.filtro) && tarjeta.dataset.publicacion !== boton.dataset.filtro;
        });
        vacio.hidden = publicaciones.some((tarjeta) => !tarjeta.hidden);
      });
    });
    filtros.hidden = false;
  }

  const campos = ["titulo", "categoria", "ubicacion", "descripcion"];
  document.querySelectorAll("[data-ejemplo-titulo]").forEach((boton) => {
    boton.addEventListener("click", () => {
      const valores = [
        boton.dataset.ejemploTitulo,
        boton.dataset.ejemploCategoria,
        boton.dataset.ejemploUbicacion,
        boton.dataset.ejemploDescripcion,
      ];
      campos.forEach((id, indice) => {
        const campo = document.getElementById(id);
        if (campo) campo.value = valores[indice];
      });
      document.getElementById("titulo")?.focus();
    });
  });

  const tipo = document.getElementById("tipo");
  const bloqueEvento = document.querySelector("[data-campos-evento]");
  if (tipo && bloqueEvento) {
    const fecha = document.getElementById("fecha_evento");
    const lugar = document.getElementById("lugar");
    const actualizarCampos = () => {
      const esEvento = tipo.value === "Evento";
      bloqueEvento.hidden = !esEvento;
      if (fecha) fecha.required = esEvento;
      if (lugar) lugar.required = esEvento;
    };
    tipo.addEventListener("change", actualizarCampos);
    actualizarCampos();
  }
});


document.querySelectorAll("[data-acierto]").forEach(boton => {
  boton.onclick = () => {
    const juego = boton.closest("[data-practica]");
    const salida = juego.querySelector("[role=status]");
    salida.textContent = boton.dataset.acierto === "1"
      ? "¡Acertaste! Juega el reto para sumar puntos a tu facultad."
      : "La mejor opción es «" + salida.dataset.solucion + "».";
    juego.querySelectorAll("button").forEach(b => b.disabled = true);
  };
});

const planes = [...document.querySelectorAll("[data-plan]")];
const categoriaAgenda = document.querySelector("#categoria-agenda");
if (categoriaAgenda) {
  const vista = document.querySelector("#vista-agenda");
  const filtrar = () => {
    for (const plan of planes) {
      const guardado = plan.querySelector("[data-guardar]").getAttribute("aria-pressed") === "true";
      plan.hidden = (categoriaAgenda.value !== "Todas" && categoriaAgenda.value !== plan.dataset.tipo)
        || (vista.value === "horas" && Number(plan.dataset.horas) === 0)
        || (vista.value === "guardado" && !guardado);
    }
    document.querySelector("#sin-planes").hidden = planes.some(p => !p.hidden);
  };
  for (const plan of planes) {
    const clave = "jaguar.plan." + plan.dataset.plan;
    const boton = plan.querySelector("[data-guardar]");
    const marcar = activo => {
      boton.setAttribute("aria-pressed", String(activo));
      boton.textContent = activo ? "✓ Guardado" : "Me interesa";
    };
    try { marcar(localStorage.getItem(clave) === "1"); } catch {}
    boton.onclick = () => {
      const activo = boton.getAttribute("aria-pressed") !== "true";
      marcar(activo);
      try { localStorage.setItem(clave, activo ? "1" : "0"); } catch {}
      filtrar();
    };
    plan.querySelector("[data-compartir]").onclick = async () => {
      const texto = [plan.querySelector("h2"),plan.querySelector(".meta"),plan.querySelector("strong")].map(el => el.textContent).join(" · ");
      try {
        if (navigator.share) await navigator.share({text:texto});
        else { await navigator.clipboard.writeText(texto); plan.querySelector("output").textContent = "Invitación copiada"; }
      } catch (e) { if (e.name !== "AbortError") plan.querySelector("output").textContent = texto; }
    };
  }
  categoriaAgenda.onchange = vista.onchange = filtrar;
  filtrar();
}
