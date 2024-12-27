import disnake
from disnake.ext import commands
import settings
import random
import os

class Discord_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channel = settings.welcome_channel
        self.images_folder = settings.images_folder

    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcome_channel = self.bot.get_channel(self.welcome_channel)
        if welcome_channel:
            # Создание объекта Embed
            embed = disnake.Embed(
                title="Пересек периметр!",
                description=f"{member.mention}, приветствуем, сталкер!",
                color=disnake.Color.green()
            )
            # Получаем список всех файлов в папке с изображениями
            images = [file for file in os.listdir(self.images_folder) if file.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            # Выбираем случайное изображение
            if images:
                random_image_path = os.path.join(self.images_folder, random.choice(images))
                file = disnake.File(random_image_path, filename="image.png")
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_image(url=f"attachment://image.png")
                embed.set_footer(text="Никому не доверяй!")
                # Отправляем эмбед с изображением как вложение
                await welcome_channel.send(embed=embed, file=file)
            else:
                # Отправляем только эмбед, если изображения нет
                await welcome_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Discord_commands(bot))