import json
import urllib.request
import re

def extraer_analitica_fantasy_directo():
    print("🤖 Conectando directamente con Analítica Fantasy (Mercado LaLiga)...")

    # URL exacta de Analítica Fantasy para Mercado LaLiga Fantasy
    url = "https://www.analiticafantasy.com/api/players?game=fantasy" 
    
    # Simular navegador real para evitar bloqueos
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Referer': 'https://www.analiticafantasy.com/fantasy-la-liga/mercado',
        'Accept': 'application/json, text/plain, */*'
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=25) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            
            # Si responde la lista de jugadores directamente
            raw_players = res_data if isinstance(res_data, list) else res_data.get("players", res_data.get("data", []))

            jugadores = []

            for p in raw_players:
                nombre = p.get("nickname", p.get("name", "Jugador"))
                equipo = p.get("teamName", p.get("team", {}).get("name", "LaLiga"))
                pos = p.get("position", "MED")
                
                # Valores de mercado de Analítica Fantasy
                precio = p.get("marketValue", p.get("price", 0))
                incremento = p.get("marketValueIncrement", p.get("priceIncrement", 0))
                puntos = str(p.get("pointsAverage", p.get("points", 0)))

                # Formatear la subida/bajada diario
                if incremento >= 0:
                    str_subida = f"+ {incremento:,} €".replace(',', '.')
                else:
                    str_subida = f"- {abs(incremento):,} €".replace(',', '.')

                jugadores.append({
                    "nombre": nombre,
                    "equipo": equipo,
                    "pos": pos,
                    "precio": f"{precio:,} €".replace(',', '.'),
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

            print(f"✅ ¡ÉXITO! Extraídos {len(jugadores)} jugadores directamente de Analítica Fantasy.")

    except Exception as e:
        print(f"⚠️ Error en API directa, activando plan B para Analítica Fantasy: {e}")
        # Si la API privada requiere token, usamos respaldo con scrape de HTML embebido de Analítica
        extraer_html_analitica()

def extraer_html_analitica():
    url = "https://www.analiticafantasy.com/fantasy-la-liga/mercado"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=25) as response:
            html = response.read().decode('utf-8')
            
            # Buscar datos JSON incrustados en la página web de Analítica Fantasy
            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
            if match:
                data_json = json.loads(match.group(1))
                players_raw = data_json.get("props", {}).get("pageProps", {}).get("players", [])
                
                jugadores = []
                for p in players_raw:
                    nombre = p.get("name", "Jugador")
                    equipo = p.get("teamName", "LaLiga")
                    precio = p.get("price", 0)
                    inc = p.get("increment", 0)
                    
                    jugadores.append({
                        "nombre": nombre,
                        "equipo": equipo,
                        "pos": p.get("position", "MED"),
                        "precio": f"{precio:,} €".replace(',', '.'),
                        "subida": f"+ {inc:,} €".replace(',', '.') if inc >= 0 else f"- {abs(inc):,} €".replace(',', '.'),
                        "pts": str(p.get("points", 0))
                    })

                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump({"laliga": {"chollos": jugadores}}, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡ÉXITO PLAN B! {len(jugadores)} jugadores leídos de Analítica Fantasy.")
    except Exception as err:
        print(f"❌ Error final extrayendo Analítica Fantasy: {err}")

if __name__ == "__main__":
    extraer_analitica_fantasy_directo()