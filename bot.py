import json
import requests
from bs4 import BeautifulSoup

def extraccion_comuniate_laliga_fantasy():
    print("🤖 Apuntando a Comuniate (Sección Exclusiva LaLiga Fantasy)...")
    
    # Diferentes rutas que suele usar la web para listar jugadores de LaLiga Fantasy
    urls = [
        "https://www.comuniate.com/jugadores?juego=laligafantasy",
        "https://www.comuniate.com/laliga-fantasy/mercado",
        "https://www.comuniate.com/laliga-fantasy/subidas"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }

    jugadores_dict = {}

    for url in urls:
        print(f"🌐 Explorando sigilosamente: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                print("✅ Conexión limpia. Analizando la estructura de datos...")
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # ESTRATEGIA 1: Buscar en tablas tradicionales (<tr>)
                for fila in soup.find_all('tr'):
                    celdas = fila.find_all(['td', 'th'])
                    textos = [c.get_text(strip=True) for c in celdas if c.get_text(strip=True)]
                    
                    if len(textos) >= 3:
                        nombre_candidato = textos[0]
                        
                        # Descartar cabeceras de la tabla
                        if nombre_candidato.upper() in ["JUGADOR", "POS", "EQUIPO", "PUNTOS", "VALOR"]:
                            continue
                            
                        precio = "0 €"
                        pts = "0.0"
                        pos = "JUG"
                        
                        for txt in textos:
                            # Identificar precios (ej. 15.000.000 o 15.000.000 €)
                            if '€' in txt or (txt.replace('.', '').isdigit() and len(txt) > 5):
                                precio = txt if '€' in txt else f"{txt} €"
                            # Identificar puntos (ej. 120 o 5.4)
                            elif len(txt) <= 4 and txt.replace('.', '').isdigit():
                                pts = txt
                            # Identificar posiciones
                            elif txt in ['POR', 'DEF', 'MED', 'DEL', 'PT', 'DF', 'MC', 'DL']:
                                pos = txt
                        
                        if len(nombre_candidato) > 2:
                            jugadores_dict[nombre_candidato] = {
                                "nombre": nombre_candidato,
                                "equipo": "LaLiga", # El equipo suele venir en imagen, lo dejamos genérico
                                "pos": pos,
                                "precio": precio,
                                "subida": "0 €",
                                "pts": pts
                            }
                            
                # ESTRATEGIA 2: Buscar en tarjetas de diseño (<div>) por si no usan tablas
                tarjetas = soup.find_all('div', class_=lambda x: x and 'jugador' in x.lower())
                for tarjeta in tarjetas:
                    nombre_tag = tarjeta.find(['h3', 'strong', 'div'], class_=lambda x: x and 'nombre' in x.lower())
                    precio_tag = tarjeta.find(string=lambda t: t and '€' in t)
                    
                    if nombre_tag and precio_tag:
                        nombre = nombre_tag.get_text(strip=True)
                        precio = precio_tag.strip()
                        if nombre not in jugadores_dict and len(nombre) > 2:
                            jugadores_dict[nombre] = {
                                "nombre": nombre, "equipo": "LaLiga", "pos": "JUG",
                                "precio": precio, "subida": "0 €", "pts": "0.0"
                            }

            else:
                print(f"⚠️ La web devolvió el código {response.status_code} para esta ruta.")
        except Exception as e:
            print(f"❌ Error al intentar leer {url}: {e}")

    # Guardar la base de datos
    resultado = list(jugadores_dict.values())
    if resultado:
        # Ordenamos los jugadores del más caro al más barato para que quede profesional
        resultado.sort(key=lambda x: int(x["precio"].replace(" €", "").replace(".", "")) if isinstance(x.get("precio"), str) and "€" in x["precio"] else 0, reverse=True)
        
        base_datos = {"laliga": {"chollos": resultado}}
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡MISIÓN CUMPLIDA! Extraídos {len(resultado)} jugadores reales de LaLiga Fantasy.")
    else:
        print("❌ No se encontraron jugadores en estas rutas de Comuniate.")

if __name__ == "__main__":
    extraccion_comuniate_laliga_fantasy()