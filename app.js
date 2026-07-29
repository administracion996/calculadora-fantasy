let datosFantasy = {};

// Cargar los datos desde el archivo datos.json o usar datos de respaldo si falla el fetch
async function cargarDatos() {
    try {
        const respuesta = await fetch('./datos.json');
        if (!respuesta.ok) throw new Error("No se pudo cargar datos.json");
        datosFantasy = await respuesta.json();
    } catch (error) {
        console.warn("Usando datos de respaldo temporal...", error);
        // Datos por si datos.json aún no se ha generado en GitHub
        datosFantasy = {
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
    }
    
    // Mostrar la plataforma Biwenger por defecto al cargar
    mostrarPlataforma('biwenger');
}

// Función para cambiar de pestaña al pulsar los botones
function mostrarPlataforma(plataforma) {
    if (!datosFantasy || !datosFantasy[plataforma]) return;

    // Actualizar el estado visual de los botones
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    const btnActivo = document.getElementById(`btn-${plataforma}`);
    if (btnActivo) btnActivo.classList.add('active');

    const info = datosFantasy[plataforma];

    // Renderizar Chollos
    const contenedorChollos = document.getElementById('lista-chollos');
    if (contenedorChollos) {
        contenedorChollos.innerHTML = info.chollos.map(j => `
            <div class="card item-chollo" style="border: 1px solid #ccc; padding: 12px; margin: 8px 0; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0;">${j.nombre}</h3>
                    <span style="background: #2563eb; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">${j.pos}</span>
                </div>
                <p style="margin: 5px 0; color: #555;">⚽ ${j.equipo}</p>
                <div>
                    <p style="margin: 2px 0;">📈 Subida: <strong style="color: green;">${j.subida}</strong></p>
                    <p style="margin: 2px 0;">💰 Precio: ${j.precio}</p>
                    <p style="margin: 2px 0;">⭐ Puntos: ${j.pts}</p>
                </div>
            </div>
        `).join('');
    }

    // Renderizar Bajas y Lesionados
    const contenedorBajas = document.getElementById('lista-bajas');
    if (contenedorBajas) {
        contenedorBajas.innerHTML = info.bajas.map(b => `
            <div class="card item-baja" style="border: 1px solid #fca5a5; background: #fff5f5; padding: 12px; margin: 8px 0; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0;">${b.nombre}</h3>
                    <span style="background: #dc2626; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">${b.estado}</span>
                </div>
                <p style="margin: 5px 0; color: #555;">⚽ ${b.equipo}</p>
                <p style="margin: 2px 0; color: #7f1d1d;">📋 ${b.motivo}</p>
            </div>
        `).join('');
    }
}

// Escuchar el evento cuando el HTML esté cargado en la pantalla
document.addEventListener('DOMContentLoaded', cargarDatos);