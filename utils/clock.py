from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import discord, os

def get_clock() -> str:
    return datetime.now().strftime("%H:%M:%S")

def gen_clock(name: str, data: str) -> None:
    img = Image.new('RGBA', (110, 30), color = (114,137,218,0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(font="fonts/kayak.otf", size=29)
    d.text((1,1), data, font=font, fill=(255,255,255))
    img.save(name)

async def send_time(ctx: object, path: str, data: str) -> object:
    gen_clock(path, data)
    embed = discord.Embed(color=0x000000)
    embed.set_image(url=f"attachment://{path}")
    await ctx.send(file=discord.File(path), embed=embed)
    os.remove(path)