import json
import time
from playwright.sync_api import sync_playwright

def extraccion_caballo_de_troya():
    print("🤖 Iniciando Operación Caballo de Troya (Bypass Cloudflare)...")
    jugadores_procesados = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )

        try:
            # 1. Entramos a la web principal oficial para pasar el control de Cloudflare
            print("🌐 Entrando a la web de Relevo para validar la conexión humana...")
            page.goto("https://laligafantasy.relevo.com", wait_until="domcontentloaded", timeout=60000)
            
            # Dejamos 5 segundos de cortesía para que Cloudflare valide el navegador
            time.sleep(5)

            # 2. Inyectamos una petición (fetch) a su propia API desde su consola interna
            print("💉 Inyectando petición a la API maestra desde el interior...")
            datos = page.evaluate("""async () => {
                try {
                    // Al pedir los datos desde su propia web, nos saltamos todos los bloqueos
                    const res = await fetch('https://laligafantasy.relevo.com/api/v1/master-data');
                    if (!res.ok) return null;
                    return await res.json();
                } catch (e) {
                    return null;
                }
            }""")

            if datos and "players" in datos:
                players_raw = datos["players"]
                
                # Extraemos el diccionario de equipos reales
                equipos_map = {}
                for team in datos.get("teams", []):
                    equipos_map[team.get("id")] = team.get("name", "LaLiga")

                pos_map = {1: "POR", 2: "DEF", 3: "MED", 4: "DEL"}
                
                print(f"📦 ¡BINGO! Descargados {len(players_raw)} jugadores masivamente del servidor.")

                for p_item in players_raw:
                    nombre = p_item.get("nickname") or p.get("name") or "Jugador"
                    equipo = equipos_map.get(p_item.get("teamId"), "LaLiga")
                    pos = pos_map.get(p_item.get("positionId", 3), "MED")
                    
                    precio = p_item.get("marketValue", 0)
                    subida = p_item.get("marketValueIncrement", 0)
                    pts = str(p_item.get("pointsAverage", 0.0))

                    # Formateo visual al estilo español
                    str_precio = f"{precio:,} €".replace(',', '.')
                    str_subida = f"+ {subida:,} €".replace(',', '.') if subida >= 0 else f"- {abs(subida):,} €".replace(',', '.')

                    jugadores_procesados.append({
                        "nombre": nombre, "equipo": equipo, "pos": pos,
                        "precio": str_precio, "subida": str_subida, "pts": pts
                    })
            else:
                print("⚠️ El servidor no devolvió el JSON. Posible cambio de URL en la API.")
                
        except Exception as e:
            print(f"❌ Error crítico en la ejecución: {e}")
        finally:
            browser.close()
            
    if jugadores_procesados:
        # Ordenamos la lista por precio descendente para que tenga más lógica
        jugadores_procesados.sort(key=lambda x: int(x["precio"].replace(" €", "").replace(".", "")) if x["precio"] else 0, reverse=True)
        
        base_datos = {"laliga": {"chollos": jugadores_procesados}}
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡ÉXITO DEFINITIVO! Guardados {len(jugadores_procesados)} jugadores reales al instante.")
    else:
        print("❌ Fracaso al capturar datos.")

if __name__ == "__main__":
    extraccion_caballo_de_troya()