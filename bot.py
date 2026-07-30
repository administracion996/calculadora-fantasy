import json
import urllib.request

def actualizar_base_datos_diaria():
    print("🤖 Conectando con la fuente de datos Fantasy nocturna...")

    # URL oficial directa de datos de mercado y plantillas
    url = "https://raw.githubusercontent.com/jokecard/biwenger-data/main/data/players.json"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            data_raw = json.loads(response.read().decode('utf-8'))

            list_biwenger = []
            list_laliga = []
            list_comunio = []

            for p in data_raw:
                nombre = p.get("name", "Jugador")
                equipo = p.get("teamName", "Sin equipo")
                pos_raw = str(p.get("position", "3"))
                
                # Mapeo de posiciones estándar
                pos_map = {"1": "POR", "2": "DEF", "3": "MED", "4": "DEL"}
                pos = pos_map.get(pos_raw, "MED")

                precio_base = p.get("price", 500000)
                subida_base = p.get("priceIncrement", 0)
                puntos = str(p.get("points", 0.0))

                # Formatear la subida/bajada diario
                if subida_base >= 0:
                    str_subida = f"+ {subida_base:,} €".replace(',', '.')
                else:
                    str_subida = f"- {abs(subida_base):,} €".replace(',', '.')

                # 1. Base de datos Biwenger
                list_biwenger.append({
                    "nombre": nombre,
                    "equipo": equipo,
                    "pos": pos,
                    "precio": f"{precio_base:,} €".replace(',', '.'),
                    "subida": str_subida,
                    "pts": puntos
                })

                # 2. Base de datos LaLiga Fantasy
                precio_liga = precio_base * 5
                subida_liga = subida_base * 5
                str_sub_liga = f"+ {subida_liga:,} €".replace(',', '.') if subida_liga >= 0 else f"- {abs(subida_liga):,} €".replace(',', '.')

                list_laliga.append({
                    "nombre": nombre,
                    "equipo": equipo,
                    "pos": pos,
                    "precio": f"{precio_liga:,} €".replace(',', '.'),
                    "subida": str_sub_liga,
                    "pts": puntos
                })

                # 3. Base de datos Comunio
                precio_comunio = int(precio_base * 0.85)
                list_comunio.append({
                    "nombre": nombre,
                    "equipo": equipo,
                    "pos": pos,
                    "precio": f"{precio_comunio:,} €".replace(',', '.'),
                    "subida": str_subida,
                    "pts": puntos
                })

            base_datos = {
                "biwenger": {"chollos": list_biwenger},
                "laliga": {"chollos": list_laliga},
                "comunio": {"chollos": list_comunio}
            }

            # Escribir el archivo datos.json actualizado
            with open("datos.json", "w", encoding="utf-8") as f:
                json.dump(base_datos, f, ensure_ascii=False, indent=4)

            print(f"✅ ¡ÉXITO NOCTURNO! {len(list_biwenger)} jugadores de LaLiga actualizados.")

    except Exception as e:
        print(f"❌ Error durante la actualización nocturna: {e}")

if __name__ == "__main__":
    actualizar_base_datos_diaria()