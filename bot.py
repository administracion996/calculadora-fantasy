import json
import time
from playwright.sync_api import sync_playwright

def extraer_por_equipos():
    print("🤖 Iniciando extracción navegando EQUIPO POR EQUIPO en Analítica Fantasy...")
    
    jugadores_dict = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1600, "height": 900}
        )
        page = context.new_page()

        try:
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/mercado", timeout=60000, wait_until="networkidle")
            time.sleep(3)

            # Función para raspar las filas de la tabla visible en pantalla
            def guardar_filas_visibles():
                filas = page.query_selector_all("tbody tr")
                for fila in filas:
                    celdas = fila.query_selector_all("td")
                    if len(celdas) >= 4:
                        lines_nom = celdas[0].inner_text().strip().split("\n")
                        nom = lines_nom[0].strip() if lines_nom else ""

                        # Limpiar número de ranking inicial si existe
                        if nom and nom[0].isdigit():
                            partes = nom.split()
                            if len(partes) > 1 and partes[0].isdigit():
                                nom = " ".join(partes[1:])

                        eq = celdas[1].inner_text().strip().split("\n")[0] if len(celdas) > 1 else "LaLiga"
                        val = celdas[2].inner_text().strip().split("\n")[0] if len(celdas) > 2 else "0 €"
                        sub = celdas[3].inner_text().strip().split("\n")[0] if len(celdas) > 3 else "0 €"
                        pt = celdas[4].inner_text().strip().split("\n")[0] if len(celdas) > 4 else "0.0"

                        if nom and nom not in jugadores_dict:
                            jugadores_dict[nom] = {
                                "nombre": nom,
                                "equipo": eq,
                                "pos": "JUG",
                                "precio": val,
                                "subida": sub,
                                "pts": pt
                            }

            # 1. Guardar los 10 primeros de la portada (TODOS)
            guardar_filas_visibles()
            print(f"📊 Portada leída. Total actual: {len(jugadores_dict)} jugadores.")

            # 2. Localizar los botones del menú lateral de equipos (ATH, ATM, OSA, BAR, RMA, etc.)
            # Buscamos botones o enlaces en la barra lateral
            botones_equipos = page.query_selector_all("aside button, div[class*='sidebar'] button, div[class*='equipos'] button, button:has-text('BAR'), button:has-text('RMA')")

            if not botones_equipos:
                # Intento alternativo para coger los botones por sus abreviaturas de equipo
                siglas = ["ATH", "ATM", "OSA", "LEG", "CEL", "ALA", "BAR", "GET", "GIR", "RAY", "ESP", "MALL", "BET", "RMA", "RSO", "VLL", "SEV", "LPA", "VAL", "VIL"]
                botones_equipos = []
                for sigla in siglas:
                    btn = page.query_selector(f"button:has-text('{sigla}'), a:has-text('{sigla}')")
                    if btn:
                        botones_equipos.append(btn)

            print(f"🎯 Detectados {len(botones_equipos)} botones de equipos en el menú lateral.")

            # 3. Recorrer los botones de cada equipo haciendo clic
            for i, btn in enumerate(botones_equipos):
                try:
                    txt_btn = btn.inner_text().strip().replace("\n", "")
                    btn.click(force=True)
                    time.sleep(1.2)  # Esperar a que reaccione la tabla
                    
                    cant_antes = len(jugadores_dict)
                    guardar_filas_visibles()
                    nuevos = len(jugadores_dict) - cant_antes
                    
                    print(f"⚽ [{i+1}/{len(botones_equipos)}] Clic en equipo '{txt_btn}': +{nuevos} jugadores (Total: {len(jugadores_dict)})")
                except Exception as err:
                    print(f"⚠️ No se pudo clicar en el botón {i+1}: {err}")

            resultado = list(jugadores_dict.values())

            if resultado:
                base_datos = {"laliga": {"chollos": resultado}}
                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump(base_datos, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡ÉXITO ROTUNDO! Guardados {len(resultado)} jugadores en total recabados por equipos.")
            else:
                print("❌ No se pudieron leer los datos.")

        except Exception as e:
            print(f"❌ Error durante la extracción: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    extraer_por_equipos()