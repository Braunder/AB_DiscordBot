from disnake.ext import commands
from rcon.source import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import settings
import disnake
import asyncio
import subprocess




class Server_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.setup_scheduler()
        """Статусы"""
        self.status_server = False
        self.scheduled_task = None
        """Настройки"""
        self.channel_id = settings.channel_id
        self.ping_role = settings.ping_role
        self.guild_id = settings.guild_id
        self.path = settings.path
        self.server_ip = settings.server_ip
        self.rcon_port = settings.rcon_port
        self.rcon_password = settings.rcon_password
        self.admin_role = settings.admin_role
        self.pda_channel = settings.pda_channel
        self.pda_channel_logs = settings.pda_channel_logs
        
        

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     for guild in self.bot.guilds:
    #         settings.bot_logger(f"{guild.name} (ID: {guild.id})")


    
    @commands.slash_command(name="start_server", description="Запуск сервера")
    async def start_server(self, inter: disnake.CommandInteraction, mode: str = commands.Param(
        default="Default",
        description="В каком режиме запустить сервер?",
        choices=[
            disnake.OptionChoice(name="Fast", value="Fast"),
            disnake.OptionChoice(name="Default", value="Default")
        ])):
        if not inter.author.guild_permissions.administrator:
            await inter.response.send_message("У вас нет прав для использования данной", ephemeral=True)
            return
        try:
            if self.status_server == True:
                await inter.response.send_message("Сервер уже запущен.", ephemeral=True)
                return
            if mode == "Fast":
                process = await asyncio.create_subprocess_exec(self.path, creationflags=subprocess.CREATE_NEW_CONSOLE)
                await inter.response.send_message("Сервер запущен", ephemeral=True)
                settings.server_logger.info(f"{self.guild.name}|{self.guild.id} - {inter.user} удачно запустил сервер")
                self.status_server = True
            else:
                self.scheduled_task = asyncio.create_task(
                    self._scheduled_start()
                )
        except Exception as e:
                # Этот блок выполнится для всех других исключений.
                settings.error_logger(f"{self.guild.name}|{self.guild.id} - Произошла непредвиденная ошибка: {e}")
                await inter.response.send_message(e, ephemeral=True)



    @commands.slash_command(name="stop_server", description="Отключение сервера")
    async def stop_server(self, inter: disnake.CommandInteraction, mode: str = commands.Param(
        default="Default",
        description="Как завершить работу Сервера?",
        choices=[
            disnake.OptionChoice(name="Fast", value="Fast"),
            disnake.OptionChoice(name="Default", value="Default")
        ])):
        settings.server_logger(f"{self.guild.name}|{self.guild.id} -  {inter.user} запустил сервер сервер: {mode}")
        try:
            if not inter.author.guild_permissions.administrator:
                await inter.response.send_message("У вас нет прав для использования данной", ephemeral=True)
                return
            # try:
            if self.status_server == False:
                await inter.response.send_message("Сервер уже выключен", ephemeral=True)
                return
            if mode == "Fast":

                settings.server_logger(f"{self.guild.name}|{self.guild.id} - {inter.user} выключил сервер: {mode}")
                with Client(self.server_ip, self.rcon_port, passwd=self.rcon_password) as client:
                    response = client.run("quit")
                    await asyncio.wait(60)
                    subprocess.run(['taskkill', '/IM', 'cmd.exe', '/F'])
                    settings.server_logger(f"{self.guild.name}|{self.guild.id} - Сервер выключился")
                    self.status_server = False

            else:
                self.scheduled_task = asyncio.create_task(
                self._scheduled_stop()
            )
        except Exception as e:
                # Этот блок выполнится для всех других исключений.
                settings.server_logger(f"{self.guild.name}|{self.guild.id} - Произошла непредвиденная ошибка: {e}")
                await inter.response.edit_message(e)


    @commands.slash_command(name="restart_server", description="Рестарт сервера")
    async def restart_server(self, inter: disnake.CommandInteraction):
        if not inter.author.guild_permissions.administrator:
            await inter.response.send_message("У вас нет прав для использования данной", ephemeral=True)
            return
        try:
            await self.notify_user("```Рестарт сервера через 5 минут```")
            with Client(self.server_ip, self.rcon_port, passwd=self.rcon_password, timeout=5) as client:
                response = client.run("Server restart in 5 minutes")
            await asyncio.sleep(300)
            with Client(self.server_ip, self.rcon_port, passwd=self.rcon_password) as client:
                response = client.run("quit")
            await self.notify_user("```Рестарт сервера```")
            settings.server_logger.info("Рестарт сервера")
            await asyncio.wait(30)
            subprocess.run(['taskkill', '/IM', 'cmd.exe', '/F'])
            process = subprocess.Popen(self.path, creationflags=subprocess.CREATE_NEW_CONSOLE)
            await asyncio.sleep(60)
            if process.wait() == 0:  
                await self.notify_user("```Сервер запущен```")
                settings.server_logger.info("Сервер удачно запущен")

            
        except Exception as e:
                # Этот блок выполнится для всех других исключений.
                settings.error_logger.error(f"Произошла непредвиденная ошибка: {e}")



    @commands.slash_command(name="abort_action", description="Отменить запланированный запуск или отключение сервера")
    async def abort_action(self, inter: disnake.CommandInteraction):
        if not inter.author.guild_permissions.administrator:
            await inter.response.send_message("У вас нет прав для использования данной команды", ephemeral=True)
            return
        try:
            if self.scheduled_task and not self.scheduled_task.done():
                self.scheduled_task.cancel()  # Отменяем задачу
                await inter.response.send_message("Запланированное действие было отменено.", ephemeral=True)
                self.scheduled_task = None  # Сбрасываем запланированную задачу
            else:
                await inter.response.send_message("Нет активных запланированных действий для отмены.")
        except Exception as e:
                # Этот блок выполнится для всех других исключений.
                settings.error_logger.error(f"Произошла непредвиденная ошибка: {e}")



    @commands.slash_command(name="whitelist", description="Добавить игрока в whiitelist")
    async def whitelist(self, inter: disnake.CommandInteraction, user: str , password: str):
        # Проверяем, есть ли у пользователя права администратора или специальная роль
        if not inter.author.guild_permissions.administrator:
            if not any(role.id in self.admin_role for role in inter.author.roles):
                await inter.response.send_message("У вас нет прав для использования данной команды.", ephemeral=True)
                return
        try:
            with Client(self.server_ip, self.rcon_port, passwd=self.rcon_password) as client:
                response = client.run(f"adduser {user} {password}",encoding="utf-8")
            await inter.response.send_message(f"```Игрок {user} добавлен в whitelist```", ephemeral=True)
            settings.admin_logger.debug(f"Админ {inter.user} добавил в whitelist игрока {user} с паролем {password}")
        except UnicodeDecodeError as e:
            settings.error_logger.error(f"Произошла непредвиденная ошибка {e}")
        except Exception as e:
                # Этот блок выполнится для всех других исключений.
                settings.error_logger.error(f"Произошла непредвиденная ошибка: {e}")



    @commands.slash_command(name="whitelist_remove", description="Удалит игрока из whiitelist")
    async def whitelist_remove(self, inter: disnake.CommandInteraction, user: str):
        # Проверяем, есть ли у пользователя права администратора или специальная роль
        if not inter.author.guild_permissions.administrator:
            if not any(role.id in self.admin_role for role in inter.author.roles):
                await inter.response.send_message("У вас нет прав для использования данной команды.", ephemeral=True)
                return
        try:
            with Client(self.server_ip, self.rcon_port, passwd=self.rcon_password) as client:
                response = client.run(f"removeuserfromwhitelist {user}",encoding="utf-8")
            await inter.response.send_message(f"```Игрок {user} удален из whitelist```", ephemeral=True)
            settings.admin_logger.debug(f"Админ {inter.user} удалил из whitelist игрока {user}")
        except UnicodeDecodeError as e:
            settings.error_logger.error(f"Произошла непредвиденная ошибка {e}")
        except Exception as e:
                # Этот блок выполнится для всех других исключений.
                settings.error_logger.error(f"Произошла непредвиденная ошибка: {e}")



    @commands.slash_command(name="ban", description="Забанить игрока на сервере")
    async def ban(self, inter: disnake.CommandInteraction, user: str):
        # Проверяем, есть ли у пользователя права администратора или специальная роль
        if not inter.author.guild_permissions.administrator:
            if not any(role.id in self.admin_role for role in inter.author.roles):
                await inter.response.send_message("У вас нет прав для использования данной команды.", ephemeral=True)
                return
        try:
            with Client(self.server_ip, self.rcon_port, passwd=self.rcon_password) as client:
                response = client.run(f"banuser {user}",encoding="utf-8")
            await inter.response.send_message(f"```Игрок {user} забанен```", ephemeral=True)
            settings.admin_logger.debug(f"Админ {inter.user} забанил игрока {user}")
        except UnicodeDecodeError as e:
            settings.error_logger.error(f"Произошла непредвиденная ошибка {e}")
        except Exception as e:
                # Этот блок выполнится для всех других исключений.
                settings.error_logger.error(f"Произошла непредвиденная ошибка: {e}")



    @commands.slash_command(name="unban", description="Забанить игрока на сервере")
    async def unban(self, inter: disnake.CommandInteraction, user: str):
        # Проверяем, есть ли у пользователя права администратора или специальная роль
        if not inter.author.guild_permissions.administrator:
            if not any(role.id in self.admin_role for role in inter.author.roles):
                await inter.response.send_message("У вас нет прав для использования данной команды.", ephemeral=True)
                return
        try:
            with Client(self.server_ip, self.rcon_port, passwd=self.rcon_password) as client:
                response = client.run(f"unbanuser {user}",encoding="utf-8")
            await inter.response.send_message(f"```Игрок {user} разабанен```", ephemeral=True)
            settings.admin_logger.debug(f"Админ {inter.user} разабанил игрока {user}")
        except UnicodeDecodeError as e:
            settings.error_logger.error(f"Произошла непредвиденная ошибка {e}")
        except Exception as e:
                # Этот блок выполнится для всех других исключений.
                settings.error_logger.error(f"Произошла непредвиденная ошибка: {e}")



    @commands.slash_command(name="banid", description="Забанить игрока на сервере")
    async def banid(self, inter: disnake.CommandInteraction, user: int):
        # Проверяем, есть ли у пользователя права администратора или специальная роль
        if not inter.author.guild_permissions.administrator:
            if not any(role.id in self.admin_role for role in inter.author.roles):
                await inter.response.send_message("У вас нет прав для использования данной команды.", ephemeral=True)
                return
        try:
            with Client(self.server_ip, self.rcon_port, passwd=self.rcon_password) as client:
                response = client.run(f"banid {user}",encoding="utf-8")
            await inter.response.send_message(f"```Игрок {user} забанен```", ephemeral=True)
            settings.admin_logger.debug(f"Админ {inter.user} забанил игрока {user}")
        except UnicodeDecodeError as e:
            settings.error_logger.error(f"Произошла непредвиденная ошибка {e}")
        except Exception as e:
                # Этот блок выполнится для всех других исключений.
                settings.error_logger.error(f"Произошла непредвиденная ошибка: {e}")

    @commands.slash_command(name="unbanid", description="Забанить игрока на сервере")
    async def unban(self, inter: disnake.CommandInteraction, user: int):
        # Проверяем, есть ли у пользователя права администратора или специальная роль
        if not inter.author.guild_permissions.administrator:
            if not any(role.id in self.admin_role for role in inter.author.roles):
                await inter.response.send_message("У вас нет прав для использования данной команды.", ephemeral=True)
                return
        try:
            with Client(self.server_ip, self.rcon_port, passwd=self.rcon_password) as client:
                response = client.run(f"unbanid {user}",encoding="utf-8")
            await inter.response.send_message(f"```Игрок {user} разабанен```", ephemeral=True)
            settings.admin_logger.debug(f"Админ {inter.user} разабанил игрока {user}")
        except UnicodeDecodeError as e:
            settings.error_logger.error(f"Произошла непредвиденная ошибка {e}")
        except Exception as e:
                # Этот блок выполнится для всех других исключений.
                settings.error_logger.error(f"Произошла непредвиденная ошибка: {e}")

    

    @commands.slash_command(name="players", description="Посмотреть список игроков")
    async def players(self, inter: disnake.CommandInteraction):
        # Проверяем, есть ли у пользователя права администратора или специальная роль
        if not inter.author.guild_permissions.administrator:
            if not any(role.id in self.admin_role for role in inter.author.roles):
                await inter.response.send_message("У вас нет прав для использования данной команды.", ephemeral=True)
                return
        try:
            with Client(self.server_ip, self.rcon_port, passwd=self.rcon_password) as client:
                response = client.run(f"players",encoding="utf-8")
            await inter.response.send_message(f"```{response}```", ephemeral=True)
        except UnicodeDecodeError as e:
            settings.error_logger.error(f"Произошла непредвиденная ошибка {e}")
        except Exception as e:
                # Этот блок выполнится для всех других исключений.
                settings.error_logger.error(f"Произошла непредвиденная ошибка: {e}")

    
    @commands.Cog.listener()
    async def on_message(self, message):
    # Проверка, что сообщение не от бота
        if message.author.bot:
            return

        # Инициализируем переменную log_channel
        log_channel = None

        try:
            # Проверка, что сообщение в нужном канале
            if message.channel.id == self.pda_channel:
                # Сохраняем содержимое оригинального сообщения, если требуется
                original_content = message.content
                original_author = message.author
                # Удаляем оригинальное сообщение
                await message.delete()
                await message.channel.send(f"```[Неизвестный пользователь] {original_content}```")
                # Получаем объект канала для логирования
                log_channel = self.bot.get_channel(self.pda_channel_logs)

            # Проверяем, определен ли канал для логирования
            if log_channel:
                # Отправляем лог сообщения
                await log_channel.send(f"Сообщение от пользователя: {original_author.mention}\nСообщение: '{original_content}'")
            else:
                settings.error_logger.error("Канал логов не найден.")
        except Exception as e:
            # Этот блок выполнится для всех других исключений.
            settings.error_logger.error(f"Произошла непредвиденная ошибка: {e}")
        







    async def notify_user(self, message):  
        try:
            channel = self.bot.get_channel(self.channel_id)
            guild = self.bot.get_guild(self.guild_id)  # Получаем объект сервера (Guild)
            if guild:
                role = guild.get_role(self.ping_role)  # Получаем объект роли
                if role:
                    await channel.send(f"{role.mention}\n{message}")  # Отправляем сообщение с упоминанием роли
                else:
                    settings.error_logger.error(f"Роль с ID {self.ping_role} не найдена.")
            else:
                settings.error_logger.error(f"Сервер с ID {self.guild_id} не найден.")
        except Exception as e:
                # Этот блок выполнится для всех других исключений.
                settings.error_logger.error(f"Произошла непредвиденная ошибка: {e}")

    async def _scheduled_start(self):
        try:
            await self.notify_user("```Сервер запуститься через 30 минут```")
            await asyncio.sleep(900)
            await self.notify_user("```Сервер запуститься через 15 минут```")
            await asyncio.sleep(600)
            await self.notify_user("```Сервер запуститься через 5 минут```")
            await asyncio.sleep(240)
            process = subprocess.Popen(self.path, creationflags=subprocess.CREATE_NEW_CONSOLE)
            await asyncio.sleep(60)
            if process.wait() == 0:  
                await self.notify_user("```Сервер запущен```")
                settings.server_logger.info("Сервер удачно запущен")
            else:
                settings.server_logger.info("Сервер не мог запуститься из-за ошибки")
        except Exception as e:
            settings.error_logger.error(f"Произошла непредвиденная ошибка: {e}")

    async def _scheduled_stop(self):
        try:
            with Client(self.server_ip, self.rcon_port, passwd=self.rcon_password, timeout=5) as client:
                response = client.run('servermsg "Server shut down in 30 minutes"')
            settings.server_logger.info(response)
            await self.notify_user("```Сервер выключиться через 30 минут```")
            await asyncio.sleep(900)
            await self.notify_user("```Сервер выключиться через 15 минут```")
            with Client(self.server_ip, self.rcon_port, passwd=self.rcon_password, timeout=5) as client:
                response = client.run('servermsg "Server shut down in 15 minutes"')
            await asyncio.sleep(600)
            await self.notify_user("```Сервер выключиться через 5 минут```")
            with Client(self.server_ip, self.rcon_port, passwd=self.rcon_password, timeout=5) as client:
                response = client.run('servermsg "Server shut down in 5 minutes"')
            await asyncio.sleep(300)
            with Client(self.server_ip, self.rcon_port, passwd=self.rcon_password) as client:
                response = client.run("quit")
            await self.notify_user("```Сервер выключен```")
            await asyncio.wait(120)
            subprocess.run(['taskkill', '/IM', 'cmd.exe', '/F'])
            self.status_server = False
        except Exception as e:
                # Этот блок выполнится для всех других исключений.
                settings.error_logger.error(f"Произошла непредвиденная ошибка: {e}")


    def setup_scheduler(self):
        # Запуск и выключение сервера по расписанию
        self.scheduler.add_job(self.scheduled_server_start, CronTrigger(day_of_week='mon-fri', hour=17, minute=30))
        self.scheduler.add_job(self.scheduled_server_stop, CronTrigger(day_of_week='mon-fri', hour=23, minute=30))
        self.scheduler.add_job(self.scheduled_server_start, CronTrigger(day_of_week='sat-sun', hour=15, minute=30))
        self.scheduler.add_job(self.scheduled_server_stop, CronTrigger(day_of_week='sat-sun', hour=1, minute=30))

        # Проверка статуса сервера и его включение при необходимости в установленные интервалы
        # В будние дни каждые 10 минут с 18:00 до 00:00
        self.scheduler.add_job(self.check_server_status, CronTrigger(day_of_week='mon-fri', hour='18-23', minute='*/2'))
        self.scheduler.add_job(self.check_server_status, CronTrigger(day_of_week='tue-fri', hour='0', minute='*/2'))
        # В выходные каждые 10 минут с 16:00 до 02:00
        self.scheduler.add_job(self.check_server_status, CronTrigger(day_of_week='sat-sun', hour='16-23', minute='*/2'))
        self.scheduler.add_job(self.check_server_status, CronTrigger(day_of_week='sun', hour='0-1', minute='*/2'))

        self.scheduler.start()

    async def check_server_status(self):
        try:
            with Client(self.server_ip, self.rcon_port, passwd=self.rcon_password, timeout=5) as client:
                response = client.run("ping")
                if response == "Unknown command ping":
                    self.status_server = True
                    settings.server_logger.info("Сервер работает.")
                else:
                    self.status_server = False
                    settings.server_logger.info("Сервер не работает.")
        except ConnectionRefusedError:
            # Соединение не удалось, сервер не работает
            self.status_server = False
            settings.server_logger.info("Сервер не работает. Попытка перезапуска.")
            process = subprocess.Popen(self.path, creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            settings.error_logger.error(f"Ошибка при проверке статуса сервера: {e}")

    async def scheduled_server_start(self):
        # Здесь должна быть логика запуска сервера
        await self._scheduled_start()

    async def scheduled_server_stop(self):
        # Здесь должна быть логика остановки сервера
        await self._scheduled_stop()





        




        
    

def setup(bot):
    bot.add_cog(Server_commands(bot))