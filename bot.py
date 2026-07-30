import json
from seleniumbase import SB
from bs4 import BeautifulSoup

def extraccion_comuniate_paginada():
    print("🤖 Iniciando asalto total a Comuniate (Todas las páginas)...")
    jugadores_dict = {}

    with SB(uc=True, headless=True) as sb:
        try:
            print("🌐 Abriendo la URL base...")
            sb.uc_open_with_reconnect("https://www.comuniate.com/jugadores/comunio", reconnect_time=4)
            sb.sleep(4)

            print("🔄 Aplicando el filtro 'LALIGA FANTASY'...")
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
                } catch(e) { }
            """)
            sb.sleep(4) 

            pagina_actual = 1
            while True:
                print(f"📄 Escaneando página {pagina_actual}...")
                
                # Extraemos el HTML de la página actual
                html = sb.get_page_source()
                soup = BeautifulSoup(html, 'html.parser')

                # Buscamos las filas de la tabla
                filas = soup.find_all('tr')
                jugadores_en_pagina = 0

                for fila in filas:
                    texto_fila = fila.get_text(separator=" ", strip=True)
                    if '€' not in texto_fila:
                        continue # Si no hay euros, no es un jugador

                    celdas = fila.find_all(['td', 'th'])
                    if len(celdas) < 4:
                        continue

                    # 1. Atrapar Nombre
                    nombre = ""
                    a_tag = fila.find('a')
                    if a_tag and len(a_tag.get_text(strip=True)) > 2:
                        nombre = a_tag.get_text(strip=True)
                    else:
                        for c in celdas:
                            t = c.get_text(strip=True)
                            if len(t) > 3 and not any(char.isdigit() for char in t) and '€' not in t:
                                nombre = t
                                break

                    if not nombre or nombre.upper() in ["VALOR", "JUGADOR", "PUNTOS", "EQUIPO", "POSICIÓN"]:
                        continue

                    # 2. Atrapar Precio
                    precio = "0 €"
                    for c in celdas:
                        if '€' in c.text:
                            precio = c.text.strip()
                            break

                    # 3. Atrapar Posición precisa (Buscamos las siglas exactas en el texto)
                    pos = "JUG"
                    posiciones_validas = {'PT': 'POR', 'POR': 'POR', 'DF': 'DEF', 'DEF': 'DEF', 'MC': 'MED', 'MED': 'MED', 'DL': 'DEL', 'DEL': 'DEL'}
                    for fragmento in fila.stripped_strings:
                        frag_up = fragmento.upper().strip()
                        if frag_up in posiciones_validas:
                            pos = posiciones_validas[frag_up]
                            break

                    # 4. Atrapar Equipo (Buscamos en los enlaces o en el alt de la imagen)
                    equipo = "Desconocido"
                    # Intento A: Por el atributo 'alt' de la imagen
                    imgs = fila.find_all('img')
                    for img in imgs:
                        alt = img.get('alt', '').strip()
                        if alt and alt.upper() not in ["FOTO", "JUGADOR", "AVATAR", nombre.upper()]:
                            equipo = alt.title()
                            break
                    # Intento B: Si la imagen no tiene alt, buscamos en el enlace del equipo
                    if equipo == "Desconocido":
                        enlaces = fila.find_all('a')
                        for en in enlaces:
                            href = en.get('href', '')
                            if '/equipo/' in href:
                                equipo = href.split('/')[-1].replace('-', ' ').title()
                                break
                    if equipo == "Desconocido":
                        equipo = "LaLiga"

                    # 5. Atrapar Puntos
                    pts = "0.0"
                    for c in celdas:
                        t = c.get_text(strip=True)
                        if len(t) <= 4 and t.replace('.', '').replace(',', '').isdigit():
                            pts = t

                    # Guardamos el jugador si es válido
                    if nombre not in jugadores_dict and "RANGO" not in precio.upper() and "PRECIO" not in precio.upper():
                        jugadores_dict[nombre] = {
                            "nombre": nombre, "equipo": equipo, "pos": pos,
                            "precio": precio, "subida": "0 €", "pts": pts
                        }
                        jugadores_en_pagina += 1

                print(f"   -> ¡Capturados {jugadores_en_pagina} chollos en esta página!")

                # --- EL MOTOR DE PAGINACIÓN AUTOMÁTICA ---
                # Comprobamos si el botón de "Siguiente" está deshabilitado (llegamos al final)
                fin_de_paginas = sb.execute_script("""
                    var nextBtn = document.querySelector('.paginate_button.next');
                    if (!nextBtn) return true; // Si no hay botón, hemos terminado
                    return nextBtn.classList.contains('disabled'); // Devuelve true si ya no se puede hacer clic
                """)

                if fin_de_paginas:
                    print("🛑 ¡Última página alcanzada! El asalto ha terminado.")
                    break
                
                print("➡️ Haciendo clic en 'Siguiente'...")
                try:
                    sb.execute_script("document.querySelector('.paginate_button.next').click();")
                    sb.sleep(2) # Pausa de 2 segundos para que la tabla cargue los nuevos jugadores
                    pagina_actual += 1
                except Exception as e:
                    print(f"⚠️ No se pudo hacer clic en Siguiente: {e}")
                    break

        except Exception as e:
            print(f"❌ Error en la ejecución principal: {e}")

    # Ordenar y guardar
    def obtener_valor_numerico(precio_str):
        digitos = ''.join(filter(str.isdigit, precio_str))
        return int(digitos) if digitos else 0

    resultado = list(jugadores_dict.values())
    if resultado:
        resultado.sort(key=lambda x: obtener_valor_numerico(x["precio"]), reverse=True)
        
        base_datos = {"laliga": {"chollos": resultado}}
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡MISIÓN COMPLETADA! Base de datos reventada: {len(resultado)} jugadores en total.")
    else:
        print("❌ No se encontraron jugadores.")

if __name__ == "__main__":
    extraccion_comuniate_paginada()