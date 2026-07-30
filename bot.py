import json
from seleniumbase import SB

def robar_datos_desde_dentro():
    print("🤖 Iniciando asalto sigiloso a Relevo con SeleniumBase UC...")
    
    # Arrancamos el navegador en modo indetectable y oculto
    with SB(uc=True, headless=True) as sb:
        try:
            print("🌐 Entrando por la puerta principal (Portada de Relevo)...")
            # Visitamos la web normal para que Cloudflare nos ponga el sello de "Humano"
            sb.uc_open_with_reconnect("https://laligafantasy.relevo.com/", reconnect_time=6)
            
            # Le damos 8 segundos de margen al CAPTCHA invisible para que se resuelva solo
            sb.sleep(8) 
            
            print("📡 Extrayendo la base de datos masiva de la API interna...")
            # Usamos JavaScript para pedir los datos a la API desde dentro de la web aprobada
            datos = sb.execute_async_script("""
                const callback = arguments[arguments.length - 1];
                fetch('https://laligafantasy.relevo.com/api/v1/master-data')
                    .then(response => response.json())
                    .then(data => callback(data))
                    .catch(error => callback(null));
            """)
            
            if datos and "players" in datos:
                lista_raw = datos["players"]
                equipos_map = {t["id"]: t["name"] for t in datos.get("teams", [])}
                pos_map = {1: "POR", 2: "DEF", 3: "MED", 4: "DEL"}
                
                jugadores_procesados = []
                for p in lista_raw:
                    nombre = p.get("nickname") or p.get("name") or "Jugador"
                    eq = equipos_map.get(p.get("teamId"), "LaLiga")
                    pos = pos_map.get(p.get("positionId", 3), "MED")
                    precio = p.get("marketValue", 0)
                    sub = p.get("marketValueIncrement", 0)
                    pts = str(p.get("pointsAverage", 0.0))

                    # Formateamos el precio para que se vea bien en tu web
                    str_precio = f"{precio:,} €".replace(',', '.')
                    str_subida = f"+ {sub:,} €".replace(',', '.') if sub >= 0 else f"- {abs(sub):,} €".replace(',', '.')

                    jugadores_procesados.append({
                        "nombre": nombre, "equipo": eq, "pos": pos,
                        "precio": str_precio,
                        "subida": str_subida,
                        "pts": pts
                    })
                    
                # Ordenar por valor de mercado descendente
                jugadores_procesados.sort(key=lambda x: int(x["precio"].replace(" €", "").replace(".", "")) if isinstance(x.get("precio"), str) and "€" in x["precio"] else 0, reverse=True)
                
                # Guardar en tu JSON
                base_datos = {"laliga": {"chollos": jugadores_procesados}}
                with open("datos.json", "w", encoding="utf-8") as f:
                    json.dump(base_datos, f, ensure_ascii=False, indent=4)
                print(f"✅ ¡ÉXITO DEFINITIVO! {len(jugadores_procesados)} jugadores extraídos limpiamente.")
            else:
                print("❌ No se pudieron extraer los datos. Posible bloqueo residual.")

        except Exception as e:
            print(f"❌ Error en la ejecución: {e}")

if __name__ == "__main__":
    robar_datos_desde_dentro()