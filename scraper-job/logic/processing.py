import unidecode
from datetime import datetime

def categorize_title(title):
    """Clasifica un mensaje según su título."""
    if not title:
        return "comunicado"
    # Normalizamos a mayúsculas y sin acentos para hacer la comparación más robusta
    normalized_title = unidecode.unidecode(title.strip().upper())

    if normalized_title.startswith("CRONICA -") or normalized_title.startswith("CRONICAS"):
        return "cronica"
    if normalized_title.startswith("DATO -") or normalized_title.startswith("DATOS -"):
        return "dato"
    if normalized_title.startswith("CESION -"):
        return "cesion"
    return "comunicado"

def process_participation(all_messages, user_map):
    """Calcula y formatea los datos de participación de los usuarios."""
    # Inicializa un diccionario para cada usuario con todas las categorías
    participation = {name: {"comunicado": [], "dato": [], "cesion": [], "cronica": []} for name in user_map.values()}

    for msg in all_messages:
        author = msg.get('autor')
        category = msg.get('categoria')
        msg_id = msg.get('id_hash')

        # Si el autor existe en nuestro mapa y el mensaje tiene categoría y ID...
        if author in participation and category and msg_id:
            # Añadimos el ID a la lista de su categoría, evitando duplicados
            if msg_id not in participation[author][category]:
                participation[author][category].append(msg_id)

    # Formateamos la salida para el CSV
    output_data = []
    for author, categories in participation.items():
        output_data.append({
            'autor': author,
            'comunicados': ";".join(categories['comunicado']),
            'datos': ";".join(categories['dato']),
            'cesiones': ";".join(categories['cesion']),
            'cronicas': ";".join(categories['cronica'])
        })
    return output_data

def sort_messages(messages):
    """Ordena una lista de mensajes por fecha, de más reciente a más antiguo."""
    def get_date(msg):
        # Función auxiliar para convertir el string de fecha en un objeto datetime
        # Maneja posibles errores si la fecha está mal formateada o no existe
        try:
            return datetime.strptime(msg['fecha'], '%d-%m-%Y %H:%M:%S')
        except (ValueError, TypeError):
            # Si hay un error, lo tratamos como la fecha más antigua posible para que quede al final
            return datetime.min

    messages.sort(key=get_date, reverse=True)
    return messages
