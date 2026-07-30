import json
from seleniumbase import SB
from bs4 import BeautifulSoup

def extraccion_todoterreno_comuniate():
    print("🤖 Activando Escáner Todoterreno en Comuniate...")
    jugadores_dict = {}

    with SB(uc=True, headless=True) as sb:
        try:
            print("🌐 Abriendo la URL base...")
            sb.uc_open_with_reconnect("https://www.comuniate.com/jugadores/comunio", reconnect_time=4)
            sb.sleep(4)

            print("🔄 Forzando el filtro 'LALIGA FANTASY' a todos los niveles...")
            # Disparamos todos los eventos posibles (Vanilla JS y jQuery) para que la web despierte
            sb.execute_script("""
                var selects = document.querySelectorAll('select');
                for (var i = 0; i < selects.length; i++) {
                    for (var j = 0; j < selects[i].options.length; j++) {
                        if (selects[i].options[j].text.toUpperCase().includes('LALIGA FANTASY')) {
                            selects[i].value = selects[i].options[j].value;
                            selects[i].dispatchEvent(new Event('change', { bubbles: true }));
                            if (typeof jQuery !== 'undefined') {
                                jQuery(selects[i]).trigger('change');
                            }
                        }
                    }
                }
            """)
            sb.sleep(5) 

            # Intentamos forzar que se muestren "Todos" o "100" por página
            sb.execute_script("""
                var selects = document.querySelectorAll('select');
                for (var i = 0; i < selects.length; i++) {
                    if (selects[i].name && selects[i].name.includes('length')) {
                        selects[i].value = selects[i].options[selects[i].options.length - 1].value;
                        selects[i].dispatchEvent(new Event('change', { bubbles: true }));
                        if (typeof jQuery !== 'undefined') jQuery(selects[i]).trigger('change');
                    }
                }
            """)
            sb.sleep(5) 

            print("🔍 Escaneando la pantalla a ciegas buscando el símbolo '€'...")
            html = sb.get_page_source()
            soup = BeautifulSoup(html, 'html.parser')

            # HEURÍSTICA: Buscar directamente el símbolo del dinero, sin importar si es tabla o div
            elementos_precio = soup.find_all(string=lambda t: t and '€' in t)
            
            for el in elementos_precio:
                # Subimos por el código HTML hasta atrapar la fila entera (el contenedor del jugador)
                padre = el.parent
                for _ in range(5): 
                    if padre.name == 'tr' or (padre.name == 'div' and len(padre.find_all('div')) > 2):
                        break
                    if padre.parent:
                        padre = padre.parent
                        
                # Extraemos todo el texto limpio que haya en esa fila
                textos = [t.get_text(strip=True) for t in padre.find_all(['td', 'div', 'span', 'a', 'strong', 'h3']) if t.get_text(strip=True)]
                
                # Borramos textos duplicados manteniendo el orden
                textos_limpios = []
                for t in textos:
                    if t not in textos_limpios:
                        textos_limpios.append(t)

                nombre = ""
                precio = "0 €"
                pts = "0.0"
                pos = "JUG"
                equipo = "LaLiga"

                # 1. Atrapar Precio
                for t in textos_limpios:
                    if '€' in t:
                        precio = t.strip()
                        break

                # 2. Atrapar Nombre (Suele ser un enlace <a> o el texto más largo sin números)
                a_tag = padre.find('a')
                if a_tag and len(a_tag.get_text(strip=True)) > 2:
                    nombre = a_tag.get_text(strip=True)
                else:
                    for t in textos_limpios:
                        if len(t) > 2 and not any(c.isdigit() for c in t) and '€' not in t and t not in ['POR', 'DEF', 'MED', 'DEL', 'PT', 'DF', 'MC', 'DL']:
                            nombre = t
                            break

                # Filtro de seguridad para evitar cazar cabeceras
                if not nombre or nombre.upper() in ["VALOR", "JUGADOR", "PUNTOS", "EQUIPO", "POSICIÓN", "MERCADO"]:
                    continue

                # 3. Atrapar Puntos y Posición
                for t in textos_limpios:
                    if len(t) <= 4 and t.replace('.', '').isdigit():
                        pts = t
                    txt_up = t.upper()
                    if txt_up in ['POR', 'DEF', 'MED', 'DEL', 'PT', 'DF', 'MC', 'DL']:
                        pos_map = {'PT': 'POR', 'DF': 'DEF', 'MC': 'MED', 'DL': 'DEL'}
                        pos = pos_map.get(txt_up, txt_up)

                # 4. Atrapar Equipo (buscando la imagen del escudo)
                imgs = padre.find_all('img')
                for img in imgs:
                    alt = img.get('alt', '').upper()
                    if alt and 'FOTO' not in alt and 'JUGADOR' not in alt and 'AVATAR' not in alt:
                        equipo = alt.title()
                        break

                if len(nombre) > 2 and nombre not in jugadores_dict:
                    jugadores_dict[nombre] = {
                        "nombre": nombre, "equipo": equipo, "pos": pos,
                        "precio": precio, "subida": "0 €", "pts": pts
                    }

        except Exception as e:
            print(f"❌ Error en la matriz: {e}")

    # Guardado Final
    resultado = list(jugadores_dict.values())
    if resultado:
        # Ordenamos los jugadores por precio (del más caro al más barato)
        resultado.sort(key=lambda x: int(x["precio"].replace(" €", "").replace(".", "")) if "€" in x["precio"] else 0, reverse=True)
        
        base_datos = {"laliga": {"chollos": resultado}}
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡ÉXITO TODOTERRENO! El radar capturó a {len(resultado)} jugadores.")
    else:
        print("❌ El radar no encontró el símbolo '€' en la página. La web no cargó la tabla.")

if __name__ == "__main__":
    extraccion_todoterreno_comuniate()