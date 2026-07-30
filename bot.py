import json
import re
import cloudscraper

def extraer_analitica_oficial():
    print("🤖 Conectando EXCLUSIVAMENTE a www.analiticafantasy.com (Mercado LaLiga)...")
    url = "https://www.analiticafantasy.com/fantasy-la-liga/mercado"
    
    # Esto engaña al cortafuegos de Analítica para que piense que somos un navegador real
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
    
    try:
        response = scraper.get(url, timeout=30)
        response.raise_for_status()
        
        html = response.text
        
        # Analítica Fantasy guarda los datos de la tabla de mercado en este bloque oculto
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        
        if not match:
            print("❌ No se encontraron los datos ocultos en la web de Analítica.")
            return
            
        data = json.loads(match.group(1))
        
        # Buscador recursivo para cazar la lista masiva de jugadores sin importar cómo la llamen
        jugadores_raw = []
        def buscar_jugadores(obj):
            nonlocal jugadores_raw
            if jugadores_raw: return
            if isinstance(obj, dict):
                for k, v in obj.items():
                    # Si es una lista grande y tiene la palabra "marketValue" o "price", es la tabla de jugadores
                    if isinstance(v, list) and len(v) > 100 and isinstance(v[0], dict) and ("marketValue" in v[0] or "price" in v[0]):
                        jugadores_raw = v
                        return
                    buscar_jugadores(v)
            elif isinstance(obj, list):
                for item in obj:
                    buscar_jugadores(item)
        
        buscar_jugadores(data)
        
        if not jugadores_raw:
            print("❌ No se pudo extraer la lista de jugadores de la web.")
            return
            
        jugadores = []
        for p in jugadores_raw:
            nombre = p.get("nickname", p.get("name", "Jugador"))
            equipo = p.get("teamName", p.get("team", {}).get("name", "LaLiga"))
            pos = str(p.get("position", "MED"))
            
            # Mapeo por si las posiciones vienen en número
            pos_map = {"1": "POR", "2": "DEF", "3": "MED", "4": "DEL"}
            pos = pos_map.get(pos, pos)
            
            precio = p.get("marketValue", p.get("price", 0))
            incremento = p.get("marketValueIncrement", p.get("priceIncrement", 0))
            puntos = str(p.get("pointsAverage", p.get("points", 0)))
            
            # Formatear números
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
            
        print(f"✅ ¡ÉXITO! Extraídos {len(jugadores)} jugadores DIRECTAMENTE de analiticafantasy.com")
        
    except Exception as e:
        print(f"❌ Error al raspar Analítica Fantasy: {e}")

if __name__ == "__main__":
    extraer_analitica_oficial()