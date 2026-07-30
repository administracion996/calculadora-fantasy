import json
import time
from playwright.sync_api import sync_playwright

def extraer_con_navegador():
    print("🤖 Abriendo navegador real para cargar www.analiticafantasy.com...")
    
    with sync_playwright() as p:
        # Lanzar un navegador Chromium real
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # Ir directamente a la URL de Mercado LaLiga Fantasy
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/mercado", timeout=60000, wait_until="networkidle")
            time.sleep(5)  # Esperar renderizado completo de la tabla

            # Esperar a que la tabla o los elementos de jugador estén presentes
            page.wait_for_selector("table, div[class*='player']", timeout=15000)

            # Extraer filas de la tabla
            filas = page.query_selector_all("tbody tr")
            jugadores = []

            for fila in filas:
                texto_fila = fila.inner_text().split("\n")
                columnas = fila.query_selector_all("td")

                if len(columnas) >= 4:
                    nombre = columnas[0].inner_text().strip()
                    equipo_pos = columnas[1].inner_text().strip() if len(columnas) > 1 else "LaLiga"
                    precio = columnas[2].inner_text().strip() if len(columnas) > 2 else "0 €"
                    subida = columnas[3].inner_text().strip() if len(columnas) > 3 else "0 €"
                    pts = columnas[4].inner_text().strip() if len(columnas) > 4 else "0.0"

                    jugadores.append({
                        "nombre": nombre,
                        "equipo": equipo_pos,
                        "pos": "JUG",
                        "precio": precio,
                        "subida": subida,
                        "pts": pts
                    })

            if jugadores:
                base_datos = {"laliga": {"chollos": jugadores}}
                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump(base_datos, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡ÉXITO EXTRAÍDO! {len(jugadores)} jugadores capturados en pantalla.")
            else:
                print("⚠️ La tabla no devolvió filas. Guardando estructura alternativa...")

        except Exception as e:
            print(f"❌ Error durante la navegación: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    extraer_con_navegador()