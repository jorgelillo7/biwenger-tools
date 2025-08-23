from unidecode import unidecode

# Este mapa es específico para la lógica de este analizador.
# biwenger -> Analítica Fantasy
# quitar acentos, pasar a minúsculas
PLAYER_NAME_MAPPINGS = {
 # Nombres completamente diferentes
    'odysseas': 'vlachodimos',
    'alhassane': 'rahim',

    # Inversiones o adiciones
    'sancet': 'oihan sancet',
    'javi hernandez': 'javier hernandez',

    # Apodos o variaciones que no son simples acrónimos
    'javier rueda': 'javi rueda',
    'brugue': 'brugui',

    # Casos ambiguos que es mejor forzar
    'ricardo rodriguez': 'r. rodriguez', # Podría confundirse con otro Rodríguez
    'matias moreno': 'm. moreno'
}

def normalize_name(name):
    """Función centralizada para limpiar y normalizar nombres."""
    return unidecode(name.lower().strip())

def find_player_match(biwenger_name, analitica_map):
    """
    Versión mejorada que automatiza patrones comunes de nombres y usa
    un mapa de mapeo reducido solo para las excepciones.
    """
    norm_b_name = normalize_name(biwenger_name)

    # Estrategia 1: Búsqueda por nombre original normalizado (la más fiable)
    if norm_b_name in analitica_map:
        return analitica_map[norm_b_name]

    # Estrategia 2: Mapeo de excepciones (casos especiales definidos a mano)
    if norm_b_name in PLAYER_NAME_MAPPINGS:
        mapped_name = PLAYER_NAME_MAPPINGS[norm_b_name]
        if mapped_name in analitica_map:
            return analitica_map[mapped_name]

    # Estrategia 3: Transformaciones automáticas para nombres compuestos
    name_parts = norm_b_name.split()
    if len(name_parts) > 1:
        # Intenta coincidir solo con el apellido (ej: 'pacha espino' -> 'espino')
        last_name = name_parts[-1]
        if last_name in analitica_map:
            return analitica_map[last_name]

        # Intenta coincidir solo con el nombre (ej: 'giuliano simeone' -> 'giuliano')
        first_name = name_parts[0]
        if first_name in analitica_map:
            return analitica_map[first_name]

        # Intenta coincidir con inicial. apellido (ej: 'carlos vicente' -> 'c. vicente')
        initial_last_name = f"{name_parts[0][0]}. {name_parts[-1]}"
        if initial_last_name in analitica_map:
            return analitica_map[initial_last_name]

    # Estrategia 4: Búsqueda por subconjunto (último recurso)
    b_name_parts_set = set(name_parts)
    for a_name, data in analitica_map.items():
        if b_name_parts_set.issubset(set(a_name.split())):
            return data

    # Si nada funciona, se devuelve el valor por defecto
    return {'coeficiente': 'N/A', 'puntuacion_esperada': 'N/A'}

def map_position(pos_id):
    """Mapea el ID de posición de Biwenger a un string legible."""
    return {1: "Portero", 2: "Defensa", 3: "Centrocampista", 4: "Delantero"}.get(pos_id, "N/A")
