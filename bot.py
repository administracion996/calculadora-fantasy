import json
import time
from playwright.sync_api import sync_playwright

def extraccion_definitiva_api_relevo():
    print("🤖 Iniciando bypass de descarga (API Oficial Relevo)...")
    jugadores_procesados = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Creamos un contexto de navegador humano
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # 1. Visitar la web oficial de Relevo para que Cloudflare nos valide
            print("🌐 Entrando a Relevo para obtener cookies y pasar Cloudflare...")
            page.goto("https://laligafantasy.relevo.com", wait_until="domcontentloaded", timeout=60000)
            
            # Dejamos 5 segundos para que los scripts antibot hagan su trabajo
            time.sleep(5) 

            # 2. Hacer la petición a la API usando el CONTEXTO, no la página. 
            # Esto evita el error de "chrome-error" porque no hay navegación, es una petición de fondo.
            print("📡 Solicitando datos masivos a la API por debajo del radar...")
            respuesta_api = context.request.get("https://laligafantasy.relevo.com/api/v1/master-data")
            
            if respuesta_api.ok:
                datos = respuesta_api.json()
                
                if "players" in datos:
                    lista_raw = datos["players"]
                    # Mapear los nombres de los equipos
                    equipos_map = {t["id"]: t["name"] for t in datos.get("teams", [])}
                    pos_map = {1: "POR", 2: "DEF", 3: "MED", 4: "DEL"}
                    
                    print(f"📦 ¡DATOS OBTENIDOS! {len(lista_raw)} jugadores encontrados.")

                    for p_item in lista_raw:
                        nombre = p_item.get("nickname") or p.get("name") or "Jugador"
                        eq = equipos_map.get(p_item.get("teamId"), "LaLiga")
                        pos = pos_map.get(p_item.get("positionId", 3), "MED")
                        precio = p_item.get("marketValue", 0)
                        sub = p_item.get("marketValueIncrement", 0)
                        pts = str(p_item.get("pointsAverage", 0.0))

                        # Formateo visual
                        str_precio = f"{precio:,} €".replace(',', '.')
                        str_subida = f"+ {sub:,} €".replace(',', '.') if sub >= 0 else f"- {abs(sub):,} €".replace(',', '.')

                        jugadores_procesados.append({
                            "nombre": nombre, "equipo": eq, "pos": pos,
                            "precio": str_precio, "subida": str_subida, "pts": pts
                        })
            else:
                print(f"⚠️ La API rechazó la petición: {respuesta_api.status} {respuesta_api.status_text}")
                
        except Exception as e:
            print(f"❌ Error crítico: {e}")
        finally:
            browser.close()

        # 3. Guardado en JSON
        if jugadores_procesados:
            # Ordenamos por precio descendente
            jugadores_procesados.sort(key=lambda x: int(x["precio"].replace(" €", "").replace(".", "")) if isinstance(x.get("precio"), str) and "€" in x["precio"] else 0, reverse=True)
            
            base_datos = {"laliga": {"chollos": jugadores_procesados}}
            with open("datos.json", "w", encoding="utf-8") as f:
                json.dump(base_datos, f, ensure_ascii=False, indent=4)
            print(f"✅ ¡MISIÓN CUMPLIDA! Extraídos {len(jugadores_procesados)} jugadores reales.")
        else:
            print("❌ No se capturaron datos.")

if __name__ == "__main__":
    extraccion_definitiva_api_relevo()