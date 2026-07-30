import json
import time
from playwright.sync_api import sync_playwright

def extraer_con_interceptor():
    print("🤖 Lanzando navegador e interceptando datos de Analítica Fantasy...")
    
    jugadores_dict = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Interceptor de respuestas de red para cazar los datos reales de los jugadores
        def procesar_respuesta(response):
            try:
                # Comprobar si la respuesta contiene datos JSON
                if "application/json" in response.headers.get("content-type", ""):
                    payload = response.json()
                    lista = []
                    
                    if isinstance(payload, list):
                        lista = payload
                    elif isinstance(payload, dict):
                        lista = payload.get("players", payload.get("data", payload.get("chollos", [])))

                    if isinstance(lista, list):
                        for item in lista:
                            if isinstance(item, dict) and ("nickname" in item or "name" in item):
                                nombre = item.get("nickname", item.get("name", "")).strip()
                                if not nombre:
                                    continue
                                
                                equipo = item.get("teamName", item.get("team", {}).get("name", "LaLiga"))
                                pos = str(item.get("position", "MED"))
                                pos_map = {"1": "POR", "2": "DEF", "3": "MED", "4": "DEL"}
                                pos = pos_map.get(pos, pos)
                                
                                precio = item.get("marketValue", item.get("price", 0))
                                incremento = item.get("marketValueIncrement", item.get("priceIncrement", 0))
                                puntos = str(item.get("pointsAverage", item.get("points", 0)))

                                if isinstance(incremento, (int, float)):
                                    str_subida = f"+ {incremento:,} €".replace(',', '.') if incremento >= 0 else f"- {abs(incremento):,} €".replace(',', '.')
                                else:
                                    str_subida = str(incremento)

                                str_precio = f"{precio:,} €".replace(',', '.') if isinstance(precio, (int, float)) else str(precio)

                                jugadores_dict[nombre] = {
                                    "nombre": nombre,
                                    "equipo": equipo,
                                    "pos": pos,
                                    "precio": str_precio,
                                    "subida": str_subida,
                                    "pts": puntos
                                }
            except Exception:
                pass

        page.on("response", procesar_respuesta)

        try:
            # 1. Cargar la página de Mercado
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/mercado", timeout=60000, wait_until="networkidle")
            time.sleep(3)

            # 2. Intentar hacer click en selectores de paginación para forzar la carga de más filas
            for _ in range(12):
                page.evaluate("window.scrollBy(0, 1000)")
                time.sleep(0.5)

                bot_sig = page.query_selector("button:has-text('>'), [aria-label*='next'], .pagination-next")
                if bot_sig and bot_sig.is_enabled():
                    bot_sig.click()
                    time.sleep(1)

            # Si el interceptor de red no atrapó el JSON, usamos fallback directo sobre el DOM
            if not jugadores_dict:
                print("⚠️ Usando lector visual de respaldo...")
                filas = page.query_selector_all("tbody tr")
                for fila in filas:
                    celdas = fila.query_selector_all("td")
                    if len(celdas) >= 4:
                        nom = celdas[0].inner_text().strip().split("\n")[0]
                        eq = celdas[1].inner_text().strip() if len(celdas) > 1 else "LaLiga"
                        val = celdas[2].inner_text().strip() if len(celdas) > 2 else "0 €"
                        sub = celdas[3].inner_text().strip() if len(celdas) > 3 else "0 €"
                        pt = celdas[4].inner_text().strip() if len(celdas) > 4 else "0.0"

                        if nom:
                            jugadores_dict[nom] = {
                                "nombre": nom,
                                "equipo": eq,
                                "pos": "JUG",
                                "precio": val,
                                "subida": sub,
                                "pts": pt
                            }

            resultado_final = list(jugadores_dict.values())

            if resultado_final:
                base_datos = {"laliga": {"chollos": resultado_final}}
                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump(base_datos, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡ÉXITO DEFINITIVO! Extraídos {len(resultado_final)} jugadores reales de Analítica Fantasy.")
            else:
                print("❌ No se pudieron capturar datos.")

        except Exception as e:
            print(f"❌ Error durante la extracción: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    extraer_con_interceptor()