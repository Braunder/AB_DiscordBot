import logging
import datetime
import os
import json

# Создаём папку для логов, если она ещё не существует
logs_directory = "logs"
if not os.path.exists(logs_directory):
    os.makedirs(logs_directory)

# Получаем текущую дату в формате 'ГГГГ-ММ-ДД'
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
log_error = f"{logs_directory}/error_{current_date}.txt"
log_server = f"{logs_directory}/server_{current_date}.txt"
log_bot = f"{logs_directory}/bot_{current_date}.txt"

def setup_logger(name, log_file, level=logging.INFO):
    """Функция для настройки логгера."""
    handler = logging.FileHandler(log_file, encoding='utf-8')    
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Создаём логгеры для разных целей
error_logger = setup_logger('error', log_error)
server_logger = setup_logger('server', log_server)
bot_logger = setup_logger('bot', log_bot)


welcome_channel = YOUR_WELCOME_CHANNEL_ID  # Replace with the ID of the welcome channel
channel_id = YOUR_CHANNEL_ID  # Replace with the ID of the notification channel
ping_role = YOUR_PING_ROLE_ID  # Replace with the ID of the role to mention
guild_id = YOUR_GUILD_ID  # Replace with the ID of your server
path = "path/to/your/server/executable"  # Specify the path to the server executable
server_ip = "YOUR_SERVER_IP"  # Specify the server's IP address
rcon_port = YOUR_RCON_PORT  # Specify the RCON port
rcon_password = "YOUR_RCON_PASSWORD"  # Specify the RCON password
admin_role = YOUR_ADMIN_ROLE_ID  # Replace with the ID of the admin role
pda_channel = YOUR_PDA_CHANNEL_ID  # Replace with the ID of the message channel
pda_channel_logs = YOUR_PDA_LOGS_CHANNEL_ID  # Replace with the ID of the logs channel



