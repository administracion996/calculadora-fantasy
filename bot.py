import json
import time
from playwright.sync_api import sync_playwright

def extraer_base_de_datos_oculta():
    print("🤖 Iniciando navegador Chrome anti-bloqueos...")
    jugadores_totales = []

    with sync_playwright() as p:
        # Lanzamos Chromium real para saltarnos el bloqueo de Cloudflare/Antibots
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            print("🌐 Visitando el directorio COMPLETO de jugadores...")
            # Vamos a la página genérica de Jugadores, no a la de mercado que limita a 10
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/jugadores", timeout=60000, wait_until="domcontentloaded")
            time.sleep(3)

            print("🔍 Extrayendo la base de datos de la memoria interna...")
            # Extraemos el bloque JSON oculto que usa el framework (Next.js) para pintar la web
            next_data_json = page.locator("#__NEXT_DATA__").inner_text()
            datos = json.loads(next_data_json)

            # Buscador recursivo: busca cualquier lista dentro de las tripas de la web que tenga más de 300 elementos
            def buscar_lista_masiva(obj):
                if isinstance(obj, list) and len(obj) > 300:
                    if isinstance(obj[0], dict) and ("nickname" in obj[0] or "name" in obj[0] or "slug" in obj[0]):
                        return obj
                elif isinstance(obj, dict):
                    for k, v in obj.items():
                        res = buscar_lista_masiva(v)
                        if res: return res
                elif isinstance(obj, list):
                    for item in obj:
                        res = buscar_lista_masiva(item)
                        if res: return res
                return None

            lista_jugadores = buscar_lista_masiva(datos)

            if lista_jugadores:
                print(f"🎯 ¡Bingo! Encontrada lista masiva con {len(lista_jugadores)} jugadores.")
                for p_item in lista_jugadores:
                    nombre = p_item.get("nickname", p_item.get("name", ""))
                    if not nombre: continue

                    equipo = p_item.get("teamName", p_item.get("team", {}).get("name", "LaLiga"))
                    pos = str(p_item.get("position", "MED"))
                    pos_map = {"1": "POR", "2": "DEF", "3": "MED", "4": "DEL"}
                    pos = pos_map.get(pos, pos)

                    precio = p_item.get("marketValue", p_item.get("price", 0))
                    subida = p_item.get("marketValueIncrement", p_item.get("priceIncrement", 0))
                    pts = str(p_item.get("pointsAverage", p_item.get("points", "0.0")))

                    str_precio = f"{precio:,} €".replace(',', '.') if isinstance(precio, (int, float)) else str(precio)
                    
                    if isinstance(subida, (int, float)):
                        str_subida = f"+ {subida:,} €".replace(',', '.') if subida >= 0 else f"- {abs(subida):,} €".replace(',', '.')
                    else:
                        str_subida = str(subida)

                    jugadores_totales.append({
                        "nombre": nombre,
                        "equipo": equipo,
                        "pos": pos,
                        "precio": str_precio,
                        "subida": str_subida,
                        "pts": pts
                    })
            else:
                print("⚠️ No se encontró la lista en el JSON interno.")

        except Exception as e:
            print(f"❌ Error durante el proceso: {e}")
        finally:
            browser.close()

    if jugadores_totales:
        base_datos = {"laliga": {"chollos": jugadores_totales}}
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡ÉXITO TOTAL Y DEFINITIVO! Guardados {len(jugadores_totales)} jugadores sin bloqueos.")
    else:
        print("❌ Fracaso al capturar datos.")

if __name__ == "__main__":
    extraer_base_de_datos_oculta()