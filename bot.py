import json
import time
from playwright.sync_api import sync_playwright

def extraccion_json_directo():
    print("🤖 Navegando DIRECTAMENTE al archivo JSON (Bypass absoluto)...")
    jugadores_procesados = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # El User-Agent es vital para que Cloudflare nos trate como a un humano
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )

        try:
            # 1. Navegamos a las URLs de las APIs como si fueran webs normales.
            # El navegador pintará el JSON en bruto en la pantalla.
            urls_api = [
                "https://api.analiticafantasy.com/api/v1/players",
                "https://api.analiticafantasy.com/api/players",
                "https://laligafantasy.relevo.com/api/v1/master-data"
            ]

            datos = None

            for url in urls_api:
                print(f"🌐 Navegando a: {url}")
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(5) # Esperar a que pase el check de Cloudflare invisible

                    # Extraemos todo el texto visible (el navegador pinta el JSON en el body)
                    contenido = page.locator("body").inner_text().strip()
                    
                    if contenido.startswith("{") or contenido.startswith("["):
                        datos = json.loads(contenido)
                        print("🎯 ¡JSON capturado de la pantalla con éxito!")
                        break
                except Exception as e:
                    print(f"⚠️ No se pudo extraer de {url}: {e}")

            # 2. Procesamos el JSON extraído
            if datos:
                # Si nos devolvió el formato de Relevo (diccionario con "players" y "teams")
                if isinstance(datos, dict) and "players" in datos:
                    lista_raw = datos["players"]
                    equipos_map = {t["id"]: t["name"] for t in datos.get("teams", [])}
                    
                    for p_item in lista_raw:
                        nombre = p_item.get("nickname") or p.get("name") or "Jugador"
                        eq = equipos_map.get(p_item.get("teamId"), "LaLiga")
                        pos_id = p_item.get("positionId", 3)
                        pos = {1: "POR", 2: "DEF", 3: "MED", 4: "DEL"}.get(pos_id, "MED")
                        precio = p_item.get("marketValue", 0)
                        sub = p_item.get("marketValueIncrement", 0)
                        pts = str(p_item.get("pointsAverage", 0.0))

                        jugadores_procesados.append({
                            "nombre": nombre, "equipo": eq, "pos": pos,
                            "precio": f"{precio:,} €".replace(',', '.'),
                            "subida": f"+ {sub:,} €".replace(',', '.') if sub >= 0 else f"- {abs(sub):,} €".replace(',', '.'),
                            "pts": pts
                        })
                
                # Si nos devolvió el formato de Analítica Fantasy (lista directa)
                elif isinstance(datos, list):
                    for p_item in datos:
                        nombre = p_item.get("nickname") or p.get("name", "")
                        if not nombre: continue
                        eq = p_item.get("teamName", "LaLiga")
                        pos = str(p_item.get("position", "MED"))
                        pos = {"1": "POR", "2": "DEF", "3": "MED", "4": "DEL"}.get(pos, pos)
                        precio = p_item.get("marketValue", p_item.get("price", 0))
                        sub = p_item.get("marketValueIncrement", p_item.get("priceIncrement", 0))
                        pts = str(p_item.get("pointsAverage", p_item.get("points", 0.0)))
                        
                        jugadores_procesados.append({
                            "nombre": nombre, "equipo": eq, "pos": pos,
                            "precio": f"{precio:,} €".replace(',', '.'),
                            "subida": f"+ {sub:,} €".replace(',', '.') if sub >= 0 else f"- {abs(sub):,} €".replace(',', '.'),
                            "pts": pts
                        })

        except Exception as e:
            print(f"❌ Error crítico: {e}")
        finally:
            browser.close()

        # 3. Guardado
        if jugadores_procesados:
            # Ordenar por precio descendente para mejor organización
            jugadores_procesados.sort(key=lambda x: int(x["precio"].replace(" €", "").replace(".", "")) if isinstance(x.get("precio"), str) and "€" in x["precio"] else 0, reverse=True)
            base_datos = {"laliga": {"chollos": jugadores_procesados}}
            with open("datos.json", "w", encoding="utf-8") as f:
                json.dump(base_datos, f, ensure_ascii=False, indent=4)
            print(f"✅ ¡MISIÓN CUMPLIDA! Extraídos {len(jugadores_procesados)} jugadores reales.")
        else:
            print("❌ No se capturaron datos.")

if __name__ == "__main__":
    extraccion_json_directo()