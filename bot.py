import json
from seleniumbase import SB
from bs4 import BeautifulSoup

def extraccion_tarjetas_comuniate():
    print("🤖 Iniciando asalto (Escáner de Tarjetas de Jugador por Anclaje Visual)...")
    jugadores_dict = {}

    mapa_posiciones = {
        'PT': 'POR', 'POR': 'POR',
        'DF': 'DEF', 'DEF': 'DEF',
        'MC': 'MED', 'MED': 'MED',
        'DL': 'DEL', 'DEL': 'DEL'
    }

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

            for pag in range(1, 20): # Aseguramos llegar hasta el final
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
                
                # ESTRATEGIA DE ANCLAJE: Buscamos primero las etiquetas de posición (PT, DF, MC, DL)
                etiquetas_posicion = soup.find_all(['span', 'div', 'b', 'strong', 'p'])
                tarjetas_procesadas = set()
                jugadores_pagina = 0

                for tag in etiquetas_posicion:
                    texto_tag = tag.get_text(strip=True).upper()
                    
                    if texto_tag in mapa_posiciones:
                        # Hemos encontrado el "Globito Verde". Ahora subimos para agarrar toda la tarjeta
                        padre = tag.parent
                        es_tarjeta = False
                        for _ in range(6): 
                            if padre and '€' in padre.get_text():
                                es_tarjeta = True
                                break
                            if padre:
                                padre = padre.parent
                        
                        # Si no tiene precio o ya leímos esta tarjeta, pasamos de largo
                        if not es_tarjeta or not padre or id(padre) in tarjetas_procesadas:
                            continue
                        
                        tarjetas_procesadas.add(id(padre))
                        pos = mapa_posiciones[texto_tag]
                        
                        # Extraemos todo el texto suelto de la tarjeta
                        textos_sueltos = [t.strip() for t in padre.stripped_strings if t.strip()]
                        
                        # 1. NOMBRE (Suele estar en un enlace <a> o ser el primer texto largo)
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

                        # 2. PRECIO (Evitando los textos secundarios como "Ideal:" o "Máx.:")
                        precio = "0 €"
                        for i, t in enumerate(textos_sueltos):
                            if '€' in t:
                                prev_t = textos_sueltos[i-1].upper() if i > 0 else ""
                                if "IDEAL" not in prev_t and "MÁX" not in prev_t and "IDEAL" not in t.upper() and "MÁX" not in t.upper():
                                    precio = t.replace('€', '').strip() + " €"
                                    break
                        
                        # 3. PUNTOS (El número suelto que acompaña a la posición en el globito azul)
                        pts = "0.0"
                        for t in textos_sueltos:
                            t_clean = t.replace('.', '').replace(',', '')
                            if t_clean.isdigit() and len(t_clean) <= 4 and t != texto_tag:
                                pts = t
                                break
                                
                        # 4. EQUIPO (Buscando el pequeño escudo en las imágenes)
                        equipo = "LaLiga"
                        for img in padre.find_all('img'):
                            src = img.get('src', '').lower()
                            alt = img.get('alt', '').strip().upper()
                            
                            if nombre.upper() in alt or "AVATAR" in src or "JUGADOR" in src:
                                continue
                                
                            for eq in equipos_laliga:
                                eq_norm = eq.lower().replace(" ", "-")
                                eq_norm_no_accents = eq_norm.replace('é','e').replace('á','a').replace('í','i').replace('ó','o').replace('ú','u')
                                
                                if eq.lower() in src or eq_norm in src or eq_norm_no_accents in src or eq.upper() in alt:
                                    equipo = eq
                                    if equipo == "Madrid": equipo = "Real Madrid"
                                    if equipo == "Sociedad": equipo = "Real Sociedad"
                                    break
                            
                            if equipo != "LaLiga":
                                break

                        # Guardamos en el diccionario
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
        print(f"✅ ¡MISIÓN COMPLETADA! {len(resultado)} jugadores extraídos leyendo las tarjetas visuales.")
    else:
        print("❌ El escáner funcionó, pero no logró reconstruir las tarjetas.")

if __name__ == "__main__":
    extraccion_tarjetas_comuniate()