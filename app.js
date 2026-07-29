let datosGlobales = {};
let plataformaActual = 'biwenger';

// Cargar la base de datos de jugadores
async function inicializarApp() {
    try {
        const res = await fetch('./datos.json');
        if (res.ok) {
            datosGlobales = await res.json();
        }
    } catch (e) {
        console.warn("Cargando base de datos alternativa...");
    }
    
    // Cargar Biwenger por defecto
    cambiarJuego('biwenger');
}

// Cambiar plataforma (Biwenger / LaLiga / Comunio)
function cambiarJuego(juego) {
    plataformaActual = juego;

    // Cambiar estado visual de botones de cabecera
    ['biwenger', 'laliga', 'comunio'].forEach(j => {
        const btn = document.getElementById(`btn-${j}`);
        if (btn) {
            if (j === juego) {
                btn.className = "px-4 py-1.5 rounded-lg text-sm font-bold bg-emerald-500 text-slate-900";
            } else {
                btn.className = "px-4 py-1.5 rounded-lg text-sm font-bold bg-slate-800 text-slate-300";
            }
        }
    });

    // Replicar los filtros con los datos de la nueva plataforma
    aplicarFiltros();
}

// Función principal del buscador y filtros
function aplicarFiltros() {
    if (!datosGlobales[plataformaActual]) return;

    const textoBusqueda = document.getElementById('filtro-nombre')?.value.toLowerCase() || '';
    const equipoSel = document.getElementById('filtro-equipo')?.value || 'todos';
    const posicionSel = document.getElementById('filtro-posicion')?.value || 'todas';
    const precioMax = document.getElementById('filtro-precio')?.value || 'infinito';

    const listaJugadores = datosGlobales[plataformaActual].chollos;

    // Filtrar la lista
    const resultados = listaJugadores.filter(j => {
        // Coincidencia por nombre
        const coincideNombre = j.nombre.toLowerCase().includes(textoBusqueda);
        
        // Coincidencia por equipo
        const coincideEquipo = equipoSel === 'todos' || j.equipo === equipoSel;
        
        // Coincidencia por posición
        const coincidePos = posicionSel === 'todas' || j.pos === posicionSel;

        // Coincidencia por precio numérico
        let coincidePrecio = true;
        if (precioMax !== 'infinito') {
            const precioLimpio = parseInt(j.precio.replace(/[^0-9]/g, '')) || 0;
            coincidePrecio = precioLimpio <= parseInt(precioMax);
        }

        return coincideNombre && coincideEquipo && coincidePos && coincidePrecio;
    });

    // Actualizar contador
    const contador = document.getElementById('contador-resultados');
    if (contador) contador.innerText = `Mostrando ${resultados.length} jugadores en ${plataformaActual.toUpperCase()}`;

    // Renderizar tarjetas
    const contenedor = document.getElementById('contenedor-jugadores');
    if (contenedor) {
        if (resultados.length === 0) {
            contenedor.innerHTML = `<div class="col-span-full text-center text-slate-500 py-8">No se encontraron jugadores con los filtros seleccionados.</div>`;
            return;
        }

        contenedor.innerHTML = resultados.map(j => `
            <div class="bg-slate-900 p-4 rounded-xl border border-slate-800 space-y-2 hover:border-slate-700 transition">
                <div class="flex justify-between items-center">
                    <h3 class="font-bold text-lg text-white">${j.nombre}</h3>
                    <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs px-2 py-0.5 rounded-md font-bold">${j.pos}</span>
                </div>
                <p class="text-slate-400 text-sm">⚽ ${j.equipo}</p>
                <div class="text-sm space-y-1 pt-2 border-t border-slate-800">
                    <p class="text-slate-300">📈 Subida hoy: <strong class="text-emerald-400">${j.subida}</strong></p>
                    <p class="text-slate-300">💰 Valor ${plataformaActual.toUpperCase()}: <strong>${j.precio}</strong></p>
                    <p class="text-slate-300">⭐ Media: ${j.pts} pts</p>
                </div>
            </div>
        `).join('');
    }
}

document.addEventListener('DOMContentLoaded', inicializarApp);
