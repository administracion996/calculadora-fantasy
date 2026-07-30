import json
import time
from playwright.sync_api import sync_playwright

def extraer_con_buscador():
    print("🤖 Conectando a Analítica Fantasy mediante interceptor de búsqueda...")
    
    jugadores_totales = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Interceptamos cualquier llamada JSON a la base de datos interna de la web
        def capturar_json(response):
            nonlocal jugadores_totales
            try:
                url = response.url
                if "json" in response.headers.get("content-type", "") or "api" in url:
                    data = response.json()
                    lista = []
                    if isinstance(data, list):
                        lista = data
                    elif isinstance(data, dict):
                        lista = data.get("players", data.get("data", data.get("jugadores", [])))

                    if isinstance(lista, list) and len(lista) > 10:
                        print(f"🎯 Capturada lista masiva de red con {len(lista)} elementos!")
                        for p_item in lista:
                            nombre = p_item.get("nickname", p_item.get("name", ""))
                            if not nombre:
                                continue
                            
                            equipo = p_item.get("teamName", p_item.get("team", {}).get("name", "LaLiga"))
                            pos = str(p_item.get("position", "MED"))
                            pos_map = {"1": "POR", "2": "DEF", "3": "MED", "4": "DEL"}
                            pos = pos_map.get(pos, pos)
                            
                            precio = p_item.get("marketValue", p_item.get("price", 0))
                            incremento = p_item.get("marketValueIncrement", p_item.get("priceIncrement", 0))
                            puntos = str(p_item.get("pointsAverage", p_item.get("points", 0)))

                            if isinstance(incremento, (int, float)):
                                str_subida = f"+ {incremento:,} €".replace(',', '.') if incremento >= 0 else f"- {abs(incremento):,} €".replace(',', '.')
                            else:
                                str_subida = str(incremento)

                            str_precio = f"{precio:,} €".replace(',', '.') if isinstance(precio, (int, float)) else str(precio)

                            jugadores_totales.append({
                                "nombre": nombre,
                                "equipo": equipo,
                                "pos": pos,
                                "precio": str_precio,
                                "subida": str_subida,
                                "pts": puntos
                            })
            except Exception:
                pass

        page.on("response", capturar_json)

        try:
            # 1. Cargar la página
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/mercado", timeout=60000, wait_until="networkidle")
            time.sleep(3)

            # 2. Escribir una letra en el campo de búsqueda ("Buscar jugador...") para disparar la consulta masiva a su API
            buscadores = page.query_selector_all("input[placeholder*='Buscar'], input[type='text']")
            for b in buscadores:
                if b.is_visible():
                    b.fill("a")  # Al buscar la letra 'a', la API devuelve prácticamente todos los jugadores de LaLiga
                    time.sleep(2)
                    b.fill("")   # Borramos para recargar estado completo
                    time.sleep(2)
                    break

            # Si el interceptor atrapó los datos completos
            if len(jugadores_totales) > 10:
                print(f"✅ ¡ÉXITO! Se han extraído {len(jugadores_totales)} jugadores mediante el interceptor.")
            else:
                # Fallback: intentar leer todas las filas del DOM tras forzar la carga del buscador
                print("⚠️ Extrayendo del DOM tras disparar la búsqueda...")
                filas = page.query_selector_all("tbody tr")
                dict_temp = {}
                for fila in filas:
                    celdas = fila.query_selector_all("td")
                    if len(celdas) >= 4:
                        nom = celdas[0].inner_text().strip().split("\n")[0]
                        if nom and nom[0].isdigit():
                            partes = nom.split()
                            if len(partes) > 1 and partes[0].isdigit():
                                nom = " ".join(partes[1:])

                        eq = celdas[1].inner_text().strip().split("\n")[0] if len(celdas) > 1 else "LaLiga"
                        val = celdas[2].inner_text().strip().split("\n")[0] if len(celdas) > 2 else "0 €"
                        sub = celdas[3].inner_text().strip().split("\n")[0] if len(celdas) > 3 else "0 €"
                        pt = celdas[4].inner_text().strip().split("\n")[0] if len(celdas) > 4 else "0.0"

                        if nom:
                            dict_temp[nom] = {
                                "nombre": nom,
                                "equipo": eq,
                                "pos": "JUG",
                                "precio": val,
                                "subida": sub,
                                "pts": pt
                            }
                jugadores_totales = list(dict_temp.values())

            if jugadores_totales:
                # Quitar duplicados por nombre
                unicos = {j["nombre"]: j for j in jugadores_totales}.values()
                final = list(unicos)

                base_datos = {"laliga": {"chollos": final}}
                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump(base_datos, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡ÉXITO FINAL! Guardados {len(final)} jugadores reales.")
            else:
                print("❌ No se obtuvieron jugadores.")

        except Exception as e:
            print(f"❌ Error durante la extracción: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    extraer_con_buscador()