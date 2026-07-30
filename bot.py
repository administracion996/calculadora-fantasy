import json
import time
from playwright.sync_api import sync_playwright

def extraer_todos_los_jugadores():
    print("🤖 Iniciando navegador para extraer la lista completa de Analítica Fantasy...")
    
    jugadores_totales = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/mercado", timeout=60000, wait_until="networkidle")
            time.sleep(3)

            # Intentar cambiar el selector de "Filas por página" a "Mostrar todos" o 100 si existe
            try:
                selectores = page.query_selector_all("select")
                for sel in selectores:
                    opciones = sel.inner_text()
                    if "10" in opciones or "20" in opciones or "50" in opciones:
                        sel.select_option(index=-1) # Seleccionar la opción más grande (ej: Todos / 100)
                        time.sleep(2)
            except Exception:
                pass

            # Bucle para recorrer todas las páginas disponibles
            pagina_actual = 1
            max_paginas = 60 # Límite de seguridad para recorrer todo el mercado

            while pagina_actual <= max_paginas:
                print(f"📄 Extrayendo datos de la página {pagina_actual}...")
                
                # Extraer filas visibles de la tabla
                filas = page.query_selector_all("tbody tr")
                cant_previo = len(jugadores_totales)

                for fila in filas:
                    textos = [t.strip() for t in fila.inner_text().split("\n") if t.strip()]
                    if len(textos) >= 3:
                        nombre = textos[0]
                        # Limpiar nombre por si trae número de posición
                        if nombre and nombre[0].isdigit():
                            nombre = " ".join(nombre.split()[1:])

                        equipo = textos[1] if len(textos) > 1 else "LaLiga"
                        precio = textos[2] if len(textos) > 2 else "0 €"
                        subida = textos[3] if len(textos) > 3 else "0 €"
                        pts = textos[4] if len(textos) > 4 else "0.0"

                        jugadores_totales[nombre] = {
                            "nombre": nombre,
                            "equipo": equipo,
                            "pos": "JUG",
                            "precio": precio,
                            "subida": subida,
                            "pts": pts
                        }

                # Buscar botón "Siguiente" o ">" para pasar de página
                bot_siguiente = page.query_selector("button:has-text('>'), button:has-text('Siguiente'), [aria-label*='next'], .pagination-next")
                
                if bot_siguiente and bot_siguiente.is_enabled():
                    bot_siguiente.click()
                    time.sleep(1.5)
                    pagina_actual += 1
                else:
                    # Intento alternativo: hacer scroll si no hay botones de página
                    page.evaluate("window.scrollBy(0, 800)")
                    time.sleep(1)
                    if len(jugadores_totales) == cant_previo and pagina_actual > 3:
                        print("🏁 No hay más páginas o jugadores nuevos.")
                        break
                    pagina_actual += 1

            lista_final = list(jugadores_totales.values())

            if lista_final:
                base_datos = {"laliga": {"chollos": lista_final}}
                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump(base_datos, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡ÉXITO MASIVO! Extraídos {len(lista_final)} jugadores reales de Analítica Fantasy.")
            else:
                print("❌ No se pudieron capturar los datos.")

        except Exception as e:
            print(f"❌ Error durante el raspado: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    extraer_todos_los_jugadores()