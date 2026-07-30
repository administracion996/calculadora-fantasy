import json
import re
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def extraer_html_quirurgico():
    print("🤖 Obteniendo el HTML completo de Analítica Fantasy...")
    
    html_contenido = ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 10800}
        )
        page = context.new_page()

        try:
            page.goto("https://www.analiticafantasy.com/fantasy-la-liga/mercado", timeout=60000, wait_until="domcontentloaded")
            time.sleep(5)

            # Scroll para asegurar renderizado
            for _ in range(10):
                page.evaluate("window.scrollBy(0, 1500)")
                time.sleep(0.3)

            html_contenido = page.content()

        except Exception as e:
            print(f"❌ Error al cargar la página: {e}")
        finally:
            browser.close()

    if not html_contenido:
        print("❌ No se pudo capturar el HTML.")
        return

    print("🔍 Analizando el HTML con BeautifulSoup...")
    soup = BeautifulSoup(html_contenido, 'html.parser')
    
    jugadores_dict = {}

    # 1. Buscar en TODAS las filas de tablas presentes en el HTML
    filas = soup.find_all('tr')
    for fila in filas:
        celdas = fila.find_all(['td', 'th'])
        if len(celdas) >= 3:
            textos = [c.get_text(strip=True) for c in celdas if c.get_text(strip=True)]
            if len(textos) >= 3:
                nombre = textos[0]
                
                if nombre and nombre[0].isdigit():
                    partes = nombre.split()
                    if len(partes) > 1 and partes[0].isdigit():
                        nombre = " ".join(partes[1:])

                if nombre.upper() in ["JUGADOR", "NOMBRE", "POS", "EQUIPO", "VALOR"]:
                    continue

                equipo = textos[1] if len(textos) > 1 else "LaLiga"
                precio = textos[2] if len(textos) > 2 else "0 €"
                subida = textos[3] if len(textos) > 3 else "0 €"
                pts = textos[4] if len(textos) > 4 else "0.0"

                if nombre and len(nombre) > 2:
                    jugadores_dict[nombre] = {
                        "nombre": nombre,
                        "equipo": equipo,
                        "pos": "JUG",
                        "precio": precio,
                        "subida": subida,
                        "pts": pts
                    }

    # 2. Buscar bloques div o componentes de jugador con indentación corregida
    tarjetas = soup.find_all('div', class_=re.compile(r'player|jugador|card|item', re.I))
    for t in tarjetas:
        txt = t.get_text(" ", strip=True)
        if "€" in txt:
            partes = txt.split()
            if len(partes) >= 2:
                nom = partes[0]
                if nom not in jugadores_dict and len(nom) > 2 and not nom.isdigit():
                    jugadores_dict[nom] = {
                        "nombre": nom,
                        "equipo": "LaLiga",
                        "pos": "JUG",
                        "precio": "0 €",
                        "subida": "0 €",
                        "pts": "0.0"
                    }

    resultado = list(jugadores_dict.values())

    if resultado:
        base_datos = {"laliga": {"chollos": resultado}}
        with open("datos.json", "w", encoding="utf-8") as f:
            json.dump(base_datos, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡ÉXITO DEFINITIVO! Guardados {len(resultado)} jugadores extraídos del HTML nativo.")
    else:
        print("❌ No se pudieron procesar elementos del HTML.")

if __name__ == "__main__":
    extraer_html_quirurgico()