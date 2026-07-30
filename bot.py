import json
import urllib.request
import urllib.parse
import ssl

def extraccion_definitiva_proxies():
    print("🤖 Iniciando bypass de IP (Estrategia de Proxies Libres)...")
    
    url_oficial = "https://laligafantasy.relevo.com/api/v1/master-data"
    url_codificada = urllib.parse.quote(url_oficial, safe="")

    # Túneles proxy para camuflar la IP de GitHub Actions
    proxies = [
        f"https://api.allorigins.win/raw?url={url_codificada}",
        f"https://api.codetabs.com/v1/proxy?quest={url_oficial}",
        f"https://corsproxy.io/?{url_codificada}"
    ]

    # Desactivar verificación estricta de SSL para evitar problemas con los proxies
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }

    datos_api = None

    for proxy in proxies:
        print(f"🌐 Probando túnel proxy: {proxy.split('/')[2]}")
        try:
            req = urllib.request.Request(proxy, headers=headers)
            with urllib.request.urlopen(req, timeout=20, context=ctx) as response:
                if response.status == 200:
                    texto = response.read().decode('utf-8')
                    try:
                        # Si podemos convertir el texto a JSON, hemos atravesado Cloudflare
                        datos_api = json.loads(texto)
                        if "players" in datos_api:
                            print("🎯 ¡BINGO! Conexión limpia y datos extraídos con éxito.")
                            break
                    except json.JSONDecodeError:
                        print("⚠️ El proxy devolvió HTML (bloqueado por Cloudflare). Pasando al siguiente...")
        except Exception as e:
            print(f"⚠️ Fallo en el túnel: {e}")

    # Procesamiento de datos si hemos tenido éxito
    if datos_api and "players" in datos_api:
        lista_raw = datos_api["players"]
        equipos_map = {t["id"]: t["name"] for t in datos_api.get("teams", [])}
        pos_map = {1: "POR", 2: "DEF", 3: "MED", 4: "DEL"}
        
        jugadores_procesados = []
        
        for p_item in lista_raw:
            nombre = p_item.get("nickname") or p.get("name") or "Jugador"
            eq = equipos_map.get(p_item.get("teamId"), "LaLiga")
            pos = pos_map.get(p_item.get("positionId", 3), "MED")
            precio = p_item.get("marketValue", 0)
            sub = p_item.get("marketValueIncrement", 0)
            pts = str(p_item.get("pointsAverage", 0.0))

            str_precio = f"{precio:,} €".replace(',', '.')
            str_subida = f"+ {sub:,} €".replace(',', '.') if sub >= 0 else f"- {abs(sub):,} €".replace(',', '.')

            jugadores_procesados.append({
                "nombre": nombre, "equipo": eq, "pos": pos,
                "precio": str_precio, "subida": str_subida, "pts": pts
            })

        # Ordenar de los más caros a los más baratos
        jugadores_procesados.sort(key=lambda x: int(x["precio"].replace(" €", "").replace(".", "")) if isinstance(x.get("precio"), str) and "€" in x["precio"] else 0, reverse=True)
        
        base_datos = {"laliga": {"chollos": jugadores_procesados}}
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡MISIÓN CUMPLIDA! Extraídos {len(jugadores_procesados)} jugadores reales.")
    else:
        print("❌ Ningún proxy pudo atravesar Cloudflare hoy. Fin del intento.")

if __name__ == "__main__":
    extraccion_definitiva_proxies()