import csv
import os
import time
import traceback
from datetime import datetime

from teams_analyzer import config
from teams_analyzer.logic.scrapers import (
    fetch_jp_player_tips,
    fetch_analitica_fantasy_coeffs,
)
from teams_analyzer.logic.player_matching import (
    find_player_match,
    normalize_name,
    map_position,
)
from core.biwenger_client import BiwengerClient
from core.telegram_notifier import send_telegram_notification


def main():
    """Orquesta el proceso de análisis de equipos y mercado."""
    start_time = time.time()
    print(f"🚀 Script iniciado a las {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # 1. Conexión a Biwenger
        biwenger = BiwengerClient(
            config.BIWENGER_EMAIL,
            config.BIWENGER_PASSWORD,
            config.LOGIN_URL,
            config.ACCOUNT_URL,
            config.LEAGUE_ID,
        )

        # 2. Obtención de datos de fuentes externas
        players_map_biwenger = biwenger.get_all_players_data_map(
            config.ALL_PLAYERS_DATA_URL
        )
        jp_tips_map = fetch_jp_player_tips()
        analitica_coeffs_map = fetch_analitica_fantasy_coeffs()

        if not analitica_coeffs_map:
            print(
                "\n❌ No se pudieron obtener los datos de Analítica Fantasy. Abortando."
            )
            return

        # 3. Obtención de datos de la liga desde Biwenger
        managers_map = biwenger.get_league_users(config.LEAGUE_DATA_URL)
        market_players = biwenger.get_market_players(config.MARKET_URL)

        # 4. Procesamiento y análisis de los datos
        all_players_export_list = []
        print("\n--- Analizando datos de la liga ---\n")

        # Analizar plantillas de mánagers
        for manager_id, manager_name in managers_map.items():
            squad_data = biwenger.get_manager_squad(config.USER_SQUAD_URL, manager_id)
            print(f"🔎 Analizando a: {manager_name} ({len(squad_data)} jugadores)")
            time.sleep(0.5)
            for player_data in squad_data:
                player_info = players_map_biwenger.get(player_data.get("id"))
                if not player_info:
                    continue

                player_name = player_info.get("name", "N/A")
                matched_data = find_player_match(player_name, analitica_coeffs_map)

                all_players_export_list.append(
                    {
                        "Mánager": manager_name,
                        "Jugador": player_name,
                        "Posición": map_position(player_info.get("position")),
                        "Valor Actual": player_info.get("price", 0),
                        "Cláusula": player_data.get("owner", {}).get("clause", 0),
                        "Nota IA": jp_tips_map.get(
                            normalize_name(player_name), "Sin datos"
                        ),
                        "Coeficiente AF": matched_data["coeficiente"],
                        "Puntuación Esperada AF": matched_data["puntuacion_esperada"],
                    }
                )

        # Analizar jugadores libres en el mercado
        free_agents = [sale for sale in market_players if sale.get("user") is None]
        market_team_name = f"Mercado_{datetime.now().strftime('%d%m%Y')}"
        print(
            f"\n🔎 Analizando a: {market_team_name} ({len(free_agents)} jugadores libres)"
        )
        for sale in free_agents:
            player_info = players_map_biwenger.get(sale.get("player", {}).get("id"))
            if not player_info:
                continue

            player_name = player_info.get("name", "N/A")
            matched_data = find_player_match(player_name, analitica_coeffs_map)

            all_players_export_list.append(
                {
                    "Mánager": market_team_name,
                    "Jugador": player_name,
                    "Posición": map_position(player_info.get("position")),
                    "Valor Actual": player_info.get("price", 0),
                    "Cláusula": sale.get("price", 0),
                    "Nota IA": jp_tips_map.get(
                        normalize_name(player_name), "Sin datos"
                    ),
                    "Coeficiente AF": matched_data["coeficiente"],
                    "Puntuación Esperada AF": matched_data["puntuacion_esperada"],
                }
            )

        # 5. Exportación y notificación
        if all_players_export_list:
            order = {
                "muyRecomendable": 0,
                "recomendable": 1,
                "apuesta": 2,
                "fondoDeArmario": 3,
                "parche": 4,
                "noRecomendable": 5,
            }
            all_players_export_list.sort(
                key=lambda x: (
                    x["Mánager"].startswith("Mercado_"),
                    x["Mánager"],
                    order.get(x["Nota IA"], 99),
                )
            )

            # --- CORRECCIÓN: Construir la ruta de salida dinámicamente ---
            # Esto asegura que el CSV se guarde dentro de la carpeta 'teams_analyzer'
            base_dir = os.path.dirname(os.path.abspath(__file__))
            output_filepath = os.path.join(base_dir, config.FINAL_REPORT_NAME)

            fieldnames = [
                "Mánager",
                "Jugador",
                "Posición",
                "Valor Actual",
                "Cláusula",
                "Nota IA",
                "Coeficiente AF",
                "Puntuación Esperada AF",
            ]
            with open(output_filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_players_export_list)
            print(
                f"\n✅ ¡Exportación de {len(all_players_export_list)} jugadores completada en '{config.FINAL_REPORT_NAME}'!"
            )

            if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID:
                caption = f"📊 ¡Análisis de equipos completado! ({len(all_players_export_list)} jugadores)"
                send_telegram_notification(
                    config.TELEGRAM_API_URL,
                    config.TELEGRAM_BOT_TOKEN,
                    config.TELEGRAM_CHAT_ID,
                    caption,
                    output_filepath,
                )
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")
        traceback.print_exc()
    finally:
        duration = time.time() - start_time
        print(f"\n🏁 Script finalizado en {duration:.2f} segundos.")


if __name__ == "__main__":
    main()
