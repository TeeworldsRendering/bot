from typing import *
from discord.ext import commands
import discord, json, hashlib
from PIL import Image

from utils.utilities import read_json
from cogs.path import *
import cogs.api as API

extensions: Tuple[str] = (
    "cogs.page",
    "cogs.render",
    "cogs.help"
)

ENV: json = read_json("json/env.json")
bot: object = commands.Bot(command_prefix = ['!r ', 'render '])
bot.remove_command("help")

@bot.event
async def on_ready() -> None:
    await bot.change_presence(activity=discord.Game(name="skins.tw"))

@bot.event
async def on_guild_join(guild: object):
    for file in read_json("public/database/starter_kit/ddnet.json"):
        image: Image = Image.open(f"{Path.full}/{file}")
        API.insertSkin(
            guild_id = guild.id,
            user_id = 0x00,
            filename = file[:-4],
            md5_checksum = hashlib.md5(image.tobytes()).hexdigest()
        )

def load_extensions(bot: Any, extensions: List[str]) -> None:
    for extension in extensions:
        bot.load_extension(extension)

if __name__ == "__main__":
    load_extensions(bot, extensions)
    bot.run(ENV["token"])