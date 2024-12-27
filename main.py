import disnake
from disnake.ext import commands
import os
import settings
import sys





class PersistentViewBot(commands.Bot):
    def __init__(self): 
        super().__init__(command_prefix=settings.prefix, intents=disnake.Intents().all())
        self.persistent_views_added = False
    async def on_ready(self):
        images_folder = 'images'
        if not os.path.exists(images_folder):
            os.makedirs(images_folder)
            print(f"Папка '{images_folder}' успешно создана.")
        else:
            print(f"Папка '{images_folder}' уже существует.")
        
        if not self.persistent_views_added:
        

            self.persistent_views_added = True
        print(f"=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\nБот запущен\nName: {bot.user.name}#{bot.user.discriminator}\nID: {bot.user.id}\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=") #тут бот принтует в консоль при запуске, можно написать что угодно
    

if getattr(sys, 'frozen', False):
    # Путь к каталогу исполняемого файла, если скрипт скомпилирован
    base_path = sys._MEIPASS
else:
    # Путь к каталогу исходного скрипта, если скрипт не скомпилирован
    base_path = os.path.dirname(os.path.abspath(__file__))

bot = PersistentViewBot()

cogs_directory = os.path.join(base_path, 'cogs')

for filename in os.listdir(cogs_directory):
    if filename.endswith('.py'):
        cog_path = os.path.join(cogs_directory, filename)
        # Загрузить cog
        bot.load_extension(f'cogs.{filename[:-3]}')

@bot.remove_command("help") #это удаляет стандартную и не красивую команду help
        
@bot.slash_command(description='Загрузить модуль бота') #эта команда отвечает за загрузку когов
@commands.is_owner()
async def load(inter: disnake.CommandInteraction, module: str = commands.Param(name="module", description="Название модуля")):
    bot.load_extension(f"cogs.{module}")
    await inter.response.send_message(f"Загружен модуль `{module}`",ephemeral=True)

@bot.slash_command(description='Выгрузить модуль бота') #эта команда отвечает за выгрузку когов (отключение)
@commands.is_owner()
async def unload(inter: disnake.CommandInteraction, module: str = commands.Param(name="module", description="Название модуля")):
    bot.unload_extension(f"cogs.{module}")
    await inter.response.send_message(f"Выгружен модуль `{module}`",ephemeral=True)
    
@bot.slash_command(description="Перезагрузить модуль бота") #эта команда отвечает за перезагрузку когов (т.е не обязательно перезагружать бота, можно перезагрузить сам ког)
@commands.is_owner()
async def reload(inter: disnake.CommandInteraction, module: str = commands.Param(name="module", description="Название модуля")):
    bot.reload_extension(f"cogs.{module}")
    await inter.response.send_message(f"Перезагружен модуль `{module}`",ephemeral=True)
    

bot.run(settings.bot_token)