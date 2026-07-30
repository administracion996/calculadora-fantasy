import json
import time
from playwright.sync_api import sync_playwright

def extraccion_todoterreno():
    print("🤖 Activando Protocolo TODOTERRENO (Cero Selectores Estrictos)...")
    jugadores_dict = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Ventana maximizada para renderizar todos los elementos del grid
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        try:
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/jugadores", wait_until="networkidle", timeout=60000)
            time.sleep(5)

            # 1. Quitar cookies molestando
            try:
                page.evaluate("document.querySelectorAll('button').forEach(b => { if(/aceptar|agree/i.test(b.innerText)) b.click(); })")
            except: pass

            for pag in range(1, 80):
                print(f"📄 Escaneando página {pag} a ciegas...")
                
                # NO usamos wait_for_selector. Simplemente esperamos 3 segundos a que la red y JS asienten el HTML.
                time.sleep(3) 

                # 2. Rescatamos el texto de la web buscando patrones universales (enlaces a perfiles o el símbolo €)
                datos_js = page.evaluate("""() => {
                    let resultados = [];
                    // Plan A: Buscar cualquier enlace que lleve a un jugador
                    let enlaces = document.querySelectorAll("a[href*='jugador']");
                    
                    if (enlaces.length > 0) {
                        enlaces.forEach(a => {
                            let cont = a;
                            // Subimos 4 niveles en el HTML para atrapar la tarjeta completa con precio, equipo, etc.
                            for(let i=0; i<4; i++) { if(cont.parentElement) cont = cont.parentElement; }
                            resultados.push(cont.innerText);
                        });
                    } else {
                        // Plan B: Buscar cualquier bloque de texto que contenga un euro
                        let todos = document.querySelectorAll("div, li");
                        todos.forEach(el => {
                            if (el.innerText && el.innerText.includes('€') && el.children.length === 0) {
                                let cont = el;
                                for(let i=0; i<4; i++) { if(cont.parentElement) cont = cont.parentElement; }
                                resultados.push(cont.innerText);
                            }
                        });
                    }
                    return Array.from(new Set(resultados)); // Limpiar textos duplicados
                }""")

                nuevos = 0
                for texto in datos_js:
                    if not texto: continue
                    # Partimos el bloque de texto en líneas limpias
                    lineas = [l.strip() for l in texto.split('\n') if l.strip()]
                    
                    nombre = ""
                    precio = "0 €"
                    pos = "JUG"
                    eq = "LaLiga"
                    pts = "0.0"

                    # 3. Heurística de Extracción (reconoce qué es cada cosa por su forma)
                    for l in lineas:
                        if '€' in l:
                            precio = l
                        elif l in ['POR', 'DEF', 'MED', 'DEL']:
                            pos = l
                        elif len(l) == 3 and l.isupper() and l not in ['POR', 'DEF', 'MED', 'DEL']:
                            eq = l
                        elif l.replace('.', '').replace(',', '').isdigit() and len(l) < 4:
                            pts = l
                        elif len(l) > 2 and not l.isdigit() and '€' not in l and not nombre:
                            # Evitar que el nombre se guarde como "1. Vinícius" (quitamos el ranking)
                            if len(l.split()) > 1 and l.split()[0].replace('.', '').isdigit():
                                nombre = " ".join(l.split()[1:])
                            else:
                                nombre = l

                    if nombre and nombre not in jugadores_dict:
                        jugadores_dict[nombre] = {
                            "nombre": nombre, "equipo": eq, "pos": pos,
                            "precio": precio, "subida": "0 €", "pts": pts
                        }
                        nuevos += 1

                print(f"✅ Jugadores acumulados: {len(jugadores_dict)} (Nuevos: {nuevos})")

                # Si escaneamos una página y no hay nadie nuevo, hemos terminado
                if nuevos == 0 and pag > 2:
                    print("🏁 No hay jugadores nuevos. Fin del escaneo.")
                    break

                # 4. Botón siguiente universal (busca >, », Siguiente, Next o Cargar más)
                avanzar = page.evaluate("""() => {
                    let botones = Array.from(document.querySelectorAll('button, a, div[role="button"]'));
                    let next = botones.find(b => {
                        let t = (b.innerText || '').trim().toLowerCase();
                        let a = (b.getAttribute('aria-label') || '').toLowerCase();
                        return t === '>' || t === '»' || t.includes('siguiente') || t.includes('cargar') || a.includes('next');
                    });
                    
                    if (next && !next.disabled && !next.className.includes('disabled')) {
                        next.scrollIntoView();
                        next.click();
                        return true;
                    }
                    return false;
                }""")

                if not avanzar:
                    print("🏁 Botón de avance no encontrado. Tabla finalizada.")
                    break

        except Exception as e:
            print(f"❌ Error en ejecución: {e}")
        finally:
            browser.close()

        # Guardado final
        resultado = list(jugadores_dict.values())
        if resultado:
            with open("datos.json", "w", encoding="utf-8") as f:
                json.dump({"laliga": {"chollos": resultado}}, f, ensure_ascii=False, indent=4)
            print(f"✅ ¡MISIÓN CUMPLIDA! Extraídos {len(resultado)} jugadores con éxito.")
        else:
            print("❌ No se capturaron datos.")

if __name__ == "__main__":
    extraccion_todoterreno()