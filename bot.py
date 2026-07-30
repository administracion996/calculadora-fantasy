import json
import time
from playwright.sync_api import sync_playwright

def extraer_mercado_analitica_definitivo():
    print("🤖 Iniciando extracción con los selectores exactos de Analítica Fantasy...")
    
    jugadores_dict = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1600, "height": 1000}
        )
        page = context.new_page()

        try:
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/mercado", timeout=60000, wait_until="networkidle")
            time.sleep(3)

            # Función interna para leer las filas visibles en pantalla en cada instante
            def leer_filas():
                filas = page.query_selector_all("tbody tr")
                for fila in filas:
                    celdas = fila.query_selector_all("td")
                    if len(celdas) >= 4:
                        lines_nom = celdas[0].inner_text().strip().split("\n")
                        nom = lines_nom[0].strip() if lines_nom else ""

                        # Limpiar número de ranking inicial (ej: "1 José Bordalás" -> "José Bordalás")
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

            # 1. Leer los 10 primeros de la portada
            leer_filas()
            print(f"📌 Portada leída: {len(jugadores_dict)} jugadores acumulados.")

            # 2. ESTRATEGIA A: Navegar por los botones del menú lateral de equipos (ATH, BAR, RMA...)
            siglas = ["TODOS", "ATH", "ATM", "OSA", "LEG", "CEL", "ALA", "BAR", "GET", "GIR", "RAY", "ESP", "MALL", "BET", "RMA", "RSO", "VLL", "SEV", "LPA", "VAL", "VIL"]
            
            click_equipos_exitoso = False
            for sigla in siglas:
                try:
                    # Buscar cualquier elemento (div, button, a, span) que contenga exactamente la sigla del equipo
                    elem = page.query_selector(f"xpath=//*[text()='{sigla}']")
                    if elem and elem.is_visible():
                        elem.click(force=True)
                        time.sleep(1.2)
                        cant_antes = len(jugadores_dict)
                        leer_filas()
                        nuevos = len(jugadores_dict) - cant_antes
                        print(f"⚽ Clic en equipo '{sigla}': +{nuevos} nuevos (Total: {len(jugadores_dict)})")
                        click_equipos_exitoso = True
                except Exception:
                    pass

            # 3. ESTRATEGIA B: Si la estrategia de equipos no sumó suficientes, avanzar pulsando en '→Próx.'
            if len(jugadores_dict) <= 15:
                print("🔄 Probando paginación mediante botón '→Próx.'...")
                pag = 1
                while pag <= 50:
                    bot_next = page.query_selector("xpath=//*[contains(text(), 'Próx') or contains(text(), '→')]")
                    if bot_next and bot_next.is_visible():
                        cant_antes = len(jugadores_dict)
                        bot_next.click(force=True)
                        time.sleep(1.5)
                        leer_filas()
                        nuevos = len(jugadores_dict) - cant_antes
                        print(f"➡️ Paginación {pag}: +{nuevos} nuevos (Total: {len(jugadores_dict)})")
                        
                        if nuevos == 0 and pag > 3:
                            print("🏁 No hay más páginas con jugadores nuevos.")
                            break
                        pag += 1
                    else:
                        break

            resultado = list(jugadores_dict.values())

            if resultado:
                base_datos = {"laliga": {"chollos": resultado}}
                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump(base_datos, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡ÉXITO TOTAL! Guardados {len(resultado)} jugadores en total.")
            else:
                print("❌ No se pudieron capturar jugadores.")

        except Exception as e:
            print(f"❌ Error durante el proceso: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    extraer_mercado_analitica_definitivo()