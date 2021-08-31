import requests, hashlib
from typing import *
from PIL import Image

from cogs.split import *

import cogs.api as API

class TeeAttach(SplitTeeworldsSkin):
    """Controlling attachments for teeworlds skin"""
    def __init__(self, attach: object, msg: object):
        SplitTeeworldsSkin.__init__(self, attach.filename)
        self.attach: object = attach
        self.allowed: bool = True
        self.msg: object = msg

    def isAttachAllowed(self) -> bool:
        """Check if its the right image format"""
        return ".png" in self.attach.filename

    def downloadAttach(self) -> None:
        """Download the image"""
        twskin: object

        if (not self.isAttachAllowed()):
            self.allowed = False
            return
        image: object = Image.open(requests.get(self.attach.url, stream = True).raw)
        if (not self.isGoodSize(image)):
            self.allowed = False
            return

        API.insertSkin(
            guild_id = self.msg.guild.id,
            user_id = self.msg.author.id,
            filename = self.name[:-4],
            md5_checksum = hashlib.md5(image.tobytes()).hexdigest()
        )

        if (self.isInDatabase()): return

        # Save
        image.save(f"{self.full}/{self.name}")
        print(f"{self.name} saved in {self.full}")

        # Split
        self.splitTee()
        print(f"{self.name} has been splitted")