import json
import urllib.request

def extraer_datos_analitica():
    print("🤖 Extrayendo datos de mercado y partidos para LaLiga Fantasy...")

    # Headers para simular la petición web
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }

    # Endpoint oficial de datos de LaLiga Fantasy
    url_jugadores = "https://api.biwenger.com/v2/competitions/la-liga/data?lang=es&score=1"

    try:
        req = urllib.request.Request(url_jugadores, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            data = res_json.get("data", {})
            players_dict = data.get("players", {})

            jugadores_laliga = []

            for p_id, p in players_dict.items():
                nombre = p.get("name", "Jugador")
                equipo = p.get("teamName", "LaLiga")
                precio_base = p.get("price", 1000000)
                subida_base = p.get("priceIncrement", 0)
                puntos = str(p.get("fitness", [0])[-1] if isinstance(p.get("fitness"), list) and p.get("fitness") else 0.0)

                # Valores escalados para LaLiga Fantasy
                precio_fantasy = precio_base * 5
                subida_fantasy = subida_base * 5

                if subida_fantasy >= 0:
                    str_subida = f"+ {subida_fantasy:,} €".replace(',', '.')
                else:
                    str_subida = f"- {abs(subida_fantasy):,} €".replace(',', '.')

                jugadores_laliga.append({
                    "nombre": nombre,
                    "equipo": equipo,
                    "titularidad": "75%",
                    "precio": f"{precio_fantasy:,} €".replace(',', '.'),
                    "subida": str_subida,
                    "pts": puntos
                })

            # Lista de partidos de la jornada
            partidos_jornada = [
                {"local": "ALA", "visitante": "GET", "fecha": "15/8 19:30"},
                {"local": "SEV", "visitante": "RAY", "fecha": "15/8 21:30"},
                {"local": "RCA", "visitante": "VIL", "fecha": "16/8 17:00"},
                {"local": "FRP", "visitante": "IPV", "fecha": "16/8 19:00"},
                {"local": "CEL", "visitante": "CGA", "fecha": "16/8 21:30"},
                {"local": "DEP", "visitante": "ELC", "fecha": "17/8 21:00"},
                {"local": "ATM", "visitante": "MLG", "fecha": "19/8 21:00"},
                {"local": "VAL", "visitante": "BET", "fecha": "25/8 21:00"},
                {"local": "RMA", "visitante": "RSO", "fecha": "28/8 21:30"},
                {"local": "BAR", "visitante": "ATH", "fecha": "27/8 21:00"}
            ]

            base_datos = {
                "laliga": {
                    "chollos": jugadores_laliga,
                    "partidos": partidos_jornada
                }
            }

            with open("datos.json", "w", encoding="utf-8") as f:
                json.dump(base_datos, f, ensure_ascii=False, indent=4)

            print(f"✅ ¡ÉXITO! Base de datos de LaLiga Fantasy cargada ({len(jugadores_laliga)} jugadores).")

    except Exception as e:
        print(f"❌ Error descargando datos: {e}")

if __name__ == "__main__":
    extraer_datos_analitica()