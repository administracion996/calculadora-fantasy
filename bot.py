import json
import requests

def obtener_plantilla_completa():
    print("🤖 Extrayendo la base de datos masiva de LaLiga Fantasy...")

    url = "https://api.biwenger.com/v2/competitions/la-liga/data?lang=es&score=1"
    
    # Headers modernos para evitar bloqueos y cortes de conexión
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Connection': 'keep-alive'
    }

    try:
        # Petición HTTP robusta con soporte SSL completo
        response = requests.get(url, headers=headers, timeout=25)
        response.raise_for_status()
        
        res_json = response.json()
        data = res_json.get("data", {})
        players_dict = data.get("players", {})
        teams_dict = data.get("teams", {})

        jugadores = []

        for p_id, p in players_dict.items():
            nombre = p.get("name", "Jugador")
            team_id = str(p.get("teamID", ""))
            equipo_info = teams_dict.get(team_id, {})
            equipo = equipo_info.get("name", "LaLiga")

            pos_id = p.get("position", 3)
            pos_map = {1: "POR", 2: "DEF", 3: "MED", 4: "DEL"}
            pos = pos_map.get(pos_id, "MED")

            # Precios de LaLiga Fantasy (Escala x5)
            precio_base = p.get("price", 500000) * 5
            subida_base = p.get("priceIncrement", 0) * 5
            
            fitness = p.get("fitness", [])
            puntos = str(fitness[-1]) if isinstance(fitness, list) and len(fitness) > 0 else "0.0"

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

        # Sobrescribir datos.json con la lista completa
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)

        print(f"✅ ¡ÉXITO COMPLETADO! Guardados {len(jugadores)} jugadores reales.")

    except Exception as e:
        print(f"❌ Error al conectar: {e}")

if __name__ == "__main__":
    obtener_plantilla_completa()