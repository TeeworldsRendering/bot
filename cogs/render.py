import discord, os, uuid
from discord.ext import commands
from typing import *
from PIL import Image, ImageOps

from cogs.path import *
import cogs.color as tint
from utils.utilities import *
from cogs.attach import *

ENV: json = read_json("json/env.json")
REACTION: json = read_json("json/reaction.json")

class Tee(Path):
    """Tee object"""
    def __init__(self, name: str) -> None:
        self.Body: Image = Image.open(f"{self.body}/{name}")
        self.Body_s: Image = Image.open(f"{self.body}/{name[:-4]}_shadow.png")
        self.Eye_l: Image = Image.open(f"{self.eye}/{name}").resize((38, 38))
        self.Eye_r: Image = ImageOps.mirror(self.Eye_l)
        self.Feet: Image = Image.open(f"{self.feet}/{name}").resize((83, 42))
        self.Feet_s: Image = Image.open(f"{self.feet}/{name[:-4]}_shadow.png").resize((83, 42))

class RenderSize:
    """Some images size"""
    skin_w: int = 100
    skin_h: int = 100
    scene_w: int = 546
    scene_h: int = 320

class ColorVerify:
    """Verify is color is allowed"""
    def __init__(self, args: str) -> None:
        self.args: List[str] = args
        self.allowed: bool = False
    
    def checkLen(self) -> bool:
        """Check the len"""
        return (len(self.args) == 6)

    def checkByte(self) -> bool:
        """Check the bytes value"""
        f: callable = lambda x: int(x) >= 0 and int(x) <= 255
        return (all([f(x) for x in self.args]))

    def checkType(self) -> bool:
        """Check the type"""
        return (all([x.isdigit() for x in self.args]))

    def check(self) -> None:
        """Check everything"""
        if (not self.checkType()):
            self.allowed = False
            return
        self.allowed = self.checkLen() and self.checkByte()
    
class ColorParse(ColorVerify):
    """Parse color Discord argument"""
    def __init__(self, args: str) -> None:
        super().__init__(args.split())
        self.check()
        if (self.allowed):
            args = list(map(int, self.args))
            self.cBody = tuple(args[:3] + [255])
            self.cFeet = tuple(args[3:] + [255])

class TeeRender(Path, RenderSize):
    """Controlling teeworlds skin rendering"""

    def __init__(self, ctx: object, skinname: str, scenename: str = "test"):
        self.ctx: object = ctx
        self.sent_msg: object
        self.buildname: str
        self.scenename: str = f"{scenename}.png"
        self.skinname: str = skinname

    def setbuildname(self) -> None:
        """Change the tmp image name"""
        self.buildname: str = f"{uuid.uuid1()}.png"

    def buildNormal(self, image: Image, tee: Tee) -> None:
        """Assemble a teeworlds skin with the normal way"""
        image.alpha_composite(tee.Feet_s, dest = (0, 50))
        image.alpha_composite(tee.Feet_s, dest = (18 + 4, 50))
        image.alpha_composite(tee.Body_s, dest = (0 + 4, 0))
        image.alpha_composite(tee.Feet, dest = (0, 50))
        image.alpha_composite(tee.Body, dest = (0 + 4, 0))
        image.alpha_composite(tee.Feet, dest = (18 + 4, 50))
        image.alpha_composite(tee.Eye_l, dest = (35 + 4, 25))
        image.alpha_composite(tee.Eye_r, dest = (47 + 4, 25))
    
    def buildDumb(self, image: Image, tee: Tee) -> None:
        """Assemble a teeworlds skin with nouis eyes"""
        image.alpha_composite(tee.Feet_s, dest = (0, 50))
        image.alpha_composite(tee.Feet_s, dest = (18 + 4, 50))
        image.alpha_composite(tee.Body_s, dest = (0 + 4, 0))
        image.alpha_composite(tee.Feet, dest = (0, 50))
        image.alpha_composite(tee.Body, dest = (0 + 4, 0))
        image.alpha_composite(tee.Feet, dest = (18 + 4, 50))
        image.alpha_composite(tee.Eye_l, dest = (10 + 4, 25))
        image.alpha_composite(tee.Eye_r, dest = (50 + 4, 25))

    def buildSkin(self, args: str, build: str = "default") -> Image:
        """Assemble a teeworlds skin"""
        self.setbuildname()
        builds: Dict[str, callable] = {
            "dumb": self.buildDumb,
            "later": lambda x: x
        }
        func: callable = builds[build] if build in builds.keys() else self.buildNormal

        # Init images objects
        image: Image = Image.new("RGBA", (self.skin_w, self.skin_w))
        tee: Tee = Tee(self.skinname)
    
        # Apply colors
        color: ColorParse = ColorParse(args)
        if (color.allowed):
            # .convert('LA') for grayscale before coloring skin
            tee.Body = tint.applyColor(tee.Body.convert('LA').convert('RGBA'), color.cBody, tint._mod)
            tee.Feet = tint.applyColor(tee.Feet.convert('LA').convert('RGBA'), color.cFeet, tint._mod)

        # Create visual
        func(image, tee)
        image.save(f"{self.buildname}", quality = 95)
        return (image)

    def buildScene(self) -> Image:
        """Assemble a scene"""
        image: Image = Image.new("RGBA", (self.scene_w, self.scene_h))
        scene: Image = Image.open(f"{Path.scenes}/{self.scenename}")
        out_ground: Image = scene.crop((0, 0, 42, 42))
        in_ground: Image = scene.crop((42, 0, 42 + 42, 42 + 42))

        # Background
        bg: Image = scene.crop((0, 42, self.scene_w, 42 + self.scene_h))
        image.alpha_composite(bg, dest = (0, 0))

        # In ground
        for x in range(0, self.scene_w, 42):
            image.alpha_composite(in_ground, dest = (x, self.scene_h - 42 * 1))

        # Out ground
        for x in range(0, self.scene_w, 42):
            image.alpha_composite(out_ground, dest = (x, self.scene_h - 42 * 2))
        return (image)

    def buildSkinOnScene(self, args: str, build: str = "default") -> None:
        """Assemble scene with the skin"""
        visual: Image = Image.new("RGBA", (self.scene_w, self.scene_h))

        # Build visual
        skin: Image = self.buildSkin(args, build)
        scene: Image = self.buildScene()
        
        # Paste scene and skin on the new image
        visual.alpha_composite(scene, dest = (0, 0))
        visual.alpha_composite(skin, dest = ((self.scene_w - 
        self.skin_w) // 2, self.scene_h - 42 * 2 - self.skin_w + 18))

        # Overwrite self.buildname
        visual.save(f"{self.buildname}", quality = 95)

    async def discordSend(self) -> None:
        """Send the image to discord channel"""
        embed = discord.Embed(color=0x000000)
        embed.set_image(url=f"attachment://{self.buildname}")
        embed.set_footer(text=self.skinname[:-4])
        msg: object = await self.ctx.channel.send(file=discord.File(self.buildname), embed=embed)
        for _, v in REACTION["render"].items():
            await msg.add_reaction(v)
        self.sent_msg = msg
        os.remove(self.buildname)

class TeeRenders(Path):
    """Controlling multiple clients render and managing react on renders"""
    def __init__(self) -> None:
        self.renders: Dict[str, TeeRender] = {}

    def add(self, render: TeeRender) -> None:
        """Append a render of one client"""
        self.renders[str(render.sent_msg.id)] = render
    
    async def download(self, reaction: object, msg_id: str, user: object) -> None:
        """"Send original teeworlds skin to discord channel"""
        if (str(reaction) != REACTION["render"]["download"]): return
        if (not msg_id in list(self.renders.keys())): return

        skinname: str = f"{self.full}/{self.renders[msg_id].skinname}"
        await user.send(file=discord.File(skinname))

    async def _rm(self, reaction: object, msg_id: str, user: object) -> None:
        """Remove skin files and associated Discord messages"""
        if (str(reaction) != REACTION["render"]["remove"]): return
        if (not msg_id in list(self.renders.keys())): return
        if (not user.guild_permissions.administrator): return
    
        obj: TeeRender = self.renders[msg_id]

        if (hasattr(obj.ctx, 'message')):
            obj.ctx = obj.ctx.message

        await obj.ctx.delete()
        await obj.sent_msg.delete()
        API.deleteSkin(
            guild_id = obj.ctx.guild.id, 
            filename = obj.skinname[:-4]
        )
        del self.renders[msg_id]
        await bmessage(obj.ctx.channel, f"❌ `{obj.skinname[:-4]}` has been removed")
    
    async def discordSendScenesList(self, reaction: object, user: object) -> None:
        """Send a list with every scenes"""
        if (str(reaction) != REACTION["render"]["help_scenes"]): return

        # add _.png because Discord markdown in embed seems to be bugged
        full_list: str = ["_.png"] + list(map(lambda x: x[:-4], filterDir(self.scenes)))
        embed = discord.Embed(color=0x000000, title="Scenes", 
        description='```'+'\n'.join(full_list)+'```')
        embed.set_footer(text="Usage: !r skin <skin_name> <scene_name>")

        await user.send(embed=embed)
    
    async def rendersReact(self, reaction: object, user: object) -> None:
        """Check reactions"""
        _id :str = str(reaction.message.id)
    
        await self.download(reaction, _id, user)
        await self.discordSendScenesList(reaction, user)
        await self._rm(reaction, _id, user)
    
class Render(commands.Cog, TeeRenders):
    """Manage role add and update"""
    def __init__(self, bot: commands.Bot) -> None:
        TeeRenders.__init__(self)
        self.bot: commands.Bot = bot

    async def _skin(self, ctx: object, name: str, colors: str, scene: str, build: str):
        """Show the assembled skin with an optional scene"""
        if (not name or not f"{name}.png" in filterDir(Path.full)): return
        if (not name in API.selectFilenamesByGuildId(ctx.guild.id)): return

        render = TeeRender(ctx, f"{name}.png", scene)
        if (not scene):
            render.buildSkin(colors, build)
        elif (not f"{scene}.png" in filterDir(Path.scenes)):
            return
        else:
            render.buildSkinOnScene(colors, build)
        await render.discordSend()
        self.add(render) 

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: object, user: object):
        if (not reaction.message.author.bot or user.bot):
            return
        await reaction.remove(user)
        await self.rendersReact(reaction, user)

    @commands.command()
    async def skin(self, ctx: object, name: str = None, colors: str = "no", scene: str = None):
        """Displays an assembled teeworlds skin"""
        await self._skin(ctx, name, colors, scene, "default")
    
    @commands.command()
    async def dumb(self, ctx: object, name: str = None, colors: str = "no", scene: str = None):
        """Displays an assembled teeworlds skin with a dumb expression"""
        await self._skin(ctx, name, colors, scene, "dumb")
    
    async def TeeMsgAttach(self, message: object) -> None:
        """Controlling Discord attachments for teeworlds"""
        attachs: object = message.attachments

        if (len(attachs) != 1): return
        if (message.author.bot and not message.author.id in ENV["whitelist"]): return

        attach: TeeAttach = TeeAttach(attachs[0], message)
        attach.downloadAttach()
        if (not attach.allowed):
            return
        visual: TeeRender = TeeRender(message, attach.name)
        visual.buildSkin("no color")
        await visual.discordSend()
        self.add(visual)
    
    @commands.Cog.listener()
    async def on_message(self, message: object):
        if (not isinstance(message.channel, discord.DMChannel)): 
            if (message.channel.name == "skin-rendering"):
                await self.TeeMsgAttach(message)
        #await bot.process_commands(message)
    
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def rm(self, ctx: object, skinname: str = None):
        """Remove skin from guild"""
        if (not skinname or not f"{skinname}.png" in filterDir(Path.full)): return
        if (not skinname in API.selectFilenamesByGuildId(ctx.guild.id)): return

        API.deleteSkin(guild_id=ctx.guild.id, filename=skinname)
        await bmessage(ctx, f"❌ `{skinname}` has been removed")

    @commands.command()
    async def scene(self, ctx: object):
        """Send a message that explain how to create a scene"""
        embed = discord.Embed(color=0x000000, title="How to build your own scene ?")
        embed.set_image(url="attachment://help.png")
        embed.set_footer(text="to add your scene to the list, send it to an admin")

        await ctx.send(file=discord.File("public/database/help.png"), embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(Render(bot))