import json
from seleniumbase import SB
from bs4 import BeautifulSoup

def extraccion_comuniate_filtro_exacto():
    print("🤖 Entrando a Comuniate para accionar el filtro de LaLiga Fantasy...")
    jugadores_dict = {}

    # Usamos SeleniumBase de fondo para poder interactuar con los desplegables
    with SB(uc=True, headless=True) as sb:
        try:
            # 1. Vamos a la URL exacta que nos has pasado
            print("🌐 Abriendo la URL base...")
            sb.uc_open_with_reconnect("https://www.comuniate.com/jugadores/comunio", reconnect_time=4)
            sb.sleep(3)

            # 2. LA MAGIA: Hacemos clic en el desplegable de tu captura de pantalla
            print("🔄 Seleccionando el filtro 'LALIGA FANTASY DAZN'...")
            sb.execute_script("""
                let selects = document.querySelectorAll('select');
                for(let s of selects) {
                    for(let o of s.options) {
                        if(o.text.toUpperCase().includes('LALIGA FANTASY DAZN')) {
                            s.value = o.value;
                            s.dispatchEvent(new Event('change', {bubbles: true}));
                            break;
                        }
                    }
                }
            """)
            sb.sleep(4) # Esperamos 4 segundos a que la tabla cambie los datos de Comunio a Fantasy

            # 3. Forzamos el segundo desplegable (el de paginación) para mostrar TODOS los jugadores
            print("📜 Expandiendo la tabla para que no muestre solo 10...")
            sb.execute_script("""
                let selects = document.querySelectorAll('select');
                for(let s of selects) {
                    // Los desplegables de paginación suelen tener 'length' en su name
                    if(s.name && s.name.includes('length')) {
                        // Seleccionamos la última opción (suele ser "Todos" o "100")
                        s.value = s.options[s.options.length - 1].value;
                        s.dispatchEvent(new Event('change', {bubbles: true}));
                    }
                }
            """)
            sb.sleep(3) # Esperamos a que carguen todos los jugadores de golpe

            # 4. Le pasamos el código HTML a BeautifulSoup para leerlo a la velocidad de la luz
            print("🔍 Analizando la tabla extraída...")
            html = sb.get_page_source()
            soup = BeautifulSoup(html, 'html.parser')

            filas = soup.find_all('tr')
            for fila in filas:
                celdas = fila.find_all(['td', 'th'])
                textos = [c.get_text(strip=True) for c in celdas if c.get_text(strip=True)]

                if len(textos) >= 3:
                    # Buscar el nombre (normalmente es un enlace)
                    nombre = ""
                    a_tag = fila.find('a')
                    if a_tag and len(a_tag.get_text(strip=True)) > 2:
                        nombre = a_tag.get_text(strip=True)
                    else:
                        for t in textos:
                            if len(t) > 3 and not t.replace('.', '').isdigit() and '€' not in t:
                                nombre = t
                                break

                    # Si es la cabecera de la tabla, la saltamos
                    if not nombre or nombre.upper() in ["JUGADOR", "POSICIÓN", "EQUIPO", "PUNTOS", "VALOR", "NOMBRE"]:
                        continue

                    # Buscar el equipo extrayendo el "alt" de la foto del escudo
                    equipo = "LaLiga"
                    imgs = fila.find_all('img')
                    for img in imgs:
                        alt = img.get('alt', '').upper()
                        if alt and len(alt) > 2 and 'FOTO' not in alt and 'AVATAR' not in alt:
                            equipo = alt.title()
                            break

                    # Identificar variables heurísticamente (precio, posición, puntos)
                    pos = "JUG"
                    precio = "0 €"
                    pts = "0.0"

                    for txt in textos:
                        txt_up = txt.upper()
                        if txt_up in ['POR', 'DEF', 'MED', 'DEL', 'PT', 'DF', 'MC', 'DL']:
                            pos_map = {'PT': 'POR', 'DF': 'DEF', 'MC': 'MED', 'DL': 'DEL'}
                            pos = pos_map.get(txt_up, txt_up)
                        
                        elif '€' in txt or (txt.replace('.', '').replace(',', '').isdigit() and len(txt.replace('.', '')) >= 5):
                            val_limpio = txt.replace('€', '').replace('.', '').replace(',', '').strip()
                            if val_limpio.isdigit():
                                precio = f"{int(val_limpio):,} €".replace(',', '.')
                        
                        elif len(txt) <= 4 and txt.replace('.', '').replace(',', '').isdigit():
                            pts = txt

                    if nombre not in jugadores_dict:
                        jugadores_dict[nombre] = {
                            "nombre": nombre,
                            "equipo": equipo,
                            "pos": pos,
                            "precio": precio,
                            "subida": "0 €", # La subida no suele salir en esta vista general
                            "pts": pts
                        }

        except Exception as e:
            print(f"❌ Error durante el asalto: {e}")

    # Guardado de datos
    resultado = list(jugadores_dict.values())
    if resultado:
        # Ordenar por precio descendente
        resultado.sort(key=lambda x: int(x["precio"].replace(" €", "").replace(".", "")) if "€" in x["precio"] else 0, reverse=True)
        
        base_datos = {"laliga": {"chollos": resultado}}
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡GOLPE MAESTRO! Extraídos {len(resultado)} jugadores con el filtro de LaLiga Fantasy.")
    else:
        print("❌ No se guardó ningún jugador. La tabla podría estar vacía o bloqueada.")

if __name__ == "__main__":
    extraccion_comuniate_filtro_exacto()