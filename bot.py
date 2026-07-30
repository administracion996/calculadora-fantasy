import json
import time
from playwright.sync_api import sync_playwright

def extraer_todo_analitica():
    print("🤖 Lanzando navegador para capturar la base de datos completa de Analítica Fantasy...")
    
    jugadores_capturados = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Interceptamos las respuestas HTTP de la web para cazar el JSON con la lista masiva
        def manejar_respuesta(response):
            nonlocal jugadores_capturados
            try:
                # Buscamos respuestas JSON que contengan datos de jugadores / mercado / chollos
                if "json" in response.headers.get("content-type", ""):
                    data = response.json()
                    lista = []
                    if isinstance(data, list):
                        lista = data
                    elif isinstance(data, dict):
                        lista = data.get("players", data.get("data", data.get("chollos", [])))
                    
                    if isinstance(lista, list) and len(lista) > 5:
                        for item in lista:
                            if isinstance(item, dict) and ("name" in item or "nickname" in item):
                                nombre = item.get("nickname", item.get("name", "Jugador"))
                                equipo = item.get("teamName", item.get("team", {}).get("name", "LaLiga"))
                                pos = str(item.get("position", "MED"))
                                pos_map = {"1": "POR", "2": "DEF", "3": "MED", "4": "DEL"}
                                pos = pos_map.get(pos, pos)
                                
                                precio = item.get("marketValue", item.get("price", 0))
                                incremento = item.get("marketValueIncrement", item.get("priceIncrement", 0))
                                puntos = str(item.get("pointsAverage", item.get("points", 0)))

                                str_subida = f"+ {incremento:,} €".replace(',', '.') if incremento >= 0 else f"- {abs(incremento):,} €".replace(',', '.')

                                jugadores_capturados.append({
                                    "nombre": nombre,
                                    "equipo": equipo,
                                    "pos": pos,
                                    "precio": f"{precio:,} €".replace(',', '.') if isinstance(precio, int) else str(precio),
                                    "subida": str_subida,
                                    "pts": puntos
                                })
            except Exception:
                pass

        # Escuchar todo el tráfico de red de la web
        page.on("response", manejar_respuesta)

        try:
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/mercado", timeout=60000, wait_until="networkidle")
            time.sleep(3)

            # Si no capturó la API de red, hacemos auto-scroll hacia abajo para forzar la carga de más jugadores
            print("📜 Haciendo scroll dinámico para desplegar la lista entera...")
            for _ in range(15):
                page.evaluate("window.scrollBy(0, 1000)")
                time.sleep(0.5)

            # Si la intercepción de red no saltó, extraemos de los componentes DOM de la página limpiando campos
            if not jugadores_capturados:
                print("⚠️ Extrayendo directamente del selector visual de la página...")
                filas = page.query_selector_all("tbody tr")
                for fila in filas:
                    textos = [t.strip() for t in fila.inner_text().split("\n") if t.strip()]
                    if len(textos) >= 3:
                        jugadores_capturados.append({
                            "nombre": textos[0],
                            "equipo": textos[1] if len(textos) > 1 else "LaLiga",
                            "pos": "JUG",
                            "precio": textos[2] if len(textos) > 2 else "0 €",
                            "subida": textos[3] if len(textos) > 3 else "0 €",
                            "pts": textos[4] if len(textos) > 4 else "0.0"
                        })

            # Eliminar duplicados si los hubiera
            jugadores_unicos = {j["nombre"]: j for j in jugadores_capturados}.values()
            lista_final = list(jugadores_unicos)

            if lista_final:
                base_datos = {"laliga": {"chollos": lista_final}}
                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump(base_datos, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡ÉXITO TOTAL! Capturados {len(lista_final)} jugadores reales de Analítica Fantasy.")
            else:
                print("❌ No se pudieron capturar filas.")

        except Exception as e:
            print(f"❌ Error al navegar: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    extraer_todo_analitica()