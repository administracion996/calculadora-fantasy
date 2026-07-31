import json
from seleniumbase import SB
from bs4 import BeautifulSoup

def extraccion_por_foto():
    print("🤖 Iniciando asalto (Estrategia Infalible: Anclaje desde la Foto del Jugador)...")
    jugadores_dict = {}

    mapa_posiciones = {
        'PT': 'POR', 'POR': 'POR',
        'DF': 'DEF', 'DEF': 'DEF',
        'MC': 'MED', 'MED': 'MED', 'MD': 'MED',
        'DL': 'DEL', 'DEL': 'DEL'
    }

    mapa_equipos = {
        "athletic": "Athletic Club", "bilbao": "Athletic Club",
        "atletico": "Atlético de Madrid", "atlético": "Atlético de Madrid", "atm": "Atlético de Madrid", "atl": "Atlético de Madrid",
        "osasuna": "CA Osasuna",
        "leganes": "CD Leganés", "leganés": "CD Leganés",
        "alaves": "D. Alavés", "alavés": "D. Alavés",
        "barcelona": "FC Barcelona", "fcb": "FC Barcelona",
        "getafe": "Getafe CF",
        "girona": "Girona FC",
        "rayo": "Rayo Vallecano",
        "celta": "RC Celta",
        "espanyol": "RCD Espanyol",
        "mallorca": "RCD Mallorca",
        "betis": "Real Betis",
        "madrid": "Real Madrid", "rmadrid": "Real Madrid", "rma": "Real Madrid",
        "sociedad": "Real Sociedad", "rsociedad": "Real Sociedad",
        "valladolid": "Real Valladolid",
        "sevilla": "Sevilla FC",
        "palmas": "UD Las Palmas", "las-palmas": "UD Las Palmas", "udp": "UD Las Palmas",
        "valencia": "Valencia CF",
        "villarreal": "Villarreal CF"
    }

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

            for pag in range(1, 25): 
                print(f"📄 Escaneando página {pag}...")
                
                if pag > 1:
                    exito_clic = sb.execute_script("""
                        try {
                            var target = '""" + str(pag) + """';
                            
                            var current = document.querySelector('.paginate_button.current, li.active, span.current');
                            if (current && current.nextElementSibling) {
                                var nextL = current.nextElementSibling.querySelector('a') || current.nextElementSibling;
                                if (nextL && !nextL.classList.contains('disabled')) {
                                    nextL.click();
                                    return true;
                                }
                            }
                            
                            var btns = document.querySelectorAll('.paginate_button, .pagination a, ul.pagination li a, .page-link, span.paginate_button');
                            for (var i = 0; i < btns.length; i++) {
                                if (btns[i].innerText.trim() === target) {
                                    btns[i].click();
                                    return true;
                                }
                            }
                            
                            var nextBtn = document.querySelector('.next, [aria-label="Next"], [rel="next"]');
                            if (nextBtn && !nextBtn.classList.contains('disabled')) {
                                (nextBtn.querySelector('a') || nextBtn).click();
                                return true;
                            }
                        } catch(e) {}
                        return false;
                    """)
                    
                    if not exito_clic:
                        break
                        
                    sb.sleep(3)

                html = sb.get_page_source()
                soup = BeautifulSoup(html, 'html.parser')
                
                todas_las_imagenes = soup.find_all('img')
                tarjetas_procesadas = set()
                jugadores_pagina = 0

                for img in todas_las_imagenes:
                    tarjeta = img.parent
                    es_tarjeta_valida = False
                    
                    for _ in range(8):
                        if tarjeta and '€' in tarjeta.get_text():
                            if len(tarjeta.find_all('img')) <= 12:
                                es_tarjeta_valida = True
                                break
                        if tarjeta:
                            tarjeta = tarjeta.parent
                            
                    if not es_tarjeta_valida or id(tarjeta) in tarjetas_procesadas:
                        continue
                        
                    tarjetas_procesadas.add(id(tarjeta))
                    
                    textos_sueltos = [t.strip() for t in tarjeta.stripped_strings if t.strip()]
                    
                    # 1. POSICIÓN
                    pos = "JUG"
                    for t in textos_sueltos:
                        if t.upper() in mapa_posiciones:
                            pos = mapa_posiciones[t.upper()]
                            break
                            
                    # 2. NOMBRE
                    nombre = ""
                    for a in tarjeta.find_all('a'):
                        href = a.get('href', '').lower()
                        if '/equipo/' not in href and len(a.get_text(strip=True)) > 2:
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

                    # 3. PRECIO
                    precio = "0 €"
                    for i, t in enumerate(textos_sueltos):
                        if '€' in t:
                            prev_t = textos_sueltos[i-1].upper() if i > 0 else ""
                            if "IDEAL" not in prev_t and "MÁX" not in prev_t and "IDEAL" not in t.upper() and "MÁX" not in t.upper():
                                precio = t.replace('€', '').strip() + " €"
                                break

                    # 4. PUNTOS
                    pts = "0.0"
                    for t in textos_sueltos:
                        t_clean = t.replace('.', '').replace(',', '')
                        if t_clean.isdigit() and len(t_clean) <= 4 and t != precio.replace(' €', '') and t.upper() not in mapa_posiciones:
                            pts = t
                            break

                    # 5. EQUIPO
                    equipo = "LaLiga"
                    
                    for a in tarjeta.find_all('a', href=True):
                        href = a['href'].lower()
                        if '/equipo/' in href:
                            slug = href.split('/equipo/')[-1].split('/')[0]
                            for clave, nombre_real in mapa_equipos.items():
                                if clave in slug:
                                    equipo = nombre_real
                                    break
                        if equipo != "LaLiga": break

                    if equipo == "LaLiga":
                        for i_tag in tarjeta.find_all('img'):
                            src = i_tag.get('src', '').lower()
                            alt = i_tag.get('alt', '').strip().lower()
                            title = i_tag.get('title', '').strip().lower()
                            
                            if nombre.lower() in alt or "avatar" in src or "jugador" in src:
                                continue
                                
                            for clave, nombre_real in mapa_equipos.items():
                                if clave in src or clave in alt or clave in title:
                                    equipo = nombre_real
                                    break
                            
                            if equipo != "LaLiga": break

                    if nombre not in jugadores_dict:
                        jugadores_dict[nombre] = {
                            "nombre": nombre, "equipo": equipo, "pos": pos,
                            "precio": precio, "subida": "0 €", "pts": pts
                        }
                        jugadores_pagina += 1

                print(f"   -> ¡Capturados {jugadores_pagina} jugadores en página {pag}!")
                
                if jugadores_pagina == 0 and pag >= 17:
                    break

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
        print(f"✅ ¡RÉCORD TOTAL RESTAURADO! {len(resultado)} chollos capturados.")
    else:
        print("❌ Sigue dando 0. Algo va muy mal.")

if __name__ == "__main__":
    extraccion_por_foto()
    