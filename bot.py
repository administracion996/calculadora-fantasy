import json
import urllib.request

def obtener_datos_completos():
    print("🤖 Descargando base de datos completa para LaLiga Fantasy...")

    # Conexión directa a la base de datos masiva de LaLiga
    url = "https://api.biwenger.com/v2/competitions/la-liga/data?lang=es&score=1"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            players_dict = res_json.get("data", {}).get("players", {})

            jugadores = []

            for p_id, p in players_dict.items():
                nombre = p.get("name", "Jugador")
                equipo = p.get("teamName", "LaLiga")
                pos_id = p.get("position", 3)
                
                pos_map = {1: "POR", 2: "DEF", 3: "MED", 4: "DEL"}
                pos = pos_map.get(pos_id, "MED")

                # Valores de LaLiga Fantasy (Presupuestos x5)
                precio_base = p.get("price", 500000) * 5
                subida_base = p.get("priceIncrement", 0) * 5
                puntos = str(p.get("fitness", [0])[-1] if isinstance(p.get("fitness"), list) and p.get("fitness") else 0)

                if subida_base >= 0:
                    str_subida = f"+ {subida_base:,} €".replace(',', '.')
                else:
                    str_subida = f"- {abs(subida_base):,} €".replace(',', '.')

                jugadores.append({
                    "nombre": nombre,
                    "equipo": equipo,
                    "pos": pos,
                    "precio": f"{precio_base:,} €".replace(',', '.'),
                    "subida": str_subida,
                    "pts": puntos
                })

            datos_finales = {
                "laliga": {
                    "chollos": jugadores
                }
            }

            with open("datos.json", "w", encoding="utf-8") as f:
                json.dump(datos_finales, f, ensure_ascii=False, indent=4)

            print(f"✅ ¡ÉXITO! {len(jugadores)} jugadores reales guardados.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    obtener_datos_completos()