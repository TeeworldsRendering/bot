from typing import *
from PIL import Image, ImageOps


Color = Tuple[int, int, int]

def op_tuple(func: callable, t1: tuple, t2: tuple) -> tuple:
    return (tuple(map(func, t1, t2)))

# The result is a weighted average of the bottom pixel and the top pixel.
# The weight of the pixels is determined by a.
def _blend(src: Color, dest: Color, a: int = 255) -> Color:
    return ((a * src) // 255 + ((1 - a) * dest) // 255)

# It makes the colors more vivid by adding the color of the source to that of the destination.
def _add(src: Color, dest: Color, a: int = 255) -> Color:
    return ((a * src) // 255 + dest)

# It gives a rather dark image. 
# This mode can be useful to simulate the light of a projector, for example.
def _mod(src: Color, dest: Color) -> Color:
    return ((src * dest) // 255)

# Change each pixel of the src image depending of the mod
def applyColor(image: Image, color: Color, func: callable) -> Image:
    arr: List[Color] = []
    ret: Image = Image.new(image.mode, image.size)

    for pixel in image.getdata():
        arr.append(op_tuple(func, pixel, color))
    
    ret.putdata(arr)
    return (ret)