import discord, os, uuid
from typing import *
from PIL import Image, ImageOps
from dataclasses import dataclass

from tee.path import *
import tee.color as tint
from utilities import *

REACTIONS: json = read_json("json/reaction.json")

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
    skin_w: int = 100
    skin_h: int = 100
    scene_w: int = 576
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
            tee.Body = tint.applyColor(tee.Body, color.cBody, tint._mod)
            tee.Feet = tint.applyColor(tee.Feet, color.cFeet, tint._mod)

        # Create visual
        func(image, tee)
        image.save(f"{self.buildname}", quality = 95)
        return (image)

    def buildScene(self) -> Image:
        """Assemble a scene"""
        image: Image = Image.new("RGBA", (self.scene_w, self.scene_h))
        scene: Image = Image.open(f"{Path.scenes}/{self.scenename}")
        out_ground: Image = scene.crop((0, 0, 64, 64))
        in_ground: Image = scene.crop((64, 0, 64 + 64, 64 + 64))

        # Background
        bg: Image = scene.crop((0, 64, self.scene_w, 64 + self.scene_h))
        image.alpha_composite(bg, dest = (0, 0))

        # In ground
        for x in range(0, self.scene_w, 64):
            image.alpha_composite(in_ground, dest = (x, self.scene_h - 64 * 1))

        # Out ground
        for x in range(0, self.scene_w, 64):
            image.alpha_composite(out_ground, dest = (x, self.scene_h - 64 * 2))
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
        self.skin_w) // 2, self.scene_h - 64 * 2 - self.skin_w + 18))

        # Overwrite self.buildname
        visual.save(f"{self.buildname}", quality = 95)

    async def discordSend(self) -> None:
        """Send the image to discord channel"""
        embed = discord.Embed(color=0x000000)
        embed.set_image(url=f"attachment://{self.buildname}")
        embed.set_footer(text=self.skinname[:-4])
        msg: object = await self.ctx.channel.send(file=discord.File(self.buildname), embed=embed)
        for _, v in REACTIONS["render"].items():
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
    
    async def discordSendOriginalSkin(self, reaction: object, msg_id: str, user: object) -> None:
        """"Send original teeworlds skin to discord channel"""
        if (str(reaction) != REACTIONS["render"]["download"]): return
        if (not msg_id in list(self.renders.keys())): return

        skinname: str = f"{self.full}/{self.renders[msg_id].skinname}"
        await user.send(file=discord.File(skinname))

    async def discordRmRender(self, reaction: object, msg_id: str, user: object) -> None:
        """Remove skin files and associated Discord messages"""
        if (str(reaction) != REACTIONS["render"]["remove"]): return
        if (not msg_id in list(self.renders.keys())): return
        if (not user.guild_permissions.administrator): return
    
        obj: TeeRender = self.renders[msg_id]

        if (hasattr(obj.ctx, 'message')):
            obj.ctx = obj.ctx.message

        await obj.ctx.delete()
        await obj.sent_msg.delete()
        Api().deleteSkin(
            guild_id = obj.ctx.guild.id, 
            filename = obj.skinname[:-4]
        )
        del self.renders[msg_id]
        await bmessage(obj.ctx.channel, f"❌ `{obj.skinname[:-4]}` has been removed")
    
    async def discordSendScenesList(self, reaction: object, user: object) -> None:
        """Send a list with every scenes"""
        if (str(reaction) != REACTIONS["render"]["help_scenes"]): return

        # add _.png because Discord markdown in embed seems to be bugged
        full_list: str = ["_.png"] + list(map(lambda x: x[:-4], filterDir(self.scenes)))
        embed = discord.Embed(color=0x000000, title="Scenes", 
        description='```'+'\n'.join(full_list)+'```')
        embed.set_footer(text="Usage: t skin <skin_name> <scene_name>")

        await user.send(embed=embed)
    
    async def rendersReact(self, reaction: object, msg_id: str, user: object) -> None:
        """Check reactions"""
        await self.discordSendOriginalSkin(reaction, msg_id, user)
        await self.discordSendScenesList(reaction, user)
        await self.discordRmRender(reaction, msg_id, user)