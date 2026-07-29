let datosGlobales = {};
let plataformaActual = 'biwenger';

async function inicializarApp() {
    try {
        const res = await fetch('./datos.json');
        if (res.ok) {
            datosGlobales = await res.json();
        }
    } catch (e) {
        console.warn("Error cargando JSON");
    }
    cambiarJuego('biwenger');
}

function cambiarJuego(juego) {
    plataformaActual = juego;

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

    aplicarFiltros();
}

function aplicarFiltros() {
    if (!datosGlobales[plataformaActual]) return;

    const textoBusqueda = document.getElementById('filtro-nombre')?.value.toLowerCase() || '';
    const equipoSel = document.getElementById('filtro-equipo')?.value || 'todos';
    const posicionSel = document.getElementById('filtro-posicion')?.value || 'todas';
    const tendenciaSel = document.getElementById('filtro-tendencia')?.value || 'todos';

    const listaJugadores = datosGlobales[plataformaActual].chollos;

    const resultados = listaJugadores.filter(j => {
        const coincideNombre = j.nombre.toLowerCase().includes(textoBusqueda);
        const coincideEquipo = equipoSel === 'todos' || j.equipo === equipoSel;
        const coincidePos = posicionSel === 'todas' || j.pos === posicionSel;
        
        let coincideTendencia = true;
        if (tendenciaSel === 'subida') coincideTendencia = j.subida.includes('+');
        if (tendenciaSel === 'bajada') coincideTendencia = j.subida.includes('-');

        return coincideNombre && coincideEquipo && coincidePos && coincideTendencia;
    });

    const contador = document.getElementById('contador-resultados');
    if (contador) contador.innerText = `Mostrando ${resultados.length} jugadores en ${plataformaActual.toUpperCase()}`;

    const contenedor = document.getElementById('contenedor-jugadores');
    if (contenedor) {
        if (resultados.length === 0) {
            contenedor.innerHTML = `<div class="col-span-full text-center text-slate-500 py-8">No hay resultados para esta búsqueda.</div>`;
            return;
        }

        contenedor.innerHTML = resultados.map(j => {
            const esSubida = j.subida.includes('+');
            return `
                <div class="bg-slate-900 p-4 rounded-xl border border-slate-800 space-y-2 hover:border-slate-700 transition">
                    <div class="flex justify-between items-center">
                        <h3 class="font-bold text-lg text-white">${j.nombre}</h3>
                        <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs px-2 py-0.5 rounded-md font-bold">${j.pos}</span>
                    </div>
                    <p class="text-slate-400 text-sm">⚽ ${j.equipo}</p>
                    <div class="text-sm space-y-1 pt-2 border-t border-slate-800">
                        <p class="text-slate-300">📈 Tendencia: <strong class="${esSubida ? 'text-emerald-400' : 'text-red-400'}">${j.subida}</strong></p>
                        <p class="text-slate-300">💰 Valor ${plataformaActual.toUpperCase()}: <strong>${j.precio}</strong></p>
                        <p class="text-slate-300">⭐ Media: ${j.pts} pts</p>
                    </div>
                </div>
            `;
        }).join('');
    }
}

document.addEventListener('DOMContentLoaded', inicializarApp);
