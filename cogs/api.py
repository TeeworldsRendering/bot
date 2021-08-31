import requests, json

from utils.utilities import read_json

ENV: json = read_json("json/env.json")

end: str = f"http://{ENV['host']}:{ENV['port']}"

def selectAll() -> list:
    """Return the entire skin table"""
    r: object = requests.get(url = f"{end}/skin/all")
    return (r.json())

def selectByGuildId(_id: int) -> list:
    """Return the guild skins"""
    r: object = requests.get(url = f"{end}/skin/guild/{_id}")
    return (r.json())

def selectFilenamesByGuildId(_id: int) -> list:
    """Return the guild skins filename only"""
    r: object = requests.get(url = f"{end}/skin/filenames/{_id}")
    return ([x["filename"] for x in r.json()])

def selectLastUploaded(count: int = 5) -> list:
    """Return the <count> last uploads"""
    r: object = requests.get(url = f"{end}/skin/last/{count}")
    return (r.json())

def insertSkin(**kwargs) -> None:
    """Upload a skin"""
    requests.post(url = f"{end}/skin/upload", params = kwargs)

def deleteSkin(**kwargs) -> None:
    """Delete a skin"""
    requests.delete(url = f"{end}/skin/delete", params = kwargs)