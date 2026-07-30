import json
from seleniumbase import SB

def extraccion_uc_mode():
    print("🤖 Desplegando arma definitiva: SeleniumBase UC (Undetected ChromeDriver)...")
    jugadores_procesados = []

    # Iniciamos el navegador en modo indetectable (UC)
    # Headless=True asegura que corra en los servidores de GitHub sin pantalla
    with SB(uc=True, headless=True) as sb:
        try:
            print("🌐 Abriendo túnel hacia la API oficial de Relevo...")
            
            # uc_open_with_reconnect es la función mágica que engaña a Cloudflare Turnstile
            sb.driver.uc_open_with_reconnect("https://laligafantasy.relevo.com/api/v1/master-data", reconnect_time=6)
            
            # Le damos 5 segundos al navegador para resolver el CAPTCHA invisible
            sb.sleep(5)
            
            print("🔍 Extrayendo el código puro...")
            # Extraemos el texto que el navegador ve en la pantalla blanca
            texto = sb.get_text("body")
            
            datos = json.loads(texto)
            
            if "players" in datos:
                lista_raw = datos["players"]
                equipos_map = {t["id"]: t["name"] for t in datos.get("teams", [])}
                pos_map = {1: "POR", 2: "DEF", 3: "MED", 4: "DEL"}
                
                print(f"📦 ¡DATOS OBTENIDOS! Se han cazado {len(lista_raw)} jugadores.")
                
                for p_item in lista_raw:
                    nombre = p_item.get("nickname") or p.get("name") or "Jugador"
                    eq = equipos_map.get(p_item.get("teamId"), "LaLiga")
                    pos = pos_map.get(p_item.get("positionId", 3), "MED")
                    precio = p_item.get("marketValue", 0)
                    sub = p_item.get("marketValueIncrement", 0)
                    pts = str(p_item.get("pointsAverage", 0.0))

                    # Formateo
                    str_precio = f"{precio:,} €".replace(',', '.')
                    str_subida = f"+ {sub:,} €".replace(',', '.') if sub >= 0 else f"- {abs(sub):,} €".replace(',', '.')

                    jugadores_procesados.append({
                        "nombre": nombre, "equipo": eq, "pos": pos,
                        "precio": str_precio, "subida": str_subida, "pts": pts
                    })
                    
        except Exception as e:
            print(f"❌ Error durante el asalto: {e}")

    # Guardado de datos
    if jugadores_procesados:
        # Ordenamos la tabla de más caro a más barato
        jugadores_procesados.sort(key=lambda x: int(x["precio"].replace(" €", "").replace(".", "")) if isinstance(x.get("precio"), str) and "€" in x["precio"] else 0, reverse=True)
        
        base_datos = {"laliga": {"chollos": jugadores_procesados}}
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡GOLPE MAESTRO! Se han guardado {len(jugadores_procesados)} jugadores.")
    else:
        print("❌ El escudo de Cloudflare aguantó. No se capturaron datos.")

if __name__ == "__main__":
    extraccion_uc_mode()