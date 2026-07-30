import json
from seleniumbase import SB
from bs4 import BeautifulSoup

def extraccion_comuniate_robusta():
    print("🤖 Entrando a Comuniate (Modo jQuery y Extracción Robusta)...")
    jugadores_dict = {}

    with SB(uc=True, headless=True) as sb:
        try:
            print("🌐 Abriendo la URL base...")
            sb.uc_open_with_reconnect("https://www.comuniate.com/jugadores/comunio", reconnect_time=4)
            sb.sleep(4)

            print("🔄 Cambiando el motor a LaLiga Fantasy DAZN (Vía jQuery)...")
            # Forzamos el cambio usando jQuery (el lenguaje nativo de la web) para que reaccione
            sb.execute_script("""
                if (typeof jQuery != 'undefined') {
                    var $select = jQuery('select').filter(function() {
                        return jQuery(this).text().indexOf('LALIGA FANTASY DAZN') > -1;
                    });
                    if ($select.length) {
                        var val = $select.find('option:contains("LALIGA FANTASY DAZN")').val();
                        $select.val(val).trigger('change');
                    }
                }
            """)
            sb.sleep(5) # Vital esperar a que el servidor de Comuniate mande los nuevos jugadores

            print("📜 Expandiendo la paginación de la tabla al máximo...")
            sb.execute_script("""
                if (typeof jQuery != 'undefined') {
                    var $lenSelect = jQuery('select[name$="length"]');
                    if ($lenSelect.length) {
                        $lenSelect.val($lenSelect.find('option:last').val()).trigger('change');
                    }
                }
            """)
            sb.sleep(5) # Esperar a que se pinte la tabla gigante

            print("🔍 Leyendo el código fuente de la tabla...")
            html = sb.get_page_source()
            soup = BeautifulSoup(html, 'html.parser')

            # Buscamos todas las tablas y filtramos las filas de datos reales
            tablas = soup.find_all('table')
            for tabla in tablas:
                filas = tabla.find_all('tr')
                for fila in filas:
                    celdas = fila.find_all('td')
                    
                    # Una fila válida de jugadores suele tener al menos 4 columnas
                    if len(celdas) >= 4:
                        textos = [c.get_text(strip=True, separator=" ") for c in celdas]
                        
                        nombre = ""
                        # Normalmente el nombre está en un enlace (etiqueta <a>)
                        a_tag = fila.find('a')
                        if a_tag and len(a_tag.get_text(strip=True)) > 2:
                            nombre = a_tag.get_text(strip=True)
                        else:
                            # Plan B: buscar el texto más largo que no tenga números (suele ser el nombre)
                            for txt in textos:
                                if len(txt) > 3 and not any(char.isdigit() for char in txt) and '€' not in txt:
                                    nombre = txt
                                    break

                        if not nombre or nombre.upper() in ["JUGADOR", "NOMBRE", "EQUIPO", "POSICIÓN"]:
                            continue

                        # Identificar el precio (buscando el símbolo del euro o números grandes)
                        precio = "0 €"
                        for txt in textos:
                            if '€' in txt:
                                precio = txt.replace('€', '').strip() + " €"
                            elif len(txt.replace('.', '').replace(',', '')) >= 6 and txt.replace('.', '').isdigit():
                                precio = txt.strip() + " €"

                        # Identificar puntos (números pequeños de 1 a 4 dígitos)
                        pts = "0.0"
                        for txt in textos:
                            if len(txt) <= 4 and txt.replace('.', '').isdigit():
                                pts = txt

                        # Identificar la posición
                        pos = "JUG"
                        for txt in textos:
                            txt_up = txt.upper()
                            if txt_up in ['POR', 'DEF', 'MED', 'DEL', 'PT', 'DF', 'MC', 'DL']:
                                pos_map = {'PT': 'POR', 'DF': 'DEF', 'MC': 'MED', 'DL': 'DEL'}
                                pos = pos_map.get(txt_up, txt_up)

                        # Extraer el equipo (del texto alternativo del escudo del equipo)
                        equipo = "LaLiga"
                        imgs = fila.find_all('img')
                        for img in imgs:
                            alt = img.get('alt', '')
                            if alt and 'FOTO' not in alt.upper() and 'JUGADOR' not in alt.upper():
                                equipo = alt.title()
                                break

                        # Lo guardamos en nuestra base de datos si es válido
                        if nombre not in jugadores_dict:
                            jugadores_dict[nombre] = {
                                "nombre": nombre, "equipo": equipo, "pos": pos,
                                "precio": precio, "subida": "0 €", "pts": pts
                            }
                            
        except Exception as e:
            print(f"❌ Error crítico en la matriz: {e}")

    # Guardado de la base de datos
    resultado = list(jugadores_dict.values())
    if resultado:
        # Ordenamos los chollos de más caro a más barato para tu web
        resultado.sort(key=lambda x: int(x["precio"].replace(" €", "").replace(".", "")) if "€" in x["precio"] else 0, reverse=True)
        
        base_datos = {"laliga": {"chollos": resultado}}
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡MISIÓN CUMPLIDA! Extraídos {len(resultado)} jugadores con éxito.")
    else:
        print("❌ El robot se ha quedado ciego de nuevo. No pudo extraer las celdas de la tabla.")

if __name__ == "__main__":
    extraccion_comuniate_robusta()