import json
import requests
from bs4 import BeautifulSoup

def extraccion_jornada_perfecta_laliga():
    print("🤖 Apuntando a Jornada Perfecta (Sección Exclusiva LaLiga Fantasy)...")
    
    # URLs objetivo específicas del juego de Relevo en Jornada Perfecta
    urls = [
        "https://www.jornadaperfecta.com/laliga-fantasy/",
        "https://www.jornadaperfecta.com/chollos-laliga-fantasy/"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
    }

    jugadores_dict = {}

    for url in urls:
        print(f"🌐 Visitando silenciosamente: {url}")
        try:
            # Usamos requests básico. Entra instantáneamente sin cargar navegadores.
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                print("✅ Conexión establecida sin bloqueos. Analizando el código...")
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # ESTRATEGIA 1: Buscar en tablas HTML (<tbody><tr>)
                filas = soup.find_all('tr')
                for fila in filas:
                    celdas = fila.find_all(['td', 'th'])
                    textos = [c.get_text(strip=True) for c in celdas if c.get_text(strip=True)]
                    
                    if len(textos) >= 2:
                        nombre = textos[0]
                        # Limpiar si el nombre empieza por números de ranking (ej: "1. Lamine Yamal")
                        if nombre and nombre[0].isdigit():
                            partes = nombre.split()
                            if len(partes) > 1 and partes[0].replace('.', '').isdigit():
                                nombre = " ".join(partes[1:])
                                
                        if nombre.upper() in ["JUGADOR", "NOMBRE", "POSICIÓN", "EQUIPO"]: 
                            continue
                        
                        # Extraer heurísticamente precio y puntos
                        precio = "0 €"
                        pts = "0.0"
                        equipo = "LaLiga"
                        
                        for txt in textos[1:]:
                            if '€' in txt or (txt.replace('.', '').isdigit() and len(txt) > 4):
                                precio = txt if '€' in txt else f"{txt} €"
                            elif len(txt) < 4 and txt.replace('.', '').replace(',', '').isdigit():
                                pts = txt
                            elif len(txt) == 3 and txt.isupper():
                                equipo = txt
                        
                        if len(nombre) > 2:
                            jugadores_dict[nombre] = {
                                "nombre": nombre, "equipo": equipo, "pos": "JUG",
                                "precio": precio, "subida": "0 €", "pts": pts
                            }
                
                # ESTRATEGIA 2: Buscar en los encabezados (h3, h4, strong) de artículos de chollos
                # Ej: "<h3>Vinícius (Real Madrid)</h3>"
                titulos = soup.find_all(['h3', 'h4', 'strong'])
                for t in titulos:
                    txt = t.get_text(strip=True)
                    if '(' in txt and ')' in txt and len(txt) < 35:
                        partes = txt.split('(')
                        nombre = partes[0].strip()
                        equipo = partes[1].replace(')', '').strip()
                        
                        if nombre and len(nombre) > 2 and not nombre.isdigit():
                            if nombre not in jugadores_dict:
                                jugadores_dict[nombre] = {
                                    "nombre": nombre, "equipo": equipo, "pos": "JUG",
                                    "precio": "0 €", "subida": "0 €", "pts": "0.0"
                                }

            else:
                print(f"⚠️ El servidor devolvió status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Fallo en la petición a {url}: {e}")

    # Guardado de la base de datos
    resultado = list(jugadores_dict.values())
    if resultado:
        base_datos = {"laliga": {"chollos": resultado}}
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡GOLPE LIMPIO! Extraídos {len(resultado)} jugadores en tiempo récord.")
    else:
        print("❌ No se encontraron tablas o formatos de jugadores en esas URLs específicas.")

if __name__ == "__main__":
    extraccion_jornada_perfecta_laliga()