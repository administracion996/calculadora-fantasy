// Base de datos de reserva integrada directamente en el JS para garantizar que SIEMPRE haya datos
let datosGlobales = {
    biwenger: {
        chollos: [
            { nombre: "Lamine Yamal", equipo: "FC Barcelona", pos: "DEL", pts: "8.8", precio: "22.100.000 €", subida: "+ 450.000 €" },
            { nombre: "Raphinha", equipo: "FC Barcelona", pos: "DEL", pts: "9.1", precio: "19.800.000 €", subida: "+ 520.000 €" },
            { nombre: "Pedri", equipo: "FC Barcelona", pos: "MED", pts: "7.9", precio: "15.400.000 €", subida: "+ 210.000 €" },
            { nombre: "Robert Lewandowski", equipo: "FC Barcelona", pos: "DEL", pts: "8.4", precio: "18.200.000 €", subida: "- 150.000 €" },
            { nombre: "Kylian Mbappé", equipo: "Real Madrid", pos: "DEL", pts: "9.4", precio: "24.500.000 €", subida: "+ 680.000 €" },
            { nombre: "Jude Bellingham", equipo: "Real Madrid", pos: "MED", pts: "8.5", precio: "19.100.000 €", subida: "+ 190.000 €" },
            { nombre: "Vinícius Jr.", equipo: "Real Madrid", pos: "DEL", pts: "8.9", precio: "21.000.000 €", subida: "- 220.000 €" },
            { nombre: "Federico Valverde", equipo: "Real Madrid", pos: "MED", pts: "7.8", precio: "14.800.000 €", subida: "+ 140.000 €" },
            { nombre: "Nico Williams", equipo: "Athletic Club", pos: "DEL", pts: "7.8", precio: "12.500.000 €", subida: "+ 310.000 €" },
            { nombre: "Iñaki Williams", equipo: "Athletic Club", pos: "DEL", pts: "7.4", precio: "10.800.000 €", subida: "+ 180.000 €" },
            { nombre: "Oihan Sancet", equipo: "Athletic Club", pos: "MED", pts: "7.1", precio: "8.400.000 €", subida: "+ 90.000 €" },
            { nombre: "Antoine Griezmann", equipo: "Atlético de Madrid", pos: "DEL", pts: "7.6", precio: "13.800.000 €", subida: "+ 210.000 €" },
            { nombre: "Julián Alvarez", equipo: "Atlético de Madrid", pos: "DEL", pts: "7.5", precio: "15.200.000 €", subida: "+ 290.000 €" },
            { nombre: "Ayoze Pérez", equipo: "Villarreal CF", pos: "DEL", pts: "7.9", precio: "11.200.000 €", subida: "+ 340.000 €" },
            { nombre: "Alex Baena", equipo: "Villarreal CF", pos: "MED", pts: "8.1", precio: "12.900.000 €", subida: "+ 260.000 €" },
            { nombre: "Iago Aspas", equipo: "Celta de Vigo", pos: "DEL", pts: "7.7", precio: "9.800.000 €", subida: "+ 120.000 €" },
            { nombre: "Oscar Mingueza", equipo: "Celta de Vigo", pos: "DEF", pts: "7.2", precio: "6.500.000 €", subida: "+ 150.000 €" },
            { nombre: "Giovani Lo Celso", equipo: "Real Betis", pos: "MED", pts: "8.0", precio: "11.500.000 €", subida: "+ 310.000 €" },
            { nombre: "Isco Alarcón", equipo: "Real Betis", pos: "MED", pts: "8.2", precio: "10.200.000 €", subida: "+ 190.000 €" },
            { nombre: "Mikel Oyarzabal", equipo: "Real Sociedad", pos: "DEL", pts: "6.9", precio: "8.900.000 €", subida: "- 80.000 €" },
            { nombre: "Takefusa Kubo", equipo: "Real Sociedad", pos: "DEL", pts: "7.3", precio: "9.400.000 €", subida: "+ 110.000 €" },
            { nombre: "Bryan Gil", equipo: "Girona FC", pos: "DEL", pts: "7.0", precio: "5.800.000 €", subida: "+ 140.000 €" },
            { nombre: "Dodi Lukebakio", equipo: "Sevilla FC", pos: "DEL", pts: "7.3", precio: "7.200.000 €", subida: "+ 230.000 €" },
            { nombre: "Ante Budimir", equipo: "CA Osasuna", pos: "DEL", pts: "7.5", precio: "8.100.000 €", subida: "+ 170.000 €" },
            { nombre: "Jorge de Frutos", equipo: "Rayo Vallecano", pos: "MED", pts: "6.8", precio: "4.200.000 €", subida: "+ 120.000 €" },
            { nombre: "Vedat Muriqi", equipo: "RCD Mallorca", pos: "DEL", pts: "7.1", precio: "6.900.000 €", subida: "+ 90.000 €" },
            { nombre: "Hugo Duro", equipo: "Valencia CF", pos: "DEL", pts: "6.7", precio: "5.400.000 €", subida: "+ 80.000 €" },
            { nombre: "Kike García", equipo: "Deportivo Alavés", pos: "DEL", pts: "6.5", precio: "3.100.000 €", subida: "+ 60.000 €" },
            { nombre: "Juan Cruz", equipo: "CD Leganés", pos: "DEL", pts: "6.9", precio: "3.800.000 €", subida: "+ 110.000 €" },
            { nombre: "Javi Puado", equipo: "RCD Espanyol", pos: "DEL", pts: "6.8", precio: "4.500.000 €", subida: "+ 90.000 €" },
            { nombre: "Raúl Moro", equipo: "Real Valladolid", pos: "DEL", pts: "6.7", precio: "3.400.000 €", subida: "+ 80.000 €" },
            { nombre: "Alberto Moleiro", equipo: "UD Las Palmas", pos: "MED", pts: "7.2", precio: "5.900.000 €", subida: "+ 130.000 €" },
            { nombre: "Mauro Arambarri", equipo: "Getafe CF", pos: "MED", pts: "6.9", precio: "4.100.000 €", subida: "+ 100.000 €" }
        ]
    }
};

// Clonar los datos por defecto para LaLiga y Comunio si no se leen del JSON
datosGlobales.laliga = JSON.parse(JSON.stringify(datosGlobales.biwenger));
datosGlobales.comunio = JSON.parse(JSON.stringify(datosGlobales.biwenger));

let plataformaActual = 'biwenger';

async function inicializarApp() {
    try {
        const res = await fetch('./datos.json');
        if (res.ok) {
            const nuevosDatos = await res.json();
            if (nuevosDatos && nuevosDatos.biwenger) {
                datosGlobales = nuevosDatos;
            }
        }
    } catch (e) {
        console.log("Cargando base de datos interna...");
    }
    
    // Pintar los datos inmediatamente
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
    if (!datosGlobales[plataformaActual] || !datosGlobales[plataformaActual].chollos) return;

    const textoBusqueda = document.getElementById('filtro-nombre')?.value.toLowerCase().trim() || '';
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
            contenedor.innerHTML = `<div class="col-span-full text-center text-slate-500 py-12">No hay resultados para los filtros seleccionados. Prueba a cambiar de posición o poner "Todos los equipos".</div>`;
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
