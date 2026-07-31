import json
import requests
from bs4 import BeautifulSoup
import time

def extraccion_api_directa():
    print("⚡ Conectando a la API de Comuniate mediante sesión HTTP...")
    
    # Creamos una sesión para guardar cookies automáticas (el pasaporte de seguridad)
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.comuniate.com",
        "Referer": "https://www.comuniate.com/jugadores/comunio"
    })

    # 1. Primer contacto: Entramos a la web para recoger cookies de sesión
    try:
        print("🔑 Obteniendo credenciales de sesión...")
        session.get("https://www.comuniate.com/jugadores/comunio", timeout=10)
    except Exception as e:
        print(f"❌ Error al conectar con la web principal: {e}")
        return

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

    # Endpoint exacto de la API AJAX
    url_endpoint = "https://www.comuniate.com/ajax/jugadores/relevo_jugadores.php"

    for pag in range(1, 25):
        # Payload con los parámetros de consulta
        payload = {
            "page": pag,
            "pag": pag,
            "posicion": "todas",
            "orden": "puntos",
            "grupo": "0"
        }

        try:
            # Petición POST a la API
            res = session.post(url_endpoint, data=payload, timeout=10)
            
            if res.status_code != 200 or not res.text.strip():
                print(f"🛑 Fin de respuesta en página {pag}.")
                break

            soup = BeautifulSoup(res.text, 'html.parser')
            imagenes = soup.find_all('img')
            tarjetas_procesadas = set()
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
                        
                if not es_valida or id(tarjeta) in tarjetas_procesadas:
                    continue
                    
                tarjetas_procesadas.add(id(tarjeta))
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
                    for t in textos_sueltos:
                        if len(t) > 2 and not any(c.isdigit() for c in t) and '€' not in t and t.upper() not in mapa_posiciones:
                            if t.upper() not in ["IDEAL:", "MÁX.:", "IDEAL", "MÁX", "VALOR", "PUNTOS", "EQUIPO", "POSICIÓN", "MERCADO"]:
                                nombre = t
                                break
                if not nombre:
                    continue

                # Precio
                precio = "0 €"
                for i, t in enumerate(textos_sueltos):
                    if '€' in t:
                        prev_t = textos_sueltos[i-1].upper() if i > 0 else ""
                        if "IDEAL" not in prev_t and "MÁX" not in prev_t:
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

            print(f"   -> API Página {pag}: {jugadores_pagina} jugadores extraídos.")
            if jugadores_pagina == 0 and pag > 5:
                break
                
            time.sleep(0.3)

        except Exception as e:
            print(f"❌ Error consultando la página {pag}: {e}")
            break

    def obtener_valor(precio_str):
        digitos = ''.join(filter(str.isdigit, precio_str))
        return int(digitos) if digitos else 0

    resultado = list(jugadores_dict.values())
    if resultado:
        resultado.sort(key=lambda x: obtener_valor(x["precio"]), reverse=True)
        base_datos = {"laliga": {"chollos": resultado}}
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)
        print(f"🚀 API COMPLETADA: {len(resultado)} jugadores en el archivo JSON.")
    else:
        print("⚠️ La API rebotó la conexión.")

if __name__ == "__main__":
    extraccion_api_directa()