from typing import *
from PIL import Image, ImageOps
from math import *
import os, glob

from cogs.path import *

class SplitTeeworldsSkins(Path):
    def __init__(self) -> None:
        self.full_list: List[str] = filterDir(self.full)
    
    def fullsplit(self) -> None:
        """Split every skin"""
        for i, name in enumerate(self.full_list):
            SplitTeeworldsSkin(name).splitTee()
            print(f"{ceil((i * 100 / len(self.full_list)))}% [+] {name}")
        print(f"\n\nSuccesfully splitted every skin in {self.full}")
    
    def rmSplitted(self) -> None:
        for d in self.dirs_splitted:
            [os.remove(skin) for skin in glob.glob(f"{d}/*.png")]

class SkinSize:
    skin_w: int = 256
    skin_h: int = 128

class SplitTeeworldsSkin(Path, SkinSize):
    """Split a teeworlds skin into multiple images"""

    def __init__(self, filename: str) -> None:
        self.name: str = filename

    def isGoodSize(self, image: object) -> bool:
        """Check for allowed proportions"""
        return (image.size[0] == image.size[1] * 2)

    def isInDatabase(self) -> bool:
        """Check if skin exist"""
        return all(self.name in filterDir(x) for x in self.dirs_splitted)

    def _split(self, src: str, pos: List[int], size: List[int]) -> object:
        """Crop an image (src) into (dest)"""
        image: object = Image.open(src)
        ratio: int = image.size[0] / self.skin_w

        npos = list(map(lambda x: x * ratio, pos))
        nsize = list(map(lambda x: x * ratio, size))
        image = image.crop((npos[0], npos[1], nsize[0] + npos[0], nsize[1] + npos[1]))
        image = image.resize((size[0], size[1]))
        return image

    def splitTee(self) -> None:
        """Split entire tee"""
        src: str = f"{self.full}/{self.name}"

        if not self.isGoodSize(Image.open(src)) or self.isInDatabase():
            return

        # Body
        self._split(src, [0, 0], [96, 96]).save(f"{self.body}/{self.name}")
        # Body shadow
        self._split(src, [96, 0], [96, 96]).save(f"{self.body}/{self.name[:-4]}_shadow.png")

        # Eye
        self._split(src, [64, 96], [32, 32]).save(f"{self.eye}/{self.name}")
        
        # Feet
        self._split(src, [192, 32], [64, 32]).save(f"{self.feet}/{self.name}")
        # Feet shadow
        self._split(src, [192, 64], [64, 32]).save(f"{self.feet}/{self.name[:-4]}_shadow.png")

        # Hand
        self._split(src, [192, 0], [32, 32]).save(f"{self.hand}/{self.name}")
        # Hand shadow
        self._split(src,  [224, 0], [32, 32]).save(f"{self.hand}/{self.name[:-4]}_shadow.png")