import requests, json

from utilities import *

ENV: json = read_json("json/env.json")

class Api:
    """Sending request to the rest api"""
    def __init__(self) -> None:
        self.end: str = f"http://{ENV['host']}:{ENV['port']}"
    
    def selectAll(self) -> list:
        """Return the entire skin table"""
        r: object = requests.get(url = f"{self.end}/skin/all")
        return (r.json())
    
    def selectByGuildId(self, _id: int) -> list:
        """Return the guild skins"""
        r: object = requests.get(url = f"{self.end}/skin/guild/{_id}")
        return (r.json())

    def selectFilenamesByGuildId(self, _id: int) -> list:
        """Return the guild skins filename only"""
        r: object = requests.get(url = f"{self.end}/skin/filenames/{_id}")
        return ([x["filename"] for x in r.json()])

    def selectLastUploaded(self, count: int = 5) -> list:
        """Return the <count> last uploads"""
        r: object = requests.get(url = f"{self.end}/skin/last/{count}")
        return (r.json())
    
    def insertSkin(self, **kwargs) -> None:
        """Upload a skin"""
        requests.post(url = f"{self.end}/skin/upload", params = kwargs)
    
    def deleteSkin(self, **kwargs) -> None:
        """Delete a skin"""
        requests.delete(url = f"{self.end}/skin/delete", params = kwargs)