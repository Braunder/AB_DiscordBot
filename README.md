# Description
This project is a Discord bot written in Python using the Disnake library. The bot manages a game server, allowing administrators to start, stop, and restart the server, as well as manage players through Discord commands. The bot also supports automatic welcome messages for new members and scheduling server start and stop times.


# Installation
1. Ensure you have Python 3.8 or higher installed.
2. Install the required dependencies:
```bash
pip install disnake python-socketio apscheduler
```
Edit a settings.py file in the root directory of the project and add the following variables:

```python
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
```
# Project Structure

```
/project-directory
│
├── bot.py          # Main bot file
├── settings.py     # Settings file (channel IDs, server path, etc.)
└── cogs/           # Folder for cogs (modules)
    ├── discord_commands.py  # Class with commands and event handlers for welcome messages
    └── server_commands.py    # Class with commands for server management
```
# Commands
## Welcome Commands (Cog: Discord_commands)
* on_member_join: Automatically sends a welcome message to the specified channel when a new member joins the server. The message includes a random image from a specified folder.
## Server Management (Cog: Server_commands)
* `/start_server`: Starts the server. Available only to administrators.
* `/stop_server`: Stops the server. Available only to administrators.
* `/restart_server`: Restarts the server. Available only to administrators.
* `/abort_action`: Cancels a scheduled action (starting or stopping the server). Available only to administrators.
## Player Management
* `/whitelist`: Adds a player to the whitelist. Available only to administrators.
* `/whitelist_remove`: Removes a player from the whitelist. Available only to administrators.
* `/ban`: Bans a player from the server. Available only to administrators.
* `/unban`: Unbans a player from the server. Available only to administrators.
* `/banid`: Bans a player by ID. Available only to administrators.
* `/unbanid`: Unbans a player by ID. Available only to administrators.
* `/players`: Displays the list of players on the server. Available only to administrators.
# How It Works
* The bot uses RCON to manage the game server, allowing commands such as starting, stopping, and managing players.
* The bot automatically sends welcome messages to new members, including random images.
* The bot supports scheduling server start and stop times using the APScheduler library.
* All actions are logged, and errors are handled through logging.

# Running the Bot

```bash
python bot.py
```
### License
This project is licensed under the MIT License. Please refer to the LICENSE file for more information.

### Contributions
If you would like to contribute to the project, please create a repository fork and submit a pull-request with your changes.