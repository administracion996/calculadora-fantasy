import json
import time
from playwright.sync_api import sync_playwright

def extraccion_modo_humano():
    print("🤖 Iniciando modo 'Simulador Humano' anti-bloqueos...")
    jugadores_dict = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/mercado", wait_until="networkidle", timeout=60000)
            time.sleep(4)

            # 1. Cerrar banners de cookies para que no tapen los botones
            try:
                page.evaluate("""() => {
                    document.querySelectorAll('button').forEach(b => {
                        if (b.innerText.match(/aceptar|agree|entendido/i)) b.click();
                    });
                }""")
                time.sleep(1)
            except:
                pass

            # 2. Forzar el desplegable a mostrar el máximo de filas (si existe)
            try:
                page.evaluate("""() => {
                    const selects = document.querySelectorAll('select');
                    selects.forEach(s => {
                        if (s.options.length > 0) {
                            s.selectedIndex = s.options.length - 1;
                            s.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    });
                }""")
                time.sleep(2)
            except:
                pass

            # Bucle de paginación (máximo 60 páginas por seguridad)
            for pag in range(1, 60):
                print(f"📄 Leyendo página {pag}...")
                
                # Esperar a que la tabla exista
                page.wait_for_selector("tbody tr", timeout=10000)
                filas = page.query_selector_all("tbody tr")
                
                primer_jugador_actual = ""
                
                for i, fila in enumerate(filas):
                    celdas = fila.query_selector_all("td")
                    if len(celdas) >= 4:
                        nombre = celdas[0].inner_text().strip().split('\n')[0]
                        # Limpiar números de ranking
                        if nombre and nombre[0].isdigit():
                            partes = nombre.split()
                            if len(partes) > 1 and partes[0].isdigit():
                                nombre = " ".join(partes[1:])
                                
                        if i == 0:
                            primer_jugador_actual = nombre

                        eq = celdas[1].inner_text().strip().split('\n')[0] if len(celdas) > 1 else "LaLiga"
                        val = celdas[2].inner_text().strip().split('\n')[0] if len(celdas) > 2 else "0 €"
                        sub = celdas[3].inner_text().strip().split('\n')[0] if len(celdas) > 3 else "0 €"
                        pt = celdas[4].inner_text().strip().split('\n')[0] if len(celdas) > 4 else "0.0"

                        if nombre:
                            jugadores_dict[nombre] = {
                                "nombre": nombre, "equipo": eq, "pos": "JUG",
                                "precio": val, "subida": sub, "pts": pt
                            }

                print(f"✅ Acumulados: {len(jugadores_dict)} jugadores.")

                # 3. Hacer clic en "Siguiente" buscando flechas o texto
                accion = page.evaluate("""() => {
                    const botones = Array.from(document.querySelectorAll('button, a, div[role="button"], li'));
                    const btnSiguiente = botones.find(b => {
                        const txt = (b.innerText || '').trim().toLowerCase();
                        const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                        return txt === '>' || txt === '»' || txt.includes('próx') || txt.includes('siguiente') || aria.includes('next');
                    });
                    
                    if (btnSiguiente && !btnSiguiente.hasAttribute('disabled') && !btnSiguiente.className.includes('disabled')) {
                        btnSiguiente.click();
                        return 'clic';
                    }
                    return 'nada';
                }""")

                if accion == 'nada':
                    print("🏁 Fin de la tabla (botón de página siguiente no encontrado o deshabilitado).")
                    break

                # 4. LA CLAVE DEL ÉXITO: Esperar a que la tabla cambie de verdad
                try:
                    if primer_jugador_actual:
                        # Convertimos el nombre para que no rompa el código JS
                        nombre_js = primer_jugador_actual.replace("'", "\\'").replace('"', '\\"')
                        
                        # Python se congela aquí hasta que el primer nombre de la tabla ya NO sea el mismo
                        page.wait_for_function(f"""() => {{
                            const celda = document.querySelector('tbody tr td');
                            if (!celda) return false;
                            return !celda.innerText.includes('{nombre_js}');
                        }}""", timeout=8000)
                    time.sleep(0.5) # Dejar que termine de pintar
                except Exception:
                    print("⚠️ La tabla no se actualizó tras pulsar Siguiente. Rompiendo bucle para evitar duplicados.")
                    break

            resultado = list(jugadores_dict.values())
            
            if resultado:
                base_datos = {"laliga": {"chollos": resultado}}
                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump(base_datos, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡MISIÓN CUMPLIDA! Extraídos {len(resultado)} jugadores en total.")
            else:
                print("❌ No se guardó ningún jugador.")

        except Exception as e:
            print(f"❌ Error crítico: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    extraccion_modo_humano()