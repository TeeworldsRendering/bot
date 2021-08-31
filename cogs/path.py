from typing import *
from dataclasses import dataclass
import os

import cogs.api as API
from utils.utilities import *

REACTION: json = read_json("json/reaction.json")

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