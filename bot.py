import json
import requests
from bs4 import BeautifulSoup
import time

def extraccion_flash_api():
    print("🚀 Lanzando misil directo a la base de datos de Comuniate (Sin navegador)...")
    jugadores_dict = {}

    mapa_posiciones = {
        'PT': 'POR', 'POR': 'POR',
        'DF': 'DEF', 'DEF': 'DEF',
        'MC': 'MED', 'MED': 'MED', 'MD': 'MED',
        'DL': 'DEL', 'DEL': 'DEL'
    }

    mapa_equipos = {
        "athletic": "Athletic Club", "bilbao": "Athletic Club",
        "atletico": "Atlético de Madrid", "atlético": "Atlético de Madrid", "atm": "Atlético de Madrid",
        "osasuna": "CA Osasuna", "leganes": "CD Leganés", "alaves": "D. Alavés",
        "barcelona": "FC Barcelona", "getafe": "Getafe CF", "girona": "Girona FC",
        "rayo": "Rayo Vallecano", "celta": "RC Celta", "espanyol": "RCD Espanyol",
        "mallorca": "RCD Mallorca", "betis": "Real Betis", "madrid": "Real Madrid",
        "sociedad": "Real Sociedad", "valladolid": "Real Valladolid", "sevilla": "Sevilla FC",
        "palmas": "UD Las Palmas", "valencia": "Valencia CF", "villarreal": "Villarreal CF"
    }

    # La URL secreta que tú mismo descubriste
    url_api = "https://www.comuniate.com/ajax/jugadores/relevo_jugadores.php"
    
    # Nos disfrazamos de navegador real para que no nos bloqueen
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    jugadores_totales = 0

    # Vamos a pedirle al servidor las páginas de la 1 a la 25
    for pag in range(1, 26):
        # Este es el Payload deducido: le decimos qué página queremos
        payload = {
            "page": pag,
            "posicion": "todas",
            "orden": "puntos"
        }

        try:
            # ¡BUM! Disparo directo al servidor
            respuesta = requests.post(url_api, headers=headers, data=payload)
            
            # Como nos dijiste que devolvía HTML, se lo pasamos a BeautifulSoup
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            
            # Buscamos directamente las etiquetas <img> de las fotos como hicimos en el código que funcionó
            imagenes = soup.find_all('img')
            jugadores_pagina = 0

            for img in imagenes:
                tarjeta = img.parent
                es_valida = False
                
                for _ in range(8):
                    if tarjeta and '€' in tarjeta.get_text():
                        if len(tarjeta.find_all('img')) <= 12:
                            es_valida = True
                            break
                    if tarjeta:
                        tarjeta = tarjeta.parent
                        
                if not es_valida:
                    continue
                    
                textos_sueltos = [t.strip() for t in tarjeta.stripped_strings if t.strip()]
                
                # Posición
                pos = "JUG"
                for t in textos_sueltos:
                    if t.upper() in mapa_posiciones:
                        pos = mapa_posiciones[t.upper()]
                        break
                        
                # Nombre
                nombre = ""
                for a in tarjeta.find_all('a'):
                    if '/equipo/' not in a.get('href', '').lower() and len(a.get_text(strip=True)) > 2:
                        nombre = a.get_text(strip=True)
                        break
                if not nombre:
                    continue

                # Precio
                precio = "0 €"
                for i, t in enumerate(textos_sueltos):
                    if '€' in t:
                        precio = t.replace('€', '').strip() + " €"
                        break

                # Puntos
                pts = "0.0"
                for t in textos_sueltos:
                    t_clean = t.replace('.', '').replace(',', '')
                    if t_clean.isdigit() and len(t_clean) <= 4 and t != precio.replace(' €', '') and t.upper() not in mapa_posiciones:
                        pts = t
                        break

                # Equipo
                equipo = "LaLiga"
                for a in tarjeta.find_all('a', href=True):
                    if '/equipo/' in a['href'].lower():
                        slug = a['href'].lower().split('/equipo/')[-1].split('/')[0]
                        for clave, nombre_real in mapa_equipos.items():
                            if clave in slug:
                                equipo = nombre_real
                                break
                    if equipo != "LaLiga": break

                if equipo == "LaLiga":
                    for i_tag in tarjeta.find_all('img'):
                        src = i_tag.get('src', '').lower()
                        alt = i_tag.get('alt', '').strip().lower()
                        for clave, nombre_real in mapa_equipos.items():
                            if clave in src or clave in alt:
                                equipo = nombre_real
                                break
                        if equipo != "LaLiga": break

                if nombre not in jugadores_dict:
                    jugadores_dict[nombre] = {
                        "nombre": nombre, "equipo": equipo, "pos": pos,
                        "precio": precio, "subida": "0 €", "pts": pts
                    }
                    jugadores_pagina += 1

            if jugadores_pagina == 0:
                print(f"🛑 Fin de los datos en la página {pag}.")
                break
                
            print(f"✅ ¡Extraídos {jugadores_pagina} jugadores en un parpadeo (Página {pag})!")
            jugadores_totales += jugadores_pagina
            
            # Descansamos medio segundo para no saturar su servidor
            time.sleep(0.5)

        except Exception as e:
            print(f"❌ Error en la página {pag}: {e}")

    def obtener_valor(precio_str):
        digitos = ''.join(filter(str.isdigit, precio_str))
        return int(digitos) if digitos else 0

    resultado = list(jugadores_dict.values())
    resultado.sort(key=lambda x: obtener_valor(x["precio"]), reverse=True)
    
    base_datos = {"laliga": {"chollos": resultado}}
    with open("datos.json", "w", encoding="utf-8") as f:
        json.dump(base_datos, f, ensure_ascii=False, indent=4)
        
    print(f"🏆 ¡MISIÓN CUMPLIDA! API ejecutada. {len(resultado)} chollos robados de la base de datos limpia.")

if __name__ == "__main__":
    extraccion_flash_api()