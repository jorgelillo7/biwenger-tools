# teams_analyzer/logic/player_matching.py
from unidecode import unidecode

# Este mapa es específico para la lógica de este analizador.
PLAYER_NAME_MAPPINGS = {
    'odysseas': 'vlachodimos', 'sancet': 'oihan sancet', 'carlos vicente': 'c. vicente',
    'javier rueda': 'javi rueda', 'javi': 'javier', 'brugue': 'brugui',
    'nacho': 'ignacio', 'alhassane': 'rahim',
}

def normalize_name(name):
    """Función centralizada para limpiar y normalizar nombres."""
    return unidecode(name.lower().strip())

def find_player_match(biwenger_name, analitica_map):
    """
    Busca la correspondencia de un jugador de Biwenger en el mapa de datos
    de Analítica Fantasy usando varias estrategias.
    """
    norm_b_name = normalize_name(biwenger_name)

    # Estrategia 1: Mapeo directo
    if norm_b_name in PLAYER_NAME_MAPPINGS:
        mapped_name = PLAYER_NAME_MAPPINGS[norm_b_name]
        if mapped_name in analitica_map:
            return analitica_map[mapped_name]

    # Estrategia 2: Reemplazo de partes del nombre
    modified_name = norm_b_name
    for biwenger_part, fa_part in PLAYER_NAME_MAPPINGS.items():
        if biwenger_part in modified_name:
            modified_name = modified_name.replace(biwenger_part, fa_part)
    if modified_name in analitica_map:
        return analitica_map[modified_name]

    # Estrategia 3: Búsqueda por nombre original normalizado
    if norm_b_name in analitica_map:
        return analitica_map[norm_b_name]

    # Estrategia 4: Búsqueda por subconjunto de palabras
    b_name_parts = set(norm_b_name.split())
    for a_name, data in analitica_map.items():
        if b_name_parts.issubset(set(a_name.split())):
            return data

    return {'coeficiente': 'N/A', 'puntuacion_esperada': 'N/A'}

def map_position(pos_id):
    """Mapea el ID de posición de Biwenger a un string legible."""
    return {1: "Portero", 2: "Defensa", 3: "Centrocampista", 4: "Delantero"}.get(pos_id, "N/A")
