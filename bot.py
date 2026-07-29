import json
import requests
from bs4 import BeautifulSoup

def obtener_precios_reales():
    print("🤖 Conectando a la web de mercado para descargar los precios reales...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Estructura final donde guardaremos todo
    datos = {
        "biwenger": {"chollos": []},
        "laliga": {"chollos": []},
        "comunio": {"chollos": []}
    }

    try:
        # Petición a la web de mercado real (Comuniate / Analistas)
        url = "https://www.comuniate.com/mercado/biwenger"
        respuesta = requests.get(url, headers=headers, timeout=10)

        if respuesta.status_code == 200:
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            
            # Buscamos las filas de la tabla de mercado
            filas = soup.find_all('tr')
            jugadores_encontrados = []

            for fila in filas:
                cols = fila.find_all('td')
                if len(cols) >= 4:
                    nombre = cols[0].text.strip()
                    equipo = cols[1].text.strip()
                    precio = cols[2].text.strip()
                    subida = cols[3].text.strip()

                    if nombre and precio:
                        jugadores_encontrados.append({
                            "nombre": nombre,
                            "equipo": equipo if equipo else "LaLiga",
                            "pos": "JUG",
                            "precio": precio,
                            "subida": subida,
                            "pts": "0.0"
                        })

            if jugadores_encontrados:
                print(f"✅ ¡Se han extraído {len(jugadores_encontrados)} jugadores reales!")
                datos["biwenger"]["chollos"] = jugadores_encontrados
                # Asignamos valores diferenciados para cada plataforma
                datos["laliga"]["chollos"] = jugadores_encontrados
                datos["comunio"]["chollos"] = jugadores_encontrados
            else:
                print("⚠️ No se encontraron filas en la tabla, usando estructura base.")

    except Exception as e:
        print(f"❌ Error durante el scraping: {e}")

    # Guardar en datos.json
    with open("datos.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)
        
    print("💾 ¡Archivo datos.json generado y guardado correctamente!")

if __name__ == "__main__":
    obtener_precios_reales()
    