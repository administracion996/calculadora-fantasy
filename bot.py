import json

def generar_mercado_completo():
    print("🤖 Generando base de datos completa de los 20 equipos de LaLiga...")

    # Lista con los 20 clubes oficiales
    equipos = [
        "Athletic Club", "Atlético de Madrid", "CA Osasuna", "CD Leganés", "Celta de Vigo",
        "Deportivo Alavés", "FC Barcelona", "Getafe CF", "Girona FC", "Rayo Vallecano",
        "RCD Espanyol", "RCD Mallorca", "Real Betis", "Real Madrid", "Real Sociedad",
        "Real Valladolid", "Sevilla FC", "UD Las Palmas", "Valencia CF", "Villarreal CF"
    ]

    # Plantilla de jugadores destacados repartidos por equipos y plataformas
    jugadores_base = [
        # FC Barcelona
        {"nombre": "Lamine Yamal", "equipo": "FC Barcelona", "pos": "DEL", "pts": "8.8", "bio_price": "22.100.000 €", "bio_sub": "+ 450.000 €", "liga_price": "125.000.000 €", "liga_sub": "+ 950.000 €", "com_price": "18.200.000 €", "com_sub": "+ 300.000 €"},
        {"nombre": "Raphinha", "equipo": "FC Barcelona", "pos": "DEL", "pts": "9.1", "bio_price": "19.800.000 €", "bio_sub": "+ 520.000 €", "liga_price": "110.000.000 €", "liga_sub": "+ 800.000 €", "com_price": "16.500.000 €", "com_sub": "+ 410.000 €"},
        {"nombre": "Pedri", "equipo": "FC Barcelona", "pos": "MED", "pts": "7.9", "bio_price": "15.400.000 €", "bio_sub": "+ 210.000 €", "liga_price": "88.000.000 €", "liga_sub": "+ 450.000 €", "com_price": "13.100.000 €", "com_sub": "+ 180.000 €"},
        {"nombre": "Robert Lewandowski", "equipo": "FC Barcelona", "pos": "DEL", "pts": "8.4", "bio_price": "18.200.000 €", "bio_sub": "- 150.000 €", "liga_price": "95.000.000 €", "liga_sub": "- 300.000 €", "com_price": "15.000.000 €", "com_sub": "- 90.000 €"},
        
        # Real Madrid
        {"nombre": "Kylian Mbappé", "equipo": "Real Madrid", "pos": "DEL", "pts": "9.4", "bio_price": "24.500.000 €", "bio_sub": "+ 680.000 €", "liga_price": "182.000.000 €", "liga_sub": "+ 1.200.000 €", "com_price": "21.000.000 €", "com_sub": "+ 500.000 €"},
        {"nombre": "Jude Bellingham", "equipo": "Real Madrid", "pos": "MED", "pts": "8.5", "bio_price": "19.100.000 €", "bio_sub": "+ 190.000 €", "liga_price": "115.000.000 €", "liga_sub": "+ 350.000 €", "com_price": "16.200.000 €", "com_sub": "+ 120.000 €"},
        {"nombre": "Vinícius Jr.", "equipo": "Real Madrid", "pos": "DEL", "pts": "8.9", "bio_price": "21.000.000 €", "bio_sub": "- 220.000 €", "liga_price": "140.000.000 €", "liga_sub": "- 500.000 €", "com_price": "17.800.000 €", "com_sub": "- 200.000 €"},
        {"nombre": "Federico Valverde", "equipo": "Real Madrid", "pos": "MED", "pts": "7.8", "bio_price": "14.800.000 €", "bio_sub": "+ 140.000 €", "liga_price": "82.000.000 €", "liga_sub": "+ 200.000 €", "com_price": "12.400.000 €", "com_sub": "+ 80.000 €"},

        # Athletic Club
        {"nombre": "Nico Williams", "equipo": "Athletic Club", "pos": "DEL", "pts": "7.8", "bio_price": "12.500.000 €", "bio_sub": "+ 310.000 €", "liga_price": "78.500.000 €", "liga_sub": "+ 410.000 €", "com_price": "10.200.000 €", "com_sub": "+ 220.000 €"},
        {"nombre": "Iñaki Williams", "equipo": "Athletic Club", "pos": "DEL", "pts": "7.4", "bio_price": "10.800.000 €", "bio_sub": "+ 180.000 €", "liga_price": "62.000.000 €", "liga_sub": "+ 250.000 €", "com_price": "9.100.000 €", "com_sub": "+ 110.000 €"},
        {"nombre": "Oihan Sancet", "equipo": "Athletic Club", "pos": "MED", "pts": "7.1", "bio_price": "8.400.000 €", "bio_sub": "+ 90.000 €", "liga_price": "45.000.000 €", "liga_sub": "+ 120.000 €", "com_price": "7.200.000 €", "com_sub": "+ 60.000 €"},

        # Atlético de Madrid
        {"nombre": "Antoine Griezmann", "equipo": "Atlético de Madrid", "pos": "DEL", "pts": "7.6", "bio_price": "13.800.000 €", "bio_sub": "+ 210.000 €", "liga_price": "71.000.000 €", "liga_sub": "+ 300.000 €", "com_price": "11.500.000 €", "com_sub": "+ 140.000 €"},
        {"nombre": "Julián Alvarez", "equipo": "Atlético de Madrid", "pos": "DEL", "pts": "7.5", "bio_price": "15.200.000 €", "bio_sub": "+ 290.000 €", "liga_price": "85.000.000 €", "liga_sub": "+ 400.000 €", "com_price": "12.800.000 €", "com_sub": "+ 190.000 €"},

        # Villarreal CF
        {"nombre": "Ayoze Pérez", "equipo": "Villarreal CF", "pos": "DEL", "pts": "7.9", "bio_price": "11.200.000 €", "bio_sub": "+ 340.000 €", "liga_price": "58.000.000 €", "liga_sub": "+ 420.000 €", "com_price": "9.400.000 €", "com_sub": "+ 250.000 €"},
        {"nombre": "Alex Baena", "equipo": "Villarreal CF", "pos": "MED", "pts": "8.1", "bio_price": "12.900.000 €", "bio_sub": "+ 260.000 €", "liga_price": "69.000.000 €", "liga_sub": "+ 380.000 €", "com_price": "10.800.000 €", "com_sub": "+ 170.000 €"},

        # Celta de Vigo
        {"nombre": "Iago Aspas", "equipo": "Celta de Vigo", "pos": "DEL", "pts": "7.7", "bio_price": "9.800.000 €", "bio_sub": "+ 120.000 €", "liga_price": "51.000.000 €", "liga_sub": "+ 180.000 €", "com_price": "8.300.000 €", "com_sub": "+ 90.000 €"},
        {"nombre": "Oscar Mingueza", "equipo": "Celta de Vigo", "pos": "DEF", "pts": "7.2", "bio_price": "6.500.000 €", "bio_sub": "+ 150.000 €", "liga_price": "34.000.000 €", "liga_sub": "+ 220.000 €", "com_price": "5.400.000 €", "com_sub": "+ 110.000 €"},

        # Real Betis
        {"nombre": "Giovani Lo Celso", "equipo": "Real Betis", "pos": "MED", "pts": "8.0", "bio_price": "11.500.000 €", "bio_sub": "+ 310.000 €", "liga_price": "61.000.000 €", "liga_sub": "+ 390.000 €", "com_price": "9.900.000 €", "com_sub": "+ 210.000 €"},
        {"nombre": "Isco Alarcón", "equipo": "Real Betis", "pos": "MED", "pts": "8.2", "bio_price": "10.200.000 €", "bio_sub": "+ 190.000 €", "liga_price": "54.000.000 €", "liga_sub": "+ 240.000 €", "com_price": "8.700.000 €", "com_sub": "+ 130.000 €"},

        # Real Sociedad
        {"nombre": "Mikel Oyarzabal", "equipo": "Real Sociedad", "pos": "DEL", "pts": "6.9", "bio_price": "8.900.000 €", "bio_sub": "- 80.000 €", "liga_price": "43.000.000 €", "liga_sub": "- 120.000 €", "com_price": "7.500.000 €", "com_sub": "- 60.000 €"},
        {"nombre": "Takefusa Kubo", "equipo": "Real Sociedad", "pos": "DEL", "pts": "7.3", "bio_price": "9.400.000 €", "bio_sub": "+ 110.000 €", "liga_price": "49.000.000 €", "liga_sub": "+ 160.000 €", "com_price": "8.100.000 €", "com_sub": "+ 70.000 €"},

        # Girona FC
        {"nombre": "Bryan Gil", "equipo": "Girona FC", "pos": "DEL", "pts": "7.0", "bio_price": "5.800.000 €", "bio_sub": "+ 140.000 €", "liga_price": "29.000.000 €", "liga_sub": "+ 180.000 €", "com_price": "4.900.000 €", "com_sub": "+ 90.000 €"},

        # Sevilla FC
        {"nombre": "Dodi Lukebakio", "equipo": "Sevilla FC", "pos": "DEL", "pts": "7.3", "bio_price": "7.200.000 €", "bio_sub": "+ 230.000 €", "liga_price": "38.000.000 €", "liga_sub": "+ 290.000 €", "com_price": "6.100.000 €", "com_sub": "+ 160.000 €"},

        # CA Osasuna
        {"nombre": "Ante Budimir", "equipo": "CA Osasuna", "pos": "DEL", "pts": "7.5", "bio_price": "8.100.000 €", "bio_sub": "+ 170.000 €", "liga_price": "41.000.000 €", "liga_sub": "+ 220.000 €", "com_price": "6.800.000 €", "com_sub": "+ 110.000 €"},

        # Rayo Vallecano
        {"nombre": "Jorge de Frutos", "equipo": "Rayo Vallecano", "pos": "MED", "pts": "6.8", "bio_price": "4.200.000 €", "bio_sub": "+ 120.000 €", "liga_price": "21.000.000 €", "liga_sub": "+ 150.000 €", "com_price": "3.500.000 €", "com_sub": "+ 80.000 €"},

        # RCD Mallorca
        {"nombre": "Vedat Muriqi", "equipo": "RCD Mallorca", "pos": "DEL", "pts": "7.1", "bio_price": "6.900.000 €", "bio_sub": "+ 90.000 €", "liga_price": "35.000.000 €", "liga_sub": "+ 110.000 €", "com_price": "5.800.000 €", "com_sub": "+ 50.000 €"},

        # Valencia CF
        {"nombre": "Hugo Duro", "equipo": "Valencia CF", "pos": "DEL", "pts": "6.7", "bio_price": "5.400.000 €", "bio_sub": "+ 80.000 €", "liga_price": "27.000.000 €", "liga_sub": "+ 100.000 €", "com_price": "4.300.000 €", "com_sub": "+ 40.000 €"},

        # Deportivo Alavés
        {"nombre": "Kike García", "equipo": "Deportivo Alavés", "pos": "DEL", "pts": "6.5", "bio_price": "3.100.000 €", "bio_sub": "+ 60.000 €", "liga_price": "14.000.000 €", "liga_sub": "+ 80.000 €", "com_price": "2.400.000 €", "com_sub": "+ 30.000 €"},

        # CD Leganés
        {"nombre": "Juan Cruz", "equipo": "CD Leganés", "pos": "DEL", "pts": "6.9", "bio_price": "3.800.000 €", "bio_sub": "+ 110.000 €", "liga_price": "18.000.000 €", "liga_sub": "+ 130.000 €", "com_price": "3.100.000 €", "com_sub": "+ 70.000 €"},

        # RCD Espanyol
        {"nombre": "Javi Puado", "equipo": "RCD Espanyol", "pos": "DEL", "pts": "6.8", "bio_price": "4.500.000 €", "bio_sub": "+ 90.000 €", "liga_price": "22.000.000 €", "liga_sub": "+ 120.000 €", "com_price": "3.700.000 €", "com_sub": "+ 50.000 €"},

        # Real Valladolid
        {"nombre": "Raúl Moro", "equipo": "Real Valladolid", "pos": "DEL", "pts": "6.7", "bio_price": "3.400.000 €", "bio_sub": "+ 80.000 €", "liga_price": "16.000.000 €", "liga_sub": "+ 90.000 €", "com_price": "2.800.000 €", "com_sub": "+ 40.000 €"},

        # UD Las Palmas
        {"nombre": "Alberto Moleiro", "equipo": "UD Las Palmas", "pos": "MED", "pts": "7.2", "bio_price": "5.900.000 €", "bio_sub": "+ 130.000 €", "liga_price": "28.000.000 €", "liga_sub": "+ 160.000 €", "com_price": "4.800.000 €", "com_sub": "+ 80.000 €"},

        # Getafe CF
        {"nombre": "Mauro Arambarri", "equipo": "Getafe CF", "pos": "MED", "pts": "6.9", "bio_price": "4.100.000 €", "bio_sub": "+ 100.000 €", "liga_price": "20.000.000 €", "liga_sub": "+ 120.000 €", "com_price": "3.300.000 €", "com_sub": "+ 60.000 €"}
    ]

    # Construir objeto JSON por plataformas
    datos = {
        "biwenger": {"chollos": []},
        "laliga": {"chollos": []},
        "comunio": {"chollos": []}
    }

    for j in jugadores_base:
        datos["biwenger"]["chollos"].append({
            "nombre": j["nombre"], "equipo": j["equipo"], "pos": j["pos"], "pts": j["pts"],
            "precio": j["bio_price"], "subida": j["bio_sub"]
        })
        datos["laliga"]["chollos"].append({
            "nombre": j["nombre"], "equipo": j["equipo"], "pos": j["pos"], "pts": j["pts"],
            "precio": j["liga_price"], "subida": j["liga_sub"]
        })
        datos["comunio"]["chollos"].append({
            "nombre": j["nombre"], "equipo": j["equipo"], "pos": j["pos"], "pts": j["pts"],
            "precio": j["com_price"], "subida": j["com_sub"]
        })

    with open("datos.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

    print("✅ Base de datos guardada con éxito en datos.json!")

if __name__ == "__main__":
    generar_mercado_completo()
    