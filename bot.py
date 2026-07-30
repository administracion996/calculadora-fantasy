import json
import urllib.request

def extraer_datos_mercado():
    print("🤖 Extrayendo base de datos de mercado para LaLiga Fantasy...")

    # Fuente de respaldo directa y abierta para evitar bloqueos de Cloudflare
    url = "https://raw.githubusercontent.com/jokecard/biwenger-data/main/data/players.json"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            data_raw = json.loads(response.read().decode('utf-8'))

            jugadores = []

            for p in data_raw:
                nombre = p.get("name", "Jugador")
                equipo = p.get("teamName", "LaLiga")
                pos_raw = str(p.get("position", "3"))
                
                pos_map = {"1": "POR", "2": "DEF", "3": "MED", "4": "DEL"}
                pos = pos_map.get(pos_raw, "MED")

                # Valores escalados al mercado de LaLiga Fantasy
                precio_base = p.get("price", 500000) * 5
                subida_base = p.get("priceIncrement", 0) * 5
                puntos = str(p.get("points", 0.0))

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

            base_datos = {
                "laliga": {
                    "chollos": jugadores
                }
            }

            with open("datos.json", "w", encoding="utf-8") as f:
                json.dump(base_datos, f, ensure_ascii=False, indent=4)

            print(f"✅ ¡ÉXITO! Base de datos de mercado guardada con {len(jugadores)} jugadores.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    extraer_datos_mercado()