// Datos simulados de los juegos (En la fase final, este objeto lo generará el bot automático)
const datosJuegos = {
    biwenger: {
        chollos: [
            { nombre: "Lamine Yamal", equipo: "FC Barcelona", pos: "DEL", subida: "+ 320.000 €", precio: "18.400.000 €", pts: "8.2" },
            { nombre: "Brahim Díaz", equipo: "Real Madrid", pos: "MED", subida: "+ 210.000 €", precio: "5.100.000 €", pts: "6.1" },
            { nombre: "Kirian Rodríguez", equipo: "Las Palmas", pos: "MED", subida: "+ 140.000 €", precio: "7.800.000 €", pts: "6.5" }
        ],
        bajas: [
            { nombre: "Gavi", equipo: "FC Barcelona", estado: "🔴 Baja Confirmada", motivo: "Rotura de ligamento" },
            { nombre: "Jude Bellingham", equipo: "Real Madrid", estado: "🟡 Duda", motivo: "Molestias en el hombro" }
        ]
    },
    laliga: {
        chollos: [
            { nombre: "Kylian Mbappé", equipo: "Real Madrid", pos: "DEL", subida: "+ 500.000 €", precio: "62.000.000 €", pts: "9.1" },
            { nombre: "Nico Williams", equipo: "Athletic Club", pos: "DEL", subida: "+ 290.000 €", precio: "35.500.000 €", pts: "7.4" },
            { nombre: "Sancet", equipo: "Athletic Club", pos: "MED", subida: "+ 180.000 €", precio: "19.200.000 €", pts: "5.8" }
        ],
        bajas: [
            { nombre: "Vinícius Jr.", equipo: "Real Madrid", estado: "🔴 Sancionado", motivo: "Acumulación de tarjetas" },
            { nombre: "Isco Alarcón", equipo: "Real Betis", estado: "🟡 Duda", motivo: "Sobrecarga muscular" }
        ]
    },
    comunio: {
        chollos: [
            { nombre: "Antoine Griezmann", equipo: "Atlético de Madrid", pos: "DEL", subida: "+ 150.000 €", precio: "12.300.000 €", pts: "7.0" },
            { nombre: "Take Kubo", equipo: "Real Sociedad", pos: "DEL", subida: "+ 110.000 €", precio: "8.900.000 €", pts: "5.9" },
            { nombre: "Aleix García", equipo: "Girona FC", pos: "MED", subida: "+ 90.000 €", precio: "9.500.000 €", pts: "6.8" }
        ],
        bajas: [
            { nombre: "Mikel Oyarzabal", equipo: "Real Sociedad", estado: "🟡 Duda", motivo: "Evaluación médica" }
        ]
    }
};

let juegoActual = 'biwenger';

// Función para cambiar de juego y renderizar los datos
function cambiarJuego(juego) {
    juegoActual = juego;

    // Actualizar estilo de los botones
    document.querySelectorAll('.btn-juego').forEach(btn => {
        btn.classList.remove('bg-emerald-500', 'text-slate-950');
        btn.classList.add('bg-slate-800', 'text-slate-300');
    });

    const btnActivo = document.getElementById(`btn-${juego}`);
    if (btnActivo) {
        btnActivo.classList.remove('bg-slate-800', 'text-slate-300');
        btnActivo.classList.add('bg-emerald-500', 'text-slate-950');
    }

    // Renderizar Chollos
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

    // Renderizar Bajas
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

// Cargar Biwenger por defecto al iniciar
document.addEventListener('DOMContentLoaded', () => {
    cambiarJuego('biwenger');
});