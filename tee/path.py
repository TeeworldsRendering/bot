from typing import *
from dataclasses import dataclass
import os

from tee.api import *
from utilities import *

REACTIONS: json = read_json("json/reaction.json")

class Path:
    """Img paths"""
    root: str = "public/database/skin"
    scenes: str = "public/database/scenes"
    body: str = f"{root}/body"
    eye: str = f"{root}/eye"
    feet: str = f"{root}/feet"
    full: str = f"{root}/full"
    hand: str = f"{root}/hand"
    dirs_splitted: List[str] = [body, eye, feet, hand]

def groupList(arr: list, size: int) -> list:
    return [arr[i:i + size] for i in range(0, len(arr), size)]

def filterDir(_dir: str, extension: str = ".png") -> List[str]:
    return sorted(list(filter(lambda x: extension in x, os.listdir(_dir))))

@dataclass
class SkinList:
    """SkinList object"""
    ctx: object
    page: int
    author_id: str

class SkinsList:
    """Controlling SkinList objects and reactions for the skin list"""
    def __init__(self) -> None:
        self.skinlist_msg: Dict[str, SkinList] = {}
        self.pages: Dict[str, List[List[str]]] = {}

    def add(self, obj: SkinList) -> None:
        """Add SkinList object in the dict"""
        self.skinlist_msg[str(obj.ctx.id)] = obj

    def setPages(self, _id: str) -> List[List[str]]:
        """Init every page"""
        self.pages[_id] = groupList(Api().selectFilenamesByGuildId(_id), 10) \
            or [["Empty"]]
        return self.pages[_id]
        
    async def discordSendChangePage(self, reaction_dest: object, 
    msg_id: str, reaction_src: str, move: int, user: object) -> None:
        """Change t list page"""
        if (str(reaction_dest) != reaction_src): return
        if (not msg_id in list(self.skinlist_msg.keys())): return
        if (self.skinlist_msg[msg_id].author_id != user.id): return

        pages: List[List[str]] = self.setPages(str(reaction_dest.message.guild.id))
        obj: SkinList = self.skinlist_msg[msg_id]
        if (obj.page + move < 0 or obj.page + move > len(pages) - 1):
            return
        obj.page += move

        # add '_' because Discord markdown in embed seems to be bugged
        fullPage: str = ["_"] + pages[obj.page]
        embed = discord.Embed(color=0x000000, description="```" + "\n".join(fullPage) + "```")
        embed.set_footer(text=f"page {obj.page + 1} / {len(pages)}")
        await obj.ctx.edit(embed=embed)

    async def skinsListReact(self, reaction: object, msg_id: str, user: object) -> None:
        """Check reactions"""
        await self.discordSendChangePage(reaction, msg_id, REACTIONS["skin_list"]["previous"], -1, user)
        await self.discordSendChangePage(reaction, msg_id, REACTIONS["skin_list"]["next"], 1, user)