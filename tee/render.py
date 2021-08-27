import discord, os, uuid
from typing import *
from PIL import Image, ImageOps
from dataclasses import dataclass

from tee.path import *
from utilities import *

REACTIONS: json = read_json("json/reaction.json")

class RenderSize:
    skin_w: int = 100
    skin_h: int = 100
    scene_w: int = 576
    scene_h: int = 320

class TeeRender(Path, RenderSize):
    """Controlling teeworlds skin rendering"""

    def __init__(self, ctx: object, skinname: str, scenename: str = "test"):
        self.ctx: object = ctx
        self.sent_msg: object
        self.buildname: str
        self.scene: Image
        self.scenename: str = f"{scenename}.png"
        self.skin: Image
        self.skinname = skinname
        self.visual: Image

    def setbuildname(self) -> None:
        """Change the tmp image name"""
        self.buildname: str = f"{uuid.uuid1()}.png"

    def buildSkin(self) -> None:
        """Assemble a teeworlds skin"""
        self.setbuildname()
        # Init images objects
        image: Image = Image.new("RGBA", (self.skin_w, self.skin_w))
        body: Image = Image.open(f"{self.body}/{self.skinname}")
        body_s: Image = Image.open(f"{self.body}/{self.skinname[:-4]}_shadow.png")
        eye_l: Image = Image.open(f"{self.eye}/{self.skinname}").resize((38, 38))
        eye_r: Image = ImageOps.mirror(eye_l)
        feet: Image = Image.open(f"{self.feet}/{self.skinname}").resize((83, 42))
        feet_s: Image = Image.open(f"{self.feet}/{self.skinname[:-4]}_shadow.png").resize((83, 42))
    
        # Create visual
        image.alpha_composite(feet_s, dest = (0, 50))
        image.alpha_composite(feet_s, dest = (18 + 4, 50))
        image.alpha_composite(body_s, dest = (0 + 4, 0))
        image.alpha_composite(feet, dest = (0, 50))
        image.alpha_composite(body, dest = (0 + 4, 0))
        image.alpha_composite(feet, dest = (18 + 4, 50))
        image.alpha_composite(eye_l, dest = (35 + 4, 25))
        image.alpha_composite(eye_r, dest = (47 + 4, 25))
        image.save(f"{self.buildname}", quality = 95)
        self.skin = image

    def buildScene(self) -> None:
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

        self.scene = image

    def buildSkinOnScene(self) -> None:
        """Assemble scene with the skin"""
        self.visual: Image = Image.new("RGBA", (self.scene_w, self.scene_h))

        # Build visual
        self.buildSkin()
        self.buildScene()
        
        # Paste scene and skin on the new image
        self.visual.alpha_composite(self.scene, dest = (0, 0))
        self.visual.alpha_composite(self.skin, dest = ((self.scene_w - 
        self.skin_w) // 2, self.scene_h - 64 * 2 - self.skin_w + 18))

        # Overwrite self.buildname
        self.visual.save(f"{self.buildname}", quality = 95)

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