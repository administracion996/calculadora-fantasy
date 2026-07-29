let datosJuegos = {};
let juegoActual = 'biwenger';

// Función para cargar el archivo datos.json actualizado por el robot
async function cargarDatos() {
    try {
        const respuesta = await fetch('datos.json');
        datosJuegos = await respuesta.json();
        cambiarJuego('biwenger'); // Carga Biwenger por defecto
    } catch (error) {
        console.error("Error al cargar los datos:", error);
    }
}

// Función para cambiar de juego y renderizar en pantalla
function cambiarJuego(juego) {
    juegoActual = juego;

    if (!datosJuegos[juego]) return;

    // Estilos de los botones
    document.querySelectorAll('.btn-juego').forEach(btn => {
        btn.classList.remove('bg-emerald-500', 'text-slate-950');
        btn.classList.add('bg-slate-800', 'text-slate-300');
    });

    const btnActivo = document.getElementById(`btn-${juego}`);
    if (btnActivo) {
        btnActivo.classList.remove('bg-slate-800', 'text-slate-300');
        btnActivo.classList.add('bg-emerald-500', 'text-slate-950');
    }

    // Dibujar Chollos
    const contenedorChollos = document.getElementById('contenedor-chollos');
    contenedorChollos.innerHTML = datosJuegos[juego].chollos.map(item => `
        <div class="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5 hover:border-emerald-500/50 transition">
            <div class="flex justify-between items-start">
                <div>
                    <span class="text-xs font-semibold text-slate-400">${item.pos} • ${item.equipo}</span>
                    <h4 class="text-lg font-bold mt-1">${item.nombre}</h4>
                </div>
                <span class="bg-emerald-500/20 text-emerald-400 text-xs font-bold px-2 py-1 rounded">
                    ${item.subida}
                </span>
            </div>
            <div class="mt-4 pt-4 border-t border-slate-700/50 flex justify-between text-sm">
                <span class="text-slate-400">Precio: <strong class="text-white">${item.precio}</strong></span>
                <span class="text-slate-400">Media: <strong class="text-emerald-400">${item.pts} pts</strong></span>
            </div>
        </div>
    `).join('');

    // Dibujar Bajas / Dudas
    const contenedorBajas = document.getElementById('contenedor-bajas');
    contenedorBajas.innerHTML = datosJuegos[juego].bajas.map(item => `
        <tr class="hover:bg-slate-800/50 transition">
            <td class="py-3 px-4 font-semibold text-white">${item.nombre}</td>
            <td class="py-3 px-4 text-slate-400">${item.equipo}</td>
            <td class="py-3 px-4">
                <span class="${item.estado.includes('🔴') ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-amber-500/20 text-amber-400 border-amber-500/30'} border text-xs px-2.5 py-1 rounded-full font-medium inline-block">
                    ${item.estado}
                </span>
            </td>
            <td class="py-3 px-4 text-slate-400">${item.motivo}</td>
        </tr>
    `).join('');
}

// Iniciar la carga al abrir la web
document.addEventListener('DOMContentLoaded', cargarDatos);