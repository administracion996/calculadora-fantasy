import json
import time
from playwright.sync_api import sync_playwright

def extraer_mercado_completo():
    print("🤖 Navegando a Analítica Fantasy para extraer el objeto de datos completo...")
    
    jugadores_totales = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # Cargar la página
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/mercado", timeout=60000, wait_until="networkidle")
            time.sleep(5)

            # Extraer directamente del objeto JS interno __NEXT_DATA__ de la página web
            datos_js = page.evaluate("""() => {
                try {
                    const el = document.getElementById('__NEXT_DATA__');
                    if (el) return JSON.parse(el.textContent);
                } catch (e) {}
                return null;
            }""")

            if datos_js:
                print("📦 Objeto __NEXT_DATA__ localizado. Buscando la lista de jugadores...")
                
                # Función para buscar la lista masiva dentro de la estructura de Next.js
                def buscar_lista(obj):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if isinstance(v, list) and len(v) > 20 and isinstance(v[0], dict):
                                return v
                            res = buscar_lista(v)
                            if res: return res
                    elif isinstance(obj, list):
                        for item in obj:
                            res = buscar_lista(item)
                            if res: return res
                    return None

                raw_list = buscar_lista(datos_js)
                
                if raw_list:
                    for p_item in raw_list:
                        nombre = p_item.get("nickname", p_item.get("name", "Jugador"))
                        equipo = p_item.get("teamName", p_item.get("team", {}).get("name", "LaLiga"))
                        pos = str(p_item.get("position", "MED"))
                        
                        pos_map = {"1": "POR", "2": "DEF", "3": "MED", "4": "DEL"}
                        pos = pos_map.get(pos, pos)
                        
                        precio = p_item.get("marketValue", p_item.get("price", 0))
                        incremento = p_item.get("marketValueIncrement", p_item.get("priceIncrement", 0))
                        puntos = str(p_item.get("pointsAverage", p_item.get("points", 0)))

                        if isinstance(incremento, (int, float)):
                            str_subida = f"+ {incremento:,} €".replace(',', '.') if incremento >= 0 else f"- {abs(incremento):,} €".replace(',', '.')
                        else:
                            str_subida = str(incremento)

                        str_precio = f"{precio:,} €".replace(',', '.') if isinstance(precio, (int, float)) else str(precio)

                        jugadores_totales.append({
                            "nombre": nombre,
                            "equipo": equipo,
                            "pos": pos,
                            "precio": str_precio,
                            "subida": str_subida,
                            "pts": puntos
                        })

            # Si la extracción por __NEXT_DATA__ falló, intentamos hacer scroll progresivo evaluando la tabla en vivo
            if not jugadores_totales:
                print("⚠️ Buscando mediante scroll y evaluación continua en el cliente...")
                jugadores_dict = {}

                for _ in range(15):
                    # Forzar scroll
                    page.evaluate("window.scrollBy(0, 1500)")
                    time.sleep(1)

                    # Extraer del DOM los elementos cargados dinámicamente
                    filas_data = page.evaluate("""() => {
                        const trs = document.querySelectorAll('tbody tr');
                        const data = [];
                        trs.forEach(tr => {
                            const tds = tr.querySelectorAll('td');
                            if (tds.length >= 4) {
                                data.push({
                                    nombre: tds[0].innerText.trim().split('\\n')[0],
                                    equipo: tds[1] ? tds[1].innerText.trim().split('\\n')[0] : 'LaLiga',
                                    precio: tds[2] ? tds[2].innerText.trim().split('\\n')[0] : '0 €',
                                    subida: tds[3] ? tds[3].innerText.trim().split('\\n')[0] : '0 €',
                                    pts: tds[4] ? tds[4].innerText.trim().split('\\n')[0] : '0.0'
                                });
                            }
                        });
                        return data;
                    }""")

                    for item in filas_data:
                        nom = item["nombre"]
                        if nom and nom[0].isdigit():
                            partes = nom.split()
                            if len(partes) > 1 and partes[0].isdigit():
                                nom = " ".join(partes[1:])

                        if nom and nom not in jugadores_dict:
                            jugadores_dict[nom] = {
                                "nombre": nom,
                                "equipo": item["equipo"],
                                "pos": "JUG",
                                "precio": item["precio"],
                                "subida": item["subida"],
                                "pts": item["pts"]
                            }

                jugadores_totales = list(jugadores_dict.values())

            if jugadores_totales:
                base_datos = {"laliga": {"chollos": jugadores_totales}}
                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump(base_datos, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡ÉXITO! Extraídos {len(jugadores_totales)} jugadores de Analítica Fantasy.")
            else:
                print("❌ No se pudieron obtener jugadores.")

        except Exception as e:
            print(f"❌ Error durante la extracción: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    extraer_mercado_completo()