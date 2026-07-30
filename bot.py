import json
import time
from playwright.sync_api import sync_playwright

def extraer_mercado_paginado():
    print("🤖 Iniciando navegación interactiva por páginas en Analítica Fantasy...")
    
    jugadores_totales = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1400, "height": 900}
        )
        page = context.new_page()

        try:
            # 1. Cargar la URL exacta de Analítica Fantasy
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/mercado", timeout=60000, wait_until="networkidle")
            time.sleep(4)

            # 2. Intentar cambiar el selector de "Filas por página" si existe a la opción máxima
            try:
                select_elem = page.query_selector("select")
                if select_elem:
                    options = select_elem.query_selector_all("option")
                    if len(options) > 1:
                        select_elem.select_option(index=len(options) - 1)
                        time.sleep(3)
            except Exception:
                pass

            pagina_num = 1
            max_paginas = 60  # Límite alto para recorrer todo el mercado

            while pagina_num <= max_paginas:
                # Extraer las filas de la tabla visibles en la página actual
                filas = page.query_selector_all("tbody tr")
                nuevos_en_esta_pag = 0

                for fila in filas:
                    celdas = fila.query_selector_all("td")
                    if len(celdas) >= 4:
                        textos_nombre = celdas[0].inner_text().strip().split("\n")
                        nombre = textos_nombre[0].strip() if textos_nombre else ""
                        
                        # Limpiar número de posición/ranking si lo lleva pegado
                        if nombre and nombre[0].isdigit():
                            partes = nombre.split()
                            if len(partes) > 1 and partes[0].isdigit():
                                nombre = " ".join(partes[1:])

                        equipo = celdas[1].inner_text().strip().split("\n")[0] if len(celdas) > 1 else "LaLiga"
                        precio = celdas[2].inner_text().strip().split("\n")[0] if len(celdas) > 2 else "0 €"
                        subida = celdas[3].inner_text().strip().split("\n")[0] if len(celdas) > 3 else "0 €"
                        pts = celdas[4].inner_text().strip().split("\n")[0] if len(celdas) > 4 else "0.0"

                        if nombre and nombre not in jugadores_totales:
                            jugadores_totales[nombre] = {
                                "nombre": nombre,
                                "equipo": equipo,
                                "pos": "JUG",
                                "precio": precio,
                                "subida": subida,
                                "pts": pts
                            }
                            nuevos_en_esta_pag += 1

                print(f"📄 Página {pagina_num}: extraídos {len(filas)} elementos (Total acumulado: {len(jugadores_totales)})")

                # Buscar el botón para ir a la siguiente página
                # Probamos selectores comunes de paginación (botón '>', 'Siguiente', icono o la siguiente página numérica)
                bot_siguiente = page.query_selector("button:has-text('>'), [aria-label*='Next'], [aria-label*='siguiente'], .pagination-next, button.next")
                
                # Si no lo encuentra por texto/aria, intentar hacer clic en el botón con el número de la siguiente página
                if not bot_siguiente:
                    bot_siguiente = page.query_selector(f"button:has-text('{pagina_num + 1}'), a:has-text('{pagina_num + 1}')")

                if bot_siguiente and bot_siguiente.is_visible() and bot_siguiente.is_enabled():
                    bot_siguiente.click()
                    time.sleep(2)
                    pagina_num += 1
                else:
                    # Si no hay más botones de paginación, intentamos scroll por si es tabla infinita
                    page.evaluate("window.scrollBy(0, 1000)")
                    time.sleep(1.5)
                    filas_nuevas = page.query_selector_all("tbody tr")
                    if len(filas_nuevas) <= len(filas) and nuevos_en_esta_pag == 0:
                        print("🏁 Fin de la tabla alcanzado.")
                        break
                    pagina_num += 1

            resultado = list(jugadores_totales.values())

            if resultado:
                base_datos = {"laliga": {"chollos": resultado}}
                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump(base_datos, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡ÉXITO MASIVO! Guardados {len(resultado)} jugadores de Analítica Fantasy.")
            else:
                print("❌ No se pudieron capturar datos de la tabla.")

        except Exception as e:
            print(f"❌ Error durante el raspado: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    extraer_mercado_paginado()