import pandas as pd

# Cargar datos de rutas turísticas
df_rutas = pd.read_csv('baseDatos/rutas_turisticas.csv')

# Función principal del recomendador
def recomendar_ruta(tipo_ruta_input, popularidad_input, dificultad_input, duracion_min, duracion_max):
    rutas_filtradas = df_rutas[df_rutas['tipo_ruta'].str.lower() == tipo_ruta_input.lower()]

    if rutas_filtradas.empty:
        return "No hay rutas disponibles para ese tipo de ruta."

    recomendaciones = []

    for _, ruta in rutas_filtradas.iterrows():
        puntuacion = 0

        if popularidad_input == 'popular' and ruta['popularidad'] >= 4.0:
            puntuacion += 3
        elif popularidad_input == 'poco popular' and ruta['popularidad'] < 4.0:
            puntuacion += 3

        distancia = ruta['longitud_km']
        if dificultad_input == 'facil' and distancia < 4.0:
            puntuacion += 2
        elif dificultad_input == 'estandar' and 4.0 <= distancia <= 6.5:
            puntuacion += 2
        elif dificultad_input == 'extremo' and distancia > 6.5:
            puntuacion += 2

        duracion = ruta['duracion_hr']
        if duracion_min <= duracion <= duracion_max:
            puntuacion += 1

        recomendaciones.append((ruta, puntuacion))

    recomendaciones.sort(key=lambda x: x[1], reverse=True)

    mejor_ruta = recomendaciones[0][0]
    puntuacion_maxima = recomendaciones[0][1]

    return {
        'Nombre': mejor_ruta['ruta_nombre'],
        'Tipo_ruta': mejor_ruta['tipo_ruta'],
        'Valoracion': mejor_ruta['popularidad'],
        'Distancia_km': mejor_ruta['longitud_km'],
        'Duracion_horas': mejor_ruta['duracion_hr'],
        'Puntuacion': puntuacion_maxima
    }

# ------------------------------
# Recoger inputs del usuario
print("Bienvenido al recomendador de rutas.")
tipo_ruta_input = input("Tipo de ruta (Cultural, Aventura, Ecologica, Historica, Gastronomica): ").strip()
popularidad_input = input("¿Prefieres una ruta popular o poco popular?: ").strip().lower()
dificultad_input = input("Nivel de dificultad (facil, estandar, extremo): ").strip().lower()
duracion_min = float(input("Duración mínima en horas (ej: 2.0): ").strip())
duracion_max = float(input("Duración máxima en horas (ej: 5.0): ").strip())

# Llamar a la función
resultado = recomendar_ruta(tipo_ruta_input, popularidad_input, dificultad_input, duracion_min, duracion_max)

print("\nRuta recomendada:")
print(resultado)
