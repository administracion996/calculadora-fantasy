import json

def actualizar_datos():
    # Estructura de datos para los tres juegos principales
    datos_actualizados = {
        "biwenger": {
            "chollos": [
                { "nombre": "Lamine Yamal", "equipo": "FC Barcelona", "pos": "DEL", "subida": "+ 350.000 €", "precio": "18.700.000 €", "pts": "8.3" },
                { "nombre": "Brahim Díaz", "equipo": "Real Madrid", "pos": "MED", "subida": "+ 220.000 €", "precio": "5.300.000 €", "pts": "6.2" },
                { "nombre": "Kirian Rodríguez", "equipo": "Las Palmas", "pos": "MED", "subida": "+ 150.000 €", "precio": "7.950.000 €", "pts": "6.5" }
            ],
            "bajas": [
                { "nombre": "Gavi", "equipo": "FC Barcelona", "estado": "🔴 Baja Confirmada", "motivo": "Rotura de ligamento" },
                { "nombre": "Jude Bellingham", "equipo": "Real Madrid", "estado": "🟡 Duda", "motivo": "Molestias en el hombro" }
            ]
        },
        "laliga": {
            "chollos": [
                { "nombre": "Kylian Mbappé", "equipo": "Real Madrid", "pos": "DEL", "subida": "+ 600.000 €", "precio": "62.600.000 €", "pts": "9.2" },
                { "nombre": "Nico Williams", "equipo": "Athletic Club", "pos": "DEL", "subida": "+ 310.000 €", "precio": "35.800.000 €", "pts": "7.5" },
                { "nombre": "Sancet", "equipo": "Athletic Club", "pos": "MED", "subida": "+ 190.000 €", "precio": "19.390.000 €", "pts": "5.9" }
            ],
            "bajas": [
                { "nombre": "Vinícius Jr.", "equipo": "Real Madrid", "estado": "🔴 Sancionado", "motivo": "Acumulación de tarjetas" },
                { "nombre": "Isco Alarcón", "equipo": "Real Betis", "estado": "🟡 Duda", "motivo": "Sobrecarga muscular" }
            ]
        },
        "comunio": {
            "chollos": [
                { "nombre": "Antoine Griezmann", "equipo": "Atlético de Madrid", "pos": "DEL", "subida": "+ 160.000 €", "precio": "12.460.000 €", "pts": "7.1" },
                { "nombre": "Take Kubo", "equipo": "Real Sociedad", "pos": "DEL", "subida": "+ 120.000 €", "precio": "9.020.000 €", "pts": "6.0" },
                { "nombre": "Aleix García", "equipo": "Girona FC", "pos": "MED", "subida": "+ 95.000 €", "precio": "9.595.000 €", "pts": "6.8" }
            ],
            "bajas": [
                { "nombre": "Mikel Oyarzabal", "equipo": "Real Sociedad", "estado": "🟡 Duda", "motivo": "Evaluación médica" }
            ]
        }
    }

    # Guarda la información en datos.json
    with open('datos.json', 'w', encoding='utf-8') as f:
        json.dump(datos_actualizados, f, ensure_ascii=False, indent=4)
        print("✅ Archivo datos.json generado y actualizado con éxito.")

if __name__ == '__main__':
    actualizar_datos()
