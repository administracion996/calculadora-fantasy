import json
import time
from playwright.sync_api import sync_playwright

def extraer_mercado_infinito():
    print("🤖 Navegación con timeout desactivado para Analítica Fantasy...")
    
    jugadores_totales = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1400, "height": 900}
        )
        # Timeout desactivado globalmente a nivel de página (0 = Infinito)
        page = context.new_page()
        page.set_default_timeout(0)

        try:
            # 1. Cargar la URL sin límite de tiempo duro
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/mercado", wait_until="commit")
            time.sleep(5)

            # Cerrar cookies si saltan
            try:
                page.evaluate("""() => {
                    const btn = document.querySelector("button:has-text('Aceptar'), button:has-text('ACEPTAR'), #onetrust-accept-btn-handler");
                    if (btn) btn.click();
                }""")
            except Exception:
                pass

            pagina_num = 1
            max_paginas = 80

            while pagina_num <= max_paginas:
                time.sleep(1.5) # Pausa estable para dejar pintar al cliente

                # Extraer filas directamente mediante ejecucion JS interna para evitar bloqueos del locator
                filas_js = page.evaluate("""() => {
                    const trs = document.querySelectorAll("tbody tr");
                    const res = [];
                    trs.forEach(tr => {
                        const tds = tr.querySelectorAll("td");
                        if (tds.length >= 4) {
                            res.push({
                                nom: tds[0] ? tds[0].innerText.trim() : "",
                                eq: tds[1] ? tds[1].innerText.trim() : "LaLiga",
                                val: tds[2] ? tds[2].innerText.trim() : "0 €",
                                sub: tds[3] ? tds[3].innerText.trim() : "0 €",
                                pt: tds[4] ? tds[4].innerText.trim() : "0.0"
                            });
                        }
                    });
                    return res;
                }""")

                nuevos_en_pag = 0
                for item in filas_js:
                    lineas = item["nom"].split("\n")
                    nombre = lineas[0].strip() if lineas else ""

                    # Limpiar ranking
                    if nombre and nombre[0].isdigit():
                        partes = nombre.split()
                        if len(partes) > 1 and partes[0].isdigit():
                            nombre = " ".join(partes[1:])

                    equipo = item["eq"].split("\n")[0]
                    precio = item["val"].split("\n")[0]
                    subida = item["sub"].split("\n")[0]
                    pts = item["pt"].split("\n")[0]

                    if nombre and nombre not in jugadores_totales:
                        jugadores_totales[nombre] = {
                            "nombre": nombre,
                            "equipo": equipo,
                            "pos": "JUG",
                            "precio": precio,
                            "subida": subida,
                            "pts": pts
                        }
                        nuevos_en_pag += 1

                print(f"📄 Página {pagina_num}: leídos {len(filas_js)} elementos (Total acumulado: {len(jugadores_totales)})")

                # Intentar avanzar de página ejecutando click directo en JS sin esperar locators
                avanzo = page.evaluate("""(numSig) => {
                    // Buscar botón con el número de la siguiente página o flechas
                    const btns = Array.from(document.querySelectorAll("button, a, div[role='button']"));
                    let target = btns.find(b => b.innerText.trim() === String(numSig));
                    if (!target) {
                        target = btns.find(b => b.innerText.trim() === '>' || b.getAttribute('aria-label')?.includes('next'));
                    }
                    if (target) {
                        target.click();
                        return true;
                    }
                    return false;
                }""", pagina_num + 1)

                if avanzo:
                    pagina_num += 1
                else:
                    # Si no hay botón numérico, scroll progresivo
                    page.evaluate("window.scrollBy(0, 1200)")
                    time.sleep(1)
                    if nuevos_en_pag == 0 and pagina_num > 4:
                        print("🏁 No se encontraron más páginas ni filas nuevas.")
                        break
                    pagina_num += 1

            resultado = list(jugadores_totales.values())

            if resultado:
                base_datos = {"laliga": {"chollos": resultado}}
                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump(base_datos, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡ÉXITO! Guardados {len(resultado)} jugadores reales de Analítica Fantasy.")
            else:
                print("❌ No se obtuvieron registros de la tabla.")

        except Exception as e:
            print(f"❌ Error durante el raspado: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    extraer_mercado_infinito()