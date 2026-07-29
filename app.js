// Datos por defecto (para que cargue SIEMPRE aunque datos.json no exista)
let datosFantasy = {
    biwenger: {
        chollos: [
            { nombre: "Lamine Yamal", equipo: "FC Barcelona", pos: "DEL", subida: "+ 350.000 €", precio: "18.700.000 €", pts: "8.3" },
            { nombre: "Brahim Díaz", equipo: "Real Madrid", pos: "MED", subida: "+ 220.000 €", precio: "5.300.000 €", pts: "6.2" }
        ],
        bajas: [
            { nombre: "Gavi", equipo: "FC Barcelona", estado: "Baja", motivo: "Rotura de ligamento cruzado" }
        ]
    },
    laliga: {
        chollos: [
            { nombre: "Kylian Mbappé", equipo: "Real Madrid", pos: "DEL", subida: "+ 600.000 €", precio: "62.600.000 €", pts: "9.2" },
            { nombre: "Nico Williams", equipo: "Athletic Club", pos: "DEL", subida: "+ 310.000 €", precio: "35.800.000 €", pts: "7.5" }
        ],
        bajas: [
            { nombre: "Vinícius Jr.", equipo: "Real Madrid", estado: "Sancionado", motivo: "Acumulación de tarjetas" }
        ]
    },
    comunio: {
        chollos: [
            { nombre: "Antoine Griezmann", equipo: "Atlético de Madrid", pos: "DEL", subida: "+ 160.000 €", precio: "12.460.000 €", pts: "7.1" }
        ],
        bajas: [
            { nombre: "Mikel Oyarzabal", equipo: "Real Sociedad", estado: "Duda", motivo: "Molestias musculares" }
        ]
    }
};

// Intentar cargar datos.json si existe en el servidor
async function cargarDatos() {
    try {
        const respuesta = await fetch('./datos.json');
        if (respuesta.ok) {
            datosFantasy = await respuesta.json();
        }
    } catch (e) {
        console.log("Usando datos de respaldo");
    }
    cambiarJuego('biwenger');
}

// ESTA ES LA FUNCIÓN QUE BUSCABA TU HTML
function cambiarJuego(juego) {
    if (!datosFantasy[juego]) return;

    // Actualizar botones activos
    document.querySelectorAll('button').forEach(btn => {
        if (btn.innerText.toLowerCase().includes(juego)) {
            btn.classList.add('bg-emerald-500', 'text-slate-900');
            btn.classList.remove('bg-slate-800', 'text-slate-300');
        } else if (btn.onclick && btn.onclick.toString().includes('cambiarJuego')) {
            btn.classList.remove('bg-emerald-500', 'text-slate-900');
            btn.classList.add('bg-slate-800', 'text-slate-300');
        }
    });

    const info = datosFantasy[juego];

    // Cargar Chollos
    const contenedorChollos = document.getElementById('lista-chollos');
    if (contenedorChollos) {
        contenedorChollos.innerHTML = info.chollos.map(j => `
            <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
                <div class="flex justify-between items-center mb-2">
                    <h3 class="font-bold text-lg text-white">${j.nombre}</h3>
                    <span class="bg-blue-600 text-white text-xs px-2 py-1 rounded-md font-semibold">${j.pos}</span>
                </div>
                <p class="text-slate-400 text-sm mb-2">⚽ ${j.equipo}</p>
                <div class="text-sm space-y-1">
                    <p class="text-slate-300">📈 Subida: <strong class="text-emerald-400">${j.subida}</strong></p>
                    <p class="text-slate-300">💰 Precio: ${j.precio}</p>
                    <p class="text-slate-300">⭐ Puntos: ${j.pts}</p>
                </div>
            </div>
        `).join('');
    }

    // Cargar Bajas
    const contenedorBajas = document.getElementById('lista-bajas');
    if (contenedorBajas) {
        contenedorBajas.innerHTML = info.bajas.map(b => `
            <div class="bg-slate-800 p-4 rounded-xl border border-red-900/50">
                <div class="flex justify-between items-center mb-2">
                    <h3 class="font-bold text-lg text-white">${b.nombre}</h3>
                    <span class="bg-red-600 text-white text-xs px-2 py-1 rounded-md font-semibold">${b.estado}</span>
                </div>
                <p class="text-slate-400 text-sm mb-2">⚽ ${b.equipo}</p>
                <p class="text-red-300 text-sm">📋 ${b.motivo}</p>
            </div>
        `).join('');
    }
}

// Cargar al iniciar la web
document.addEventListener('DOMContentLoaded', cargarDatos);
