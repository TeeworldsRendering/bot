from discord.ext import commands
from typing import *
import discord, asyncio

from clock import *
from utilities import *
from tee.skin import *
from tee.render import *
from tee.attach import *
from tee.api import *
from tee.path import *

ENV: json = read_json("json/env.json")
bot = commands.Bot(command_prefix = ['!r ', 'render '])
bot.remove_command("help")

async def _clock() -> None:
    """Clock that update every 10 secondes"""
    while 42:
        await bot.change_presence(activity=discord.Game(name=f"[{get_clock()}]"))
        await asyncio.sleep(10)

@bot.event
async def on_ready() -> None:
    asyncio.create_task(_clock())

renders: TeeRenders = TeeRenders()
skinsHelp: SkinsList = SkinsList()
api: Api = Api()

@bot.event
async def on_guild_join(guild: object):
    for file in read_json("public/database/starter_kit/ddnet.json"):
        image: Image = Image.open(f"{Path.full}/{file}")
        api.insertSkin(
            guild_id = guild.id,
            user_id = 0x00,
            filename = file[:-4],
            md5_checksum = hashlib.md5(image.tobytes()).hexdigest()
        )

async def TeeMsgAttach(message: object) -> None:
    """Controlling Discord attachments for teeworlds"""
    attachs: object = message.attachments
    attach: TeeAttach
    visual: TeeRender

    if (len(attachs) != 1 or message.author.bot):
        return
    attach = TeeAttach(attachs[0], message)
    attach.downloadAttach()
    if (not attach.allowed):
        return
    visual = TeeRender(message, attach.name)
    visual.buildSkin("no color")
    await visual.discordSend()
    renders.add(visual)

@bot.event
async def on_message(message: object):
    if (not isinstance(message.channel, discord.DMChannel)): 
        if (message.channel.name == "tee"):
            await TeeMsgAttach(message)
    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction: object, user: object):
    if (not reaction.message.author.bot or user.bot):
        return
    await reaction.remove(user)
    await renders.rendersReact(reaction, str(reaction.message.id), user)
    await skinsHelp.skinsListReact(reaction, str(reaction.message.id), user)

@bot.command()
async def skin(ctx: object, name: str = None, colors: str = "no color", scene: str = None):
    """Show the assembled skin with an optional scene"""
    render: TeeRender

    if (not name or not f"{name}.png" in filterDir(Path.full)): return
    if (not name in api.selectFilenamesByGuildId(ctx.guild.id)): return

    render = TeeRender(ctx, f"{name}.png", scene)
    if (not scene):
        render.buildSkin(colors)
    elif (not f"{scene}.png" in filterDir(Path.scenes)):
        return
    else:
        render.buildSkinOnScene(colors)
    await render.discordSend()
    renders.add(render)  

@bot.command(pass_context = True)
async def help(ctx: object):
    """Shows the help menu"""
    await display_panel(ctx, "json/panel.json", "help")

@bot.command(aliases=["list"])
async def List(ctx: object, page: int = 0):
    """Show every skin"""
    skinsHelp.setPages(str(ctx.guild.id))
    pages: List[List[str]] = skinsHelp.pages[str(ctx.guild.id)]
    # add '_' because Discord markdown in embed seems to be bugged
    full_page: str = ["_"] + pages[page]
    embed = discord.Embed(color=0x000000, description="```" + "\n".join(full_page) + "```")
    embed.set_footer(text=f"page {page + 1} / {len(pages)}")
    msg: object = await ctx.send(embed = embed)

    for _, v in REACTIONS["skin_list"].items():
        await msg.add_reaction(v)
    skinsHelp.add(SkinList(msg, page, ctx.author.id))

@commands.has_permissions(administrator=True)
@bot.command()
async def rm(ctx: object, skinname: str = None):
    """Remove skin from guild"""
    if (not skinname or not f"{skinname}.png" in filterDir(Path.full)): return
    if (not skinname in api.selectFilenamesByGuildId(ctx.guild.id)): return

    api.deleteSkin(guild_id=ctx.guild.id, filename=skinname)
    await bmessage(ctx, f"❌ `{skinname}` has been removed")

@bot.command()
async def scene(ctx: object):
    """Send a message that explain how to create a scene"""
    embed = discord.Embed(color=0x000000, title="How to build your own scene ?")
    embed.set_image(url="attachment://help.png")
    embed.set_footer(text="to add your scene to the list, send it to an admin")

    await ctx.send(file=discord.File("help.png"), embed=embed)

if __name__ == "__main__":
    bot.run(ENV["token"])