import json
import urllib.request

def obtener_datos_laliga_oficial():
    print("🤖 Conectando a la API de mercado completa...")
    
    # Endpoint oficial con la base de datos global de jugadores de LaLiga Fantasy
    url = "https://api-fantasy.llf.laliga.com/api/v1/master-data"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                
                # Mapeo de IDs de equipos a sus nombres
                equipos_map = {}
                for team in data.get("teams", []):
                    equipos_map[team.get("id")] = team.get("name", "LaLiga")

                # Mapeo de Posiciones
                pos_map = {1: "POR", 2: "DEF", 3: "MED", 4: "DEL"}

                players_raw = data.get("players", [])
                print(f"📦 Recibidos {len(players_raw)} jugadores de la API.")

                jugadores_procesados = []

                for p in players_raw:
                    nombre = p.get("nickname") or p.get("name") or "Jugador"
                    id_equipo = p.get("teamId")
                    equipo = equipos_map.get(id_equipo, "LaLiga")
                    
                    id_pos = p.get("positionId", 3)
                    pos = pos_map.get(id_pos, "MED")

                    precio_val = p.get("marketValue", 0)
                    subida_val = p.get("marketValueIncrement", 0)
                    pts_val = str(p.get("pointsAverage", 0.0))

                    # Formatear precio y subida
                    str_precio = f"{precio_val:,} €".replace(',', '.')
                    if subida_val >= 0:
                        str_subida = f"+ {subida_val:,} €".replace(',', '.')
                    else:
                        str_subida = f"- {abs(subida_val):,} €".replace(',', '.')

                    jugadores_procesados.append({
                        "nombre": nombre,
                        "equipo": equipo,
                        "pos": pos,
                        "precio": str_precio,
                        "subida": str_subida,
                        "pts": pts_val
                    })

                # Ordenar la lista por valor de mercado descendente
                jugadores_procesados.sort(
                    key=lambda x: int(x["precio"].replace(" €", "").replace(".", "")) if x["precio"] else 0, 
                    reverse=True
                )

                if jugadores_procesados:
                    base_datos = {"laliga": {"chollos": jugadores_procesados}}
                    with open("datos.json", "w", encoding="utf-8") as f:
                        json.dump(base_datos, f, ensure_ascii=False, indent=4)
                    print(f"✅ ¡ÉXITO TOTAL Y DEFINITIVO! Guardados {len(jugadores_procesados)} jugadores reales.")
                else:
                    print("⚠️ No se pudieron mapear los jugadores.")

            else:
                print(f"❌ La API devolvió status {response.status}")

    except Exception as e:
        print(f"❌ Error al consultar la API oficial: {e}")

if __name__ == "__main__":
    obtener_datos_laliga_oficial()