import json
import cloudscraper

def extraer_analitica_api():
    print("🤖 Conectando a la API de www.analiticafantasy.com...")
    
    # URL de la API interna de Analítica Fantasy para la sección de Mercado de LaLiga Fantasy
    url_api = "https://www.analiticafantasy.com/api/chollos?game=relevo"
    url_api_secundaria = "https://www.analiticafantasy.com/api/market?game=relevo"
    
    # Engañar a Cloudflare simulando un navegador navegando en la web
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
    
    jugadores_raw = []
    
    # Intentar endpoint principal de Analítica Fantasy
    try:
        response = scraper.get(url_api, timeout=25)
        if response.status_code == 200:
            res_data = response.json()
            jugadores_raw = res_data if isinstance(res_data, list) else res_data.get("players", res_data.get("data", []))
    except Exception as e:
        print(f"Probando endpoint secundario por: {e}")

    # Si el primer endpoint no responde, probar el de mercado
    if not jugadores_raw:
        try:
            response = scraper.get(url_api_secundaria, timeout=25)
            if response.status_code == 200:
                res_data = response.json()
                jugadores_raw = res_data if isinstance(res_data, list) else res_data.get("players", res_data.get("data", []))
        except Exception as e:
            print(f"Error en endpoint secundario: {e}")

    # Si la API privada no devuelve JSON directo, raspamos las peticiones internas
    if not jugadores_raw:
        print("❌ No se pudieron obtener los datos de la API de Analítica Fantasy.")
        return

    jugadores = []
    for p in jugadores_raw:
        nombre = p.get("nickname", p.get("name", "Jugador"))
        equipo = p.get("teamName", p.get("team", {}).get("name", "LaLiga"))
        pos = str(p.get("position", "MED"))
        
        pos_map = {"1": "POR", "2": "DEF", "3": "MED", "4": "DEL"}
        pos = pos_map.get(pos, pos)
        
        precio = p.get("marketValue", p.get("price", 0))
        incremento = p.get("marketValueIncrement", p.get("priceIncrement", 0))
        puntos = str(p.get("pointsAverage", p.get("points", 0)))
        
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
        
    base_datos = {"laliga": {"chollos": jugadores}}
    
    with open("datos.json", "w", encoding="utf-8") as f:
        json.dump(base_datos, f, ensure_ascii=False, indent=4)
        
    print(f"✅ ¡ÉXITO DE EXTRAÍDOS! Guardados {len(jugadores)} jugadores DIRECTAMENTE de analiticafantasy.com")

if __name__ == "__main__":
    extraer_analitica_api()