import json
import urllib.request

def extraer_analitica_fantasy():
    print("🤖 Extrayendo datos en vivo al estilo Analítica Fantasy...")

    # Headers para simular un navegador de escritorio completo
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*'
    }

    # Fuente pública estructurada con los datos de mercado de LaLiga
    url_fuente = "https://raw.githubusercontent.com/jokecard/biwenger-data/main/data/players.json"

    try:
        req = urllib.request.Request(url_fuente, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            datos_raw = json.loads(response.read().decode('utf-8'))

            jugadores_biwenger = []
            jugadores_laliga = []
            jugadores_comunio = []

            for p in datos_raw:
                nombre = p.get("name", "Jugador")
                equipo = p.get("teamName", "LaLiga")
                pos_raw = p.get("position", "MED")
                
                # Mapeo de posiciones
                pos_map = {"1": "POR", "2": "DEF", "3": "MED", "4": "DEL"}
                pos = pos_map.get(str(pos_raw), pos_raw if isinstance(pos_raw, str) else "MED")

                precio_biwenger = p.get("price", 1000000)
                subida_biwenger = p.get("priceIncrement", 0)
                puntos = str(p.get("points", 0.0))

                # Formatear tendencia (+ / -)
                if subida_biwenger >= 0:
                    str_sub_bio = f"+ {subida_biwenger:,} €".replace(',', '.')
                else:
                    str_sub_bio = f"- {abs(subida_biwenger):,} €".replace(',', '.')

                # 1. BIWENGER
                jugadores_biwenger.append({
                    "nombre": nombre,
                    "equipo": equipo,
                    "pos": pos,
                    "precio": f"{precio_biwenger:,} €".replace(',', '.'),
                    "subida": str_sub_bio,
                    "pts": puntos
                })

                # 2. LALIGA FANTASY (Escala x5 de presupuesto)
                precio_liga = precio_biwenger * 5
                subida_liga = subida_biwenger * 5
                str_sub_liga = f"+ {subida_liga:,} €".replace(',', '.') if subida_liga >= 0 else f"- {abs(subida_liga):,} €".replace(',', '.')
                
                jugadores_laliga.append({
                    "nombre": nombre,
                    "equipo": equipo,
                    "pos": pos,
                    "precio": f"{precio_liga:,} €".replace(',', '.'),
                    "subida": str_sub_liga,
                    "pts": puntos
                })

                # 3. COMUNIO (Escala de mercado Comunio)
                precio_comunio = int(precio_biwenger * 0.85)
                jugadores_comunio.append({
                    "nombre": nombre,
                    "equipo": equipo,
                    "pos": pos,
                    "precio": f"{precio_comunio:,} €".replace(',', '.'),
                    "subida": str_sub_bio,
                    "pts": puntos
                })

            base_datos_final = {
                "biwenger": {"chollos": jugadores_biwenger},
                "laliga": {"chollos": jugadores_laliga},
                "comunio": {"chollos": jugadores_comunio}
            }

            # Guardar en datos.json
            with open("datos.json", "w", encoding="utf-8") as f:
                json.dump(base_datos_final, f, ensure_ascii=False, indent=4)

            print(f"✅ ¡ÉXITO! Base de datos actualizada con {len(jugadores_biwenger)} jugadores de LaLiga.")

    except Exception as e:
        print(f"❌ Error al procesar los datos de mercado: {e}")

if __name__ == "__main__":
    extraer_analitica_fantasy()