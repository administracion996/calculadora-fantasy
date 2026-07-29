import json
import urllib.request

def obtener_datos_reales():
    print("🤖 Descargando base de datos real de LaLiga...")

    # URL pública de datos Fantasy de LaLiga sin bloqueos de Cloudflare
    url = "https://raw.githubusercontent.com/jokecard/biwenger-data/main/data/players.json"

    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    try:
        with urllib.request.urlopen(req) as response:
            raw_data = json.loads(response.read().decode())
            
            jugadores_biwenger = []
            jugadores_laliga = []
            jugadores_comunio = []

            # Procesar lista de jugadores reales
            for item in raw_data:
                nombre = item.get("name", "Jugador")
                equipo = item.get("teamName", "LaLiga")
                pos = item.get("position", "MED")
                precio_base = item.get("price", 1000000)
                change = item.get("priceIncrement", 0)

                # Formatear valores
                str_subida = f"+ {change:,} €".replace(',', '.') if change >= 0 else f"- {abs(change):,} €".replace(',', '.')
                
                # Datos para Biwenger
                jugadores_biwenger.append({
                    "nombre": nombre,
                    "equipo": equipo,
                    "pos": pos,
                    "precio": f"{precio_base:,} €".replace(',', '.'),
                    "subida": str_subida,
                    "pts": str(item.get("points", 0))
                })

                # Datos para LaLiga Fantasy (Escala x5 de presupuesto)
                precio_liga = precio_base * 5
                jugadores_laliga.append({
                    "nombre": nombre,
                    "equipo": equipo,
                    "pos": pos,
                    "precio": f"{precio_liga:,} €".replace(',', '.'),
                    "subida": f"+ {change*5:,} €".replace(',', '.') if change >= 0 else f"- {abs(change)*5:,} €".replace(',', '.'),
                    "pts": str(item.get("points", 0))
                })

                # Datos para Comunio
                precio_comunio = int(precio_base * 0.8)
                jugadores_comunio.append({
                    "nombre": nombre,
                    "equipo": equipo,
                    "pos": pos,
                    "precio": f"{precio_comunio:,} €".replace(',', '.'),
                    "subida": str_subida,
                    "pts": str(item.get("points", 0))
                })

            datos_finales = {
                "biwenger": {"chollos": jugadores_biwenger},
                "laliga": {"chollos": jugadores_laliga},
                "comunio": {"chollos": jugadores_comunio}
            }

            with open("datos.json", "w", encoding="utf-8") as f:
                json.dump(datos_finales, f, ensure_ascii=False, indent=4)

            print(f"✅ ¡ÉXITO! Se han descargado {len(jugadores_biwenger)} JUGADORES REALES.")

    except Exception as e:
        print(f"❌ Error al obtener los datos: {e}")

if __name__ == "__main__":
    obtener_datos_reales()
    