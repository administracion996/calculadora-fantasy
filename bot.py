import json
from seleniumbase import SB
from bs4 import BeautifulSoup

def extraccion_maestra():
    print("🤖 Iniciando asalto total (Escáner Todoterreno + Paginación Automática)...")
    jugadores_dict = {}

    with SB(uc=True, headless=True) as sb:
        try:
            print("🌐 Abriendo la URL base...")
            sb.uc_open_with_reconnect("https://www.comuniate.com/jugadores/comunio", reconnect_time=4)
            sb.sleep(4)

            print("🔄 Forzando el filtro 'LALIGA FANTASY'...")
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

            # Intentamos forzar a mostrar todos los jugadores posibles de golpe
            sb.execute_script("""
                try {
                    var selects = document.querySelectorAll('select');
                    for (var i = 0; i < selects.length; i++) {
                        if (selects[i] && selects[i].name && selects[i].name.includes('length')) {
                            if (selects[i].options && selects[i].options.length > 0) {
                                var lastOpt = selects[i].options[selects[i].options.length - 1];
                                if (lastOpt) {
                                    selects[i].value = lastOpt.value;
                                    selects[i].dispatchEvent(new Event('change', { bubbles: true }));
                                    if (typeof jQuery !== 'undefined') jQuery(selects[i]).trigger('change');
                                }
                            }
                        }
                    }
                } catch(e) { }
            """)
            sb.sleep(4)

            pagina_actual = 1
            while True:
                print(f"📄 Escaneando página {pagina_actual} con el radar todoterreno...")
                html = sb.get_page_source()
                soup = BeautifulSoup(html, 'html.parser')

                # USAMOS EL ESCÁNER QUE SABEMOS QUE FUNCIONA
                elementos_precio = soup.find_all(string=lambda t: t and '€' in t)
                jugadores_en_pagina = 0
                
                for el in elementos_precio:
                    padre = el.parent
                    for _ in range(5): 
                        if padre.name == 'tr' or (padre.name == 'div' and len(padre.find_all('div')) > 2):
                            break
                        if padre.parent:
                            padre = padre.parent
                            
                    textos = [t.get_text(strip=True) for t in padre.find_all(['td', 'div', 'span', 'a', 'strong', 'h3']) if t.get_text(strip=True)]
                    
                    textos_limpios = []
                    for t in textos:
                        if t not in textos_limpios:
                            textos_limpios.append(t)

                    nombre = ""
                    precio = "0 €"
                    pts = "0.0"
                    pos = "JUG"
                    equipo = "Desconocido"

                    # 1. Atrapar Precio
                    for t in textos_limpios:
                        if '€' in t and "RANGO" not in t.upper() and "PRECIO" not in t.upper():
                            precio = t.strip()
                            break

                    # 2. Atrapar Nombre
                    a_tag = padre.find('a')
                    if a_tag and len(a_tag.get_text(strip=True)) > 2:
                        nombre = a_tag.get_text(strip=True)
                    else:
                        for t in textos_limpios:
                            if len(t) > 2 and not any(c.isdigit() for c in t) and '€' not in t and t not in ['POR', 'DEF', 'MED', 'DEL', 'PT', 'DF', 'MC', 'DL']:
                                nombre = t
                                break

                    if not nombre or nombre.upper() in ["VALOR", "JUGADOR", "PUNTOS", "EQUIPO", "POSICIÓN", "MERCADO"]:
                        continue

                    # 3. Atrapar Puntos y Posición real
                    for t in textos_limpios:
                        if len(t) <= 4 and t.replace('.', '').replace(',', '').isdigit():
                            pts = t
                        
                        txt_up = t.upper()
                        # Si vemos las siglas de comunio, las traducimos a tu web
                        if txt_up in ['POR', 'DEF', 'MED', 'DEL', 'PT', 'DF', 'MC', 'DL']:
                            pos_map = {'PT': 'POR', 'DF': 'DEF', 'MC': 'MED', 'DL': 'DEL'}
                            pos = pos_map.get(txt_up, txt_up)

                    # 4. Atrapar Equipo (Buscando en enlaces e imágenes)
                    imgs = padre.find_all('img')
                    for img in imgs:
                        alt = img.get('alt', '').strip()
                        src = img.get('src', '').lower()
                        
                        if alt and alt.upper() not in ["FOTO", "JUGADOR", "AVATAR", nombre.upper()]:
                            equipo = alt.title()
                            break
                        elif 'equipo' in src or 'escudo' in src:
                            equipo_str = src.split('/')[-1].split('.')[0].replace('-', ' ').title()
                            if equipo_str and len(equipo_str) > 2:
                                equipo = equipo_str
                                break
                    
                    if equipo == "Desconocido":
                        enlaces = padre.find_all('a')
                        for en in enlaces:
                            href = en.get('href', '')
                            if '/equipo/' in href:
                                equipo = href.split('/')[-1].replace('-', ' ').title()
                                break
                                
                    if equipo == "Desconocido":
                        equipo = "LaLiga"

                    # Guardamos el jugador en el diccionario si todo cuadra
                    if len(nombre) > 2 and nombre not in jugadores_dict and precio != "0 €":
                        jugadores_dict[nombre] = {
                            "nombre": nombre, "equipo": equipo, "pos": pos,
                            "precio": precio, "subida": "0 €", "pts": pts
                        }
                        jugadores_en_pagina += 1

                print(f"   -> ¡Capturados {jugadores_en_pagina} chollos en la página {pagina_actual}!")

                # --- EL BOTÓN DE SIGUIENTE ---
                # Usamos selectores múltiples para cubrir cualquier diseño de paginación que tengan
                click_exitoso = sb.execute_script("""
                    var nextBtn = document.querySelector('.paginate_button.next, li.next, a[rel="next"]');
                    if (nextBtn && !nextBtn.classList.contains('disabled')) {
                        var link = nextBtn.querySelector('a') || nextBtn;
                        link.click();
                        return true;
                    }
                    return false;
                """)

                if not click_exitoso:
                    print("🛑 No hay botón 'Siguiente' o está deshabilitado. ¡Hemos terminado el asalto!")
                    break
                
                print("➡️ Pasando a la siguiente página...")
                sb.sleep(2) # Pausa cortita para que la tabla actualice
                pagina_actual += 1

                if pagina_actual > 60: # Seguro por si el bucle se vuelve infinito
                    break

        except Exception as e:
            print(f"❌ Error en la ejecución principal: {e}")

    # Función para ordenar los números limpiamente
    def obtener_valor_numerico(precio_str):
        digitos = ''.join(filter(str.isdigit, precio_str))
        return int(digitos) if digitos else 0

    resultado = list(jugadores_dict.values())
    if resultado:
        # Ordenamos de más caro a más barato
        resultado.sort(key=lambda x: obtener_valor_numerico(x["precio"]), reverse=True)
        
        base_datos = {"laliga": {"chollos": resultado}}
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡GOLPE MAESTRO! Se han guardado {len(resultado)} jugadores en tu base de datos.")
    else:
        print("❌ No se encontraron jugadores.")

if __name__ == "__main__":
    extraccion_maestra()