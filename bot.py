import json
import os
import sys

# Instalamos la librería de camuflaje TLS dinámicamente si el servidor no la tiene
try:
    from curl_cffi import requests
except ImportError:
    print("⚙️ Instalando módulo de Spoofing TLS (curl_cffi)...")
    os.system(f"{sys.executable} -m pip install curl-cffi")
    from curl_cffi import requests

def extraccion_fantasma():
    print("🤖 Iniciando Ataque Fantasma (Spoofing TLS Chrome 120)...")
    
    url_oficial = "https://laligafantasy.relevo.com/api/v1/master-data"
    
    try:
        print("📡 Conectando a Relevo engañando al cortafuegos de Cloudflare...")
        
        # impersonate="chrome120" es la magia. Copia la huella de red exacta de Chrome.
        response = requests.get(url_oficial, impersonate="chrome120", timeout=30)
        
        if response.status_code == 200:
            datos_api = response.json()
            
            if "players" in datos_api:
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

                # Ordenar por valor de mercado de mayor a menor
                jugadores_procesados.sort(key=lambda x: int(x["precio"].replace(" €", "").replace(".", "")) if isinstance(x.get("precio"), str) and "€" in x["precio"] else 0, reverse=True)
                
                base_datos = {"laliga": {"chollos": jugadores_procesados}}
                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump(base_datos, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡GOLPE MAESTRO! Atravesamos Cloudflare y extrajimos {len(jugadores_procesados)} jugadores.")
            else:
                print("⚠️ El servidor respondió, pero el JSON no contiene jugadores.")
        else:
            print(f"❌ Cloudflare bloqueó el ataque. Código HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en la conexión fantasma: {e}")

if __name__ == "__main__":
    extraccion_fantasma()