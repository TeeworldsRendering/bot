from discord.ext import commands
from typing import *

from cogs.path import *
import cogs.color as tint
from utils.utilities import *

@dataclass
class Page:
    """Page object"""
    ctx: object
    page: int
    pages: List[List[str]]
    author_id: str
    _type: str

class Pages:
    """Class that manage Page objects"""
    def __init__(self) -> None:
        self.pages: Dict[int, Page] = {}
    
    async def change_page(self, r_dst: object, msg_id: str, r_src: str, move: int, user: object):
        """Go to previous or next page"""
        if (str(r_dst) != r_src): return
        if (not msg_id in list(self.pages.keys())): return

        obj: Page = self.pages[msg_id]
        if (obj.author_id != user.id or obj._type != "skinlist"): return

        # Check out of range
        if (obj.page + move < 0 or obj.page + move > len(obj.pages) - 1):
            return

        # Change page
        obj.page += move

        # Edit msg with fancy display
        display: str = "```" + '\n'.join(obj.pages[obj.page]) + "```"
        embed = discord.Embed(color=0x000000, description=display)
        embed.set_footer(text=f"page {obj.page + 1} / {len(obj.pages)}")
        await obj.ctx.edit(embed=embed)

    async def check_for_pages(self, reaction: object, user: object):
        """Check reactions for page"""
        _id: int = reaction.message.id
    
        await self.change_page(reaction, _id, REACTION["pages"]["previous"], -1, user)
        await self.change_page(reaction, _id, REACTION["pages"]["next"], 1, user)

class Skins(commands.Cog, Pages):
    """Page commands"""
    def __init__(self) -> None:
        Pages.__init__(self)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: object, user: object):
        if (not reaction.message.author.bot or user.bot):
            return
        await reaction.remove(user)
        await self.check_for_pages(reaction, user)
    
    @commands.command(aliases=["list"])
    async def List(self, ctx: object):
        """Show every skin name"""
        pages: List[List[str]] = groupList(API.selectFilenamesByGuildId(ctx.guild.id), 10) \
            or [["Empty"]]
        embed = discord.Embed(color=0x000000, description="```" + "\n".join(pages[0]) + "```")
        embed.set_footer(text=f"page {0 + 1} / {len(pages)}")
        msg: object = await ctx.send(embed = embed)

        for _, v in REACTION["pages"].items():
            await msg.add_reaction(v)
        self.pages[msg.id] = Page(msg, 0, pages, ctx.author.id, "skinlist")
    
def setup(bot: commands.Bot):
    bot.add_cog(Skins())