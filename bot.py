import json
import time
from playwright.sync_api import sync_playwright

def extraer_mercado_completo():
    print("🤖 Navegando a Analítica Fantasy para extraer el mercado completo...")
    
    jugadores_dict = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Seteamos un tamaño de ventana gigante para que fuerce renderizado de mas filas
        context = browser.new_context(
            viewport={"width": 1920, "height": 10800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/mercado", timeout=60000, wait_until="networkidle")
            time.sleep(4)

            # Intentar desplegar opciones de filas si existe un <select> de paginacion
            try:
                selects = page.query_selector_all("select")
                for s in selects:
                    # Si tiene opciones como 10, 20, 50, 100 o Todos, elegimos la mayor
                    options = s.query_selector_all("option")
                    if len(options) > 1:
                        s.select_option(index=len(options) - 1)
                        time.sleep(2)
            except Exception:
                pass

            # Recorrer páginas mediante clic en botón 'Siguiente'
            pagina = 1
            max_paginas = 80

            while pagina <= max_paginas:
                filas = page.query_selector_all("tbody tr")
                
                for fila in filas:
                    celdas = fila.query_selector_all("td")
                    if len(celdas) >= 4:
                        # Extraer solo el texto de la primera celda (Nombre)
                        lineas_nombre = [t.strip() for t in celdas[0].inner_text().split("\n") if t.strip()]
                        if not lineas_nombre:
                            continue
                        
                        # Limpiar si el nombre empieza por un número de ranking
                        nombre = lineas_nombre[0]
                        if nombre and nombre[0].isdigit():
                            partes = nombre.split()
                            if len(partes) > 1 and partes[0].isdigit():
                                nombre = " ".join(partes[1:])

                        equipo = celdas[1].inner_text().strip().split("\n")[0] if len(celdas) > 1 else "LaLiga"
                        precio = celdas[2].inner_text().strip().split("\n")[0] if len(celdas) > 2 else "0 €"
                        subida = celdas[3].inner_text().strip().split("\n")[0] if len(celdas) > 3 else "0 €"
                        pts = celdas[4].inner_text().strip().split("\n")[0] if len(celdas) > 4 else "0.0"

                        if nombre and nombre not in jugadores_dict:
                            jugadores_dict[nombre] = {
                                "nombre": nombre,
                                "equipo": equipo,
                                "pos": "JUG",
                                "precio": precio,
                                "subida": subida,
                                "pts": pts
                            }

                # Buscar botón para avanzar página
                siguiente = page.query_selector("button:has-text('>'), button:has-text('Siguiente'), [aria-label*='Next'], [aria-label*='siguiente']")
                
                if siguiente and siguiente.is_visible() and siguiente.is_enabled():
                    cant_antes = len(jugadores_dict)
                    siguiente.click()
                    time.sleep(1.5)
                    pagina += 1
                    # Si tras hacer clic no se añaden jugadores nuevos en 2 intentos, terminamos
                    if len(jugadores_dict) == cant_antes and pagina > 5:
                        break
                else:
                    # Hacer un scroll progresivo por si la tabla carga con scroll
                    page.evaluate("window.scrollBy(0, 1500)")
                    time.sleep(1)
                    if pagina > 5 and len(filas) <= 10:
                        break
                    pagina += 1

            resultado = list(jugadores_dict.values())

            if resultado:
                base_datos = {"laliga": {"chollos": resultado}}
                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump(base_datos, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡ÉXITO! Se extrajeron {len(resultado)} jugadores en total.")
            else:
                print("❌ No se pudieron leer filas de la tabla.")

        except Exception as e:
            print(f"❌ Error durante el raspado: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    extraer_mercado_completo()