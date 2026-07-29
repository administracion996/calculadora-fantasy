let datosFantasy = {
    biwenger: {
        chollos: [
            { nombre: "Lamine Yamal", equipo: "FC Barcelona", pos: "DEL", subida: "+ 350.000 €", precio: "18.700.000 €", pts: "8.3" },
            { nombre: "Brahim Díaz", equipo: "Real Madrid", pos: "MED", subida: "+ 220.000 €", precio: "5.300.000 €", pts: "6.2" }
        ],
        bajas: [
            { nombre: "Gavi", equipo: "FC Barcelona", estado: "🔴 Baja Confirmada", motivo: "Rotura de ligamento" }
        ]
    },
    laliga: {
        chollos: [
            { nombre: "Kylian Mbappé", equipo: "Real Madrid", pos: "DEL", subida: "+ 600.000 €", precio: "62.600.000 €", pts: "9.2" },
            { nombre: "Nico Williams", equipo: "Athletic Club", pos: "DEL", subida: "+ 310.000 €", precio: "35.800.000 €", pts: "7.5" }
        ],
        bajas: [
            { nombre: "Vinícius Jr.", equipo: "Real Madrid", estado: "🔴 Sancionado", motivo: "Acumulación de tarjetas" }
        ]
    },
    comunio: {
        chollos: [
            { nombre: "Antoine Griezmann", equipo: "Atlético de Madrid", pos: "DEL", subida: "+ 160.000 €", precio: "12.460.000 €", pts: "7.1" }
        ],
        bajas: [
            { nombre: "Mikel Oyarzabal", equipo: "Real Sociedad", estado: "🟡 Duda", motivo: "Evaluación médica" }
        ]
    }
};

// Cargar datos desde el JSON si existe
async function cargarDatos() {
    try {
        const respuesta = await fetch('./datos.json');
        if (respuesta.ok) {
            datosFantasy = await respuesta.json();
        }
    } catch (e) {
        console.log("Cargando datos por defecto");
    }
    mostrarPlataforma('biwenger');
}

// Función que cambia los datos según la pestaña
function mostrarPlataforma(plataforma) {
    if (!datosFantasy[plataforma]) return;

    // Cambiar color activo del botón
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    const btnActivo = document.getElementById(`btn-${plataforma}`);
    if (btnActivo) btnActivo.classList.add('active');

    const info = datosFantasy[plataforma];

    // Cargar Chollos
    const listaChollos = document.getElementById('lista-chollos');
    if (listaChollos) {
        listaChollos.innerHTML = info.chollos.map(j => `
            <div style="border: 1px solid #cbd5e1; background: #f8fafc; padding: 15px; border-radius: 8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0; font-size:16px;">${j.nombre}</h3>
                    <span style="background:#2563eb; color:white; padding:2px 6px; border-radius:4px; font-size:12px;">${j.pos}</span>
                </div>
                <p style="margin: 5px 0; color:#64748b; font-size:14px;">⚽ ${j.equipo}</p>
                <p style="margin:3px 0; font-size:13px;">📈 Subida: <strong style="color:#16a34a;">${j.subida}</strong></p>
                <p style="margin:3px 0; font-size:13px;">💰 Precio: ${j.precio}</p>
                <p style="margin:3px 0; font-size:13px;">⭐ Puntos: ${j.pts}</p>
            </div>
        `).join('');
    }

    // Cargar Bajas
    const listaBajas = document.getElementById('lista-bajas');
    if (listaBajas) {
        listaBajas.innerHTML = info.bajas.map(b => `
            <div style="border: 1px solid #fca5a5; background: #fef2f2; padding: 15px; border-radius: 8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0; font-size:16px;">${b.nombre}</h3>
                    <span style="background:#dc2626; color:white; padding:2px 6px; border-radius:4px; font-size:12px;">${b.estado}</span>
                </div>
                <p style="margin: 5px 0; color:#64748b; font-size:14px;">⚽ ${b.equipo}</p>
                <p style="margin:3px 0; color:#991b1b; font-size:13px;">📋 ${b.motivo}</p>
            </div>
        `).join('');
    }
}

// Inicializar al abrir
document.addEventListener('DOMContentLoaded', cargarDatos);
