import json
from seleniumbase import SB
from bs4 import BeautifulSoup

def extraccion_comuniate_vision_escudos():
    print("🤖 Iniciando asalto (Paginación 1-17 + Lector de Escudos y Tarjetas)...")
    jugadores_dict = {}

    mapa_posiciones = {
        'PT': 'POR', 'POR': 'POR',
        'DF': 'DEF', 'DEF': 'DEF',
        'MC': 'MED', 'MED': 'MED',
        'DL': 'DEL', 'DEL': 'DEL'
    }

    # Diccionario de seguridad para relacionar nombres de archivos de escudos con el equipo real
    equipos_laliga = [
        "Athletic", "Atlético", "Osasuna", "Leganés", "Alavés", 
        "Barcelona", "Getafe", "Girona", "Rayo", "Celta", 
        "Espanyol", "Mallorca", "Betis", "Madrid", "Real Madrid",
        "Sociedad", "Valladolid", "Sevilla", "Las Palmas", 
        "Valencia", "Villarreal"
    ]

    with SB(uc=True, headless=True) as sb:
        try:
            print("🌐 Abriendo la URL base...")
            sb.uc_open_with_reconnect("https://www.comuniate.com/jugadores/comunio", reconnect_time=4)
            sb.sleep(4)

            print("🔄 Forzando filtro a 'LALIGA FANTASY DAZN'...")
            sb.execute_script("""
                try {
                    var selects = document.querySelectorAll('select');
                    for (var i = 0; i < selects.length; i++) {
                        if (!selects[i] || !selects[i].options) continue;
                        for (var j = 0; j < selects[i].options.length; j++) {
                            var opt = selects[i].options[j];
                            if (opt && opt.text && opt.text.toUpperCase().includes('LALIGA FANTASY')) {
                                selects[i].value = opt.value;
                                selects[i].dispatchEvent(new Event('change', { bubbles: true }));
                                if (typeof jQuery !== 'undefined') jQuery(selects[i]).trigger('change');
                            }
                        }
                    }
                } catch(e) {}
            """)
            sb.sleep(4)

            for pag in range(1, 20):
                print(f"📄 Escaneando página {pag}...")
                
                if pag > 1:
                    exito_clic = sb.execute_script(f"""
                        var target = '{pag}';
                        var btns = document.querySelectorAll('.paginate_button, .pagination a, ul.pagination li a, .page-link, span.paginate_button');
                        for (var i = 0; i < btns.length; i++) {
                            if (btns[i].innerText.trim() === target) {
                                btns[i].click();
                                return true;
                            }
                        }
                        return false;
                    """)
                    if not exito_clic:
                        print(f"🛑 Fin de la paginación alcanzado (No existe la página {pag}).")
                        break
                    sb.sleep(2.5) 

                html = sb.get_page_source()
                soup = BeautifulSoup(html, 'html.parser')

                filas = soup.find_all('tr')
                jugadores_pagina = 0

                for fila in filas:
                    texto_fila = fila.get_text(separator=" ", strip=True)
                    if '€' not in texto_fila:
                        continue

                    # 1. NOMBRE Y PRECIO
                    nombre = ""
                    precio = "0 €"
                    pts = "0.0"
                    
                    textos_sueltos = [txt for txt in fila.stripped_strings]
                    
                    for txt in textos_sueltos:
                        if '€' in txt and "RANGO" not in txt.upper() and "PRECIO" not in txt.upper():
                            precio = txt
                        elif len(txt) > 2 and not any(ch.isdigit() for ch in txt) and '€' not in txt and txt.upper() not in ["VALOR", "JUGADOR", "PUNTOS", "EQUIPO", "POSICIÓN", "MERCADO"] and txt.upper() not in mapa_posiciones:
                            if not nombre:
                                nombre = txt
                        elif len(txt) <= 4 and txt.replace('.', '').replace(',', '').isdigit():
                            pts = txt

                    if not nombre or precio == "0 €":
                        # Intento extra para el nombre a través de enlaces si el método anterior falló
                        a_tag = fila.find('a')
                        if a_tag and len(a_tag.get_text(strip=True)) > 2:
                            nombre = a_tag.get_text(strip=True)
                            
                    if not nombre or precio == "0 €":
                        continue

                    # 2. POSICIÓN (Cazando las siglas de los globitos)
                    pos = "MED"
                    for txt in textos_sueltos:
                        if txt.upper() in mapa_posiciones:
                            pos = mapa_posiciones[txt.upper()]
                            break

                    # 3. EQUIPO (Inspeccionando los Escudos de la imagen que pasaste)
                    equipo = "LaLiga"
                    imgs = fila.find_all('img')
                    for img in imgs:
                        src = img.get('src', '').lower()
                        alt = img.get('alt', '').upper()
                        
                        # Analizamos todas las imágenes en busca del escudo
                        # Descartamos la foto principal del jugador
                        if nombre.upper() not in alt and "AVATAR" not in alt and "FOTO" not in alt:
                            # Comprobamos la lista de equipos contra el nombre del archivo de imagen o su alt
                            for eq in equipos_laliga:
                                if eq.lower() in src or eq.upper() in alt:
                                    equipo = eq
                                    if equipo == "Madrid": equipo = "Real Madrid"
                                    if equipo == "Sociedad": equipo = "Real Sociedad"
                                    break
                        if equipo != "LaLiga":
                            break

                    if nombre not in jugadores_dict:
                        jugadores_dict[nombre] = {
                            "nombre": nombre,
                            "equipo": equipo,
                            "pos": pos,
                            "precio": precio,
                            "subida": "0 €",
                            "pts": pts
                        }
                        jugadores_pagina += 1

                print(f"   -> ¡Capturados {jugadores_pagina} jugadores en página {pag}!")

        except Exception as e:
            print(f"❌ Error durante la extracción: {e}")

    def obtener_valor_numerico(precio_str):
        digitos = ''.join(filter(str.isdigit, precio_str))
        return int(digitos) if digitos else 0

    resultado = list(jugadores_dict.values())
    if resultado:
        resultado.sort(key=lambda x: obtener_valor_numerico(x["precio"]), reverse=True)
        
        base_datos = {"laliga": {"chollos": resultado}}
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡MÁXIMA PRECISIÓN! {len(resultado)} jugadores extraídos con escudos y posiciones reales.")
    else:
        print("❌ No se encontraron jugadores.")

if __name__ == "__main__":
    extraccion_comuniate_vision_escudos()