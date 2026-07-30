import json
import time
from playwright.sync_api import sync_playwright

def extraer_por_intercepcion_pura():
    print("🤖 Iniciando escuchador de red para Analítica Fantasy...")
    
    jugadores_dict = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Esta función examina absolutamente TODAS las respuestas del servidor
        def procesar_respuesta(response):
            try:
                # Si la respuesta es JSON o viene de una API
                url = response.url.lower()
                content_type = response.headers.get("content-type", "").lower()

                if "json" in content_type or "api" in url or "data" in url:
                    datos = response.json()
                    
                    # Buscar arrays en cualquier nivel del JSON devuelto
                    candidatos = []
                    if isinstance(datos, list):
                        candidatos = datos
                    elif isinstance(datos, dict):
                        for k, v in datos.items():
                            if isinstance(v, list) and len(v) > 5:
                                candidatos = v
                                break

                    # Si encontramos una lista de objetos que parecen jugadores
                    for item in candidatos:
                        if isinstance(item, dict):
                            nombre = item.get("nickname") or item.get("name") or item.get("nombre")
                            if not nombre:
                                continue

                            equipo = item.get("teamName") or item.get("team", {}).get("name") if isinstance(item.get("team"), dict) else item.get("equipo", "LaLiga")
                            pos = str(item.get("position", "MED"))
                            pos_map = {"1": "POR", "2": "DEF", "3": "MED", "4": "DEL"}
                            pos = pos_map.get(pos, pos)

                            precio = item.get("marketValue") or item.get("price") or item.get("precio", 0)
                            incremento = item.get("marketValueIncrement") or item.get("priceIncrement") or item.get("subida", 0)
                            pts = str(item.get("pointsAverage") or item.get("points") or item.get("pts", 0))

                            str_precio = f"{precio:,} €".replace(',', '.') if isinstance(precio, (int, float)) else str(precio)
                            
                            if isinstance(incremento, (int, float)):
                                str_subida = f"+ {incremento:,} €".replace(',', '.') if incremento >= 0 else f"- {abs(incremento):,} €".replace(',', '.')
                            else:
                                str_subida = str(incremento)

                            jugadores_dict[nombre] = {
                                "nombre": nombre,
                                "equipo": equipo,
                                "pos": pos,
                                "precio": str_precio,
                                "subida": str_subida,
                                "pts": pts
                            }
            except Exception:
                pass

        # Conectar el escuchador de respuestas
        page.on("response", procesar_respuesta)

        try:
            # 1. Navegar a la sección principal de Mercado
            print("🌐 Cargando la web y escuchando peticiones de fondo...")
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/mercado", timeout=60000, wait_until="networkidle")
            time.sleep(5)

            # 2. Navegar a otras pestañas internas si existen para forzar a la web a pedir más JSONs
            urls_secundarias = [
                "https://www.analiticafantasy.com/fantasy-la-liga/jugadores",
                "https://www.analiticafantasy.com/fantasy-la-liga/chollos"
            ]

            for u in urls_secundarias:
                if len(jugadores_dict) < 50:
                    try:
                        print(f"🔗 Visitando sección auxiliar: {u}")
                        page.goto(u, timeout=30000, wait_until="networkidle")
                        time.sleep(4)
                    except Exception:
                        pass

            resultado = list(jugadores_dict.values())

            if resultado:
                base_datos = {"laliga": {"chollos": resultado}}
                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump(base_datos, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡ÉXITO! Se han capturado {len(resultado)} jugadores interceptando la red.")
            else:
                print("❌ No se detectaron paquetes de datos de jugadores en la red.")

        except Exception as e:
            print(f"❌ Error durante el proceso: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    extraer_por_intercepcion_pura()