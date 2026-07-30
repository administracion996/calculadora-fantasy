import json
from seleniumbase import SB
from bs4 import BeautifulSoup

def extraccion_todoterreno_blindada():
    print("🤖 Activando Escáner Todoterreno (Versión Blindada Antierrores)...")
    jugadores_dict = {}

    with SB(uc=True, headless=True) as sb:
        try:
            print("🌐 Abriendo la URL base...")
            sb.uc_open_with_reconnect("https://www.comuniate.com/jugadores/comunio", reconnect_time=4)
            sb.sleep(4)

            print("🔄 Forzando el filtro 'LALIGA FANTASY' con escudos activados...")
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
                } catch(e) { console.log('Error silenciado al cambiar juego'); }
            """)
            sb.sleep(5) 

            print("📜 Expandiendo la paginación a 'Todos' de forma segura...")
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
                } catch(e) { console.log('Error silenciado al expandir tabla'); }
            """)
            sb.sleep(5) 

            print("🔍 Escaneando la pantalla buscando el símbolo '€'...")
            html = sb.get_page_source()
            soup = BeautifulSoup(html, 'html.parser')

            elementos_precio = soup.find_all(string=lambda t: t and '€' in t)
            
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
                equipo = "LaLiga"

                for t in textos_limpios:
                    # Filtramos para no coger el filtro de rangos de precio de la web
                    if '€' in t and "RANGO" not in t.upper() and "PRECIO" not in t.upper():
                        precio = t.strip()
                        break

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

                for t in textos_limpios:
                    if len(t) <= 4 and t.replace('.', '').isdigit():
                        pts = t
                    txt_up = t.upper()
                    if txt_up in ['POR', 'DEF', 'MED', 'DEL', 'PT', 'DF', 'MC', 'DL']:
                        pos_map = {'PT': 'POR', 'DF': 'DEF', 'MC': 'MED', 'DL': 'DEL'}
                        pos = pos_map.get(txt_up, txt_up)

                imgs = padre.find_all('img')
                for img in imgs:
                    alt = img.get('alt', '').upper()
                    if alt and 'FOTO' not in alt and 'JUGADOR' not in alt and 'AVATAR' not in alt:
                        equipo = alt.title()
                        break

                if len(nombre) > 2 and nombre not in jugadores_dict and precio != "0 €":
                    jugadores_dict[nombre] = {
                        "nombre": nombre, "equipo": equipo, "pos": pos,
                        "precio": precio, "subida": "0 €", "pts": pts
                    }

        except Exception as e:
            print(f"❌ Error en la ejecución principal: {e}")

    # --- NUEVA FUNCIÓN DE ORDENADO SEGURO ---
    def obtener_valor_numerico(precio_str):
        # Filtra el string y se queda SOLO con los números. Evita que Python explote.
        digitos = ''.join(filter(str.isdigit, precio_str))
        return int(digitos) if digitos else 0

    resultado = list(jugadores_dict.values())
    if resultado:
        # Usamos la función blindada para ordenar
        resultado.sort(key=lambda x: obtener_valor_numerico(x["precio"]), reverse=True)
        
        base_datos = {"laliga": {"chollos": resultado}}
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡ÉXITO! El radar capturó y ordenó limpiamente a {len(resultado)} jugadores.")
    else:
        print("❌ El radar escaneó la página, pero no encontró precios válidos.")

if __name__ == "__main__":
    extraccion_todoterreno_blindada()
    