import json
from seleniumbase import SB
from bs4 import BeautifulSoup

def extraccion_tarjetas_comuniate():
    print("🤖 Iniciando asalto (Escáner de Tarjetas con Diccionario de Equipos Activo)...")
    jugadores_dict = {}

    mapa_posiciones = {
        'PT': 'POR', 'POR': 'POR',
        'DF': 'DEF', 'DEF': 'DEF',
        'MC': 'MED', 'MED': 'MED',
        'DL': 'DEL', 'DEL': 'DEL'
    }

    # Diccionario implacable: Si encuentra la palabra clave (izq), pone el nombre oficial (der)
    mapa_equipos = {
        "athletic": "Athletic Club",
        "atletico": "Atlético de Madrid",
        "osasuna": "CA Osasuna",
        "leganes": "CD Leganés",
        "alaves": "D. Alavés",
        "barcelona": "FC Barcelona",
        "getafe": "Getafe CF",
        "girona": "Girona FC",
        "rayo": "Rayo Vallecano",
        "celta": "RC Celta",
        "espanyol": "RCD Espanyol",
        "mallorca": "RCD Mallorca",
        "betis": "Real Betis",
        "madrid": "Real Madrid",
        "sociedad": "Real Sociedad",
        "valladolid": "Real Valladolid",
        "sevilla": "Sevilla FC",
        "palmas": "UD Las Palmas",
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

            for pag in range(1, 20):
                print(f"📄 Escaneando página {pag}...")
                
                if pag > 1:
                    exito_clic = sb.execute_script("""
                        var target = '""" + str(pag) + """';
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
                        break
                    sb.sleep(2.5) 

                html = sb.get_page_source()
                soup = BeautifulSoup(html, 'html.parser')
                
                etiquetas_posicion = soup.find_all(['span', 'div', 'b', 'strong', 'p'])
                tarjetas_procesadas = set()
                jugadores_pagina = 0

                for tag in etiquetas_posicion:
                    texto_tag = tag.get_text(strip=True).upper()
                    
                    if texto_tag in mapa_posiciones:
                        padre = tag.parent
                        es_tarjeta = False
                        for _ in range(6): 
                            if padre and '€' in padre.get_text():
                                es_tarjeta = True
                                break
                            if padre:
                                padre = padre.parent
                        
                        if not es_tarjeta or not padre or id(padre) in tarjetas_procesadas:
                            continue
                        
                        tarjetas_procesadas.add(id(padre))
                        pos = mapa_posiciones[texto_tag]
                        
                        textos_sueltos = [t.strip() for t in padre.stripped_strings if t.strip()]
                        
                        # 1. NOMBRE
                        nombre = ""
                        a_tag = padre.find('a')
                        if a_tag and len(a_tag.get_text(strip=True)) > 2:
                            nombre = a_tag.get_text(strip=True)
                        else:
                            for t in textos_sueltos:
                                if len(t) > 2 and not any(c.isdigit() for c in t) and '€' not in t and t.upper() not in mapa_posiciones:
                                    if t.upper() not in ["IDEAL:", "MÁX.:", "IDEAL", "MÁX"]:
                                        nombre = t
                                        break
                        
                        if not nombre:
                            continue

                        # 2. PRECIO
                        precio = "0 €"
                        for i, t in enumerate(textos_sueltos):
                            if '€' in t:
                                prev_t = textos_sueltos[i-1].upper() if i > 0 else ""
                                if "IDEAL" not in prev_t and "MÁX" not in prev_t and "IDEAL" not in t.upper() and "MÁX" not in t.upper():
                                    precio = t.replace('€', '').strip() + " €"
                                    break
                        
                        # 3. PUNTOS
                        pts = "0.0"
                        for t in textos_sueltos:
                            t_clean = t.replace('.', '').replace(',', '')
                            if t_clean.isdigit() and len(t_clean) <= 4 and t != texto_tag:
                                pts = t
                                break
                                
                        # 4. EQUIPO (Búsqueda Agresiva con Diccionario)
                        equipo = "LaLiga"
                        
                        # Intento A: A través de los enlaces (href) que apuntan al equipo
                        for a in padre.find_all('a', href=True):
                            href = a['href'].lower()
                            if '/equipo/' in href:
                                slug = href.split('/equipo/')[-1].split('/')[0] # ej: "real-madrid"
                                for clave, nombre_real in mapa_equipos.items():
                                    if clave in slug:
                                        equipo = nombre_real
                                        break
                            if equipo != "LaLiga": break

                        # Intento B: Si no hay enlace, miramos el escudo (src, alt, title)
                        if equipo == "LaLiga":
                            for img in padre.find_all('img'):
                                src = img.get('src', '').lower()
                                alt = img.get('alt', '').strip().lower()
                                title = img.get('title', '').strip().lower()
                                
                                if nombre.lower() in alt or "avatar" in src or "jugador" in src:
                                    continue
                                    
                                for clave, nombre_real in mapa_equipos.items():
                                    if clave in src or clave in alt or clave in title:
                                        equipo = nombre_real
                                        break
                                
                                if equipo != "LaLiga": break

                        if nombre not in jugadores_dict and precio != "0 €":
                            jugadores_dict[nombre] = {
                                "nombre": nombre, "equipo": equipo, "pos": pos,
                                "precio": precio, "subida": "0 €", "pts": pts
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
        print(f"✅ ¡MISIÓN COMPLETADA Y PULIDA! {len(resultado)} jugadores con equipos impecables.")
    else:
        print("❌ El escáner funcionó, pero no logró reconstruir las tarjetas.")

if __name__ == "__main__":
    extraccion_tarjetas_comuniate()