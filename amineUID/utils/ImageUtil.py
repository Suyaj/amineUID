from typing import Tuple, Union, Optional

from PIL import Image, ImageFont

from gsuid_core.utils.image import image_tools


def draw_text_by_line(
    img: Image.Image,
    pos: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: Union[Tuple[int, int, int, int], str],
    max_length: float,
    center=False,
    line_space: Optional[float] = None,
) -> float:
    return image_tools.draw_text_by_line(img, pos, text, font, fill, max_length, center, line_space)


async def draw_pic_with_ring(pic: Image.Image,
                             size: int,
                             bg_color: Optional[Tuple[int, int, int]] = None,
                             is_ring: bool = True):
    return await image_tools.draw_pic_with_ring(pic, size, bg_color, is_ring)


def easy_paste(
    im: Image.Image, im_paste: Image.Image, pos=(0, 0), direction="lt"
):
    return image_tools.easy_paste(im, im_paste, pos, direction)


def easy_alpha_composite(
    im: Image.Image, im_paste: Image.Image, pos=(0, 0), direction="lt"
) -> Image.Image:
    return image_tools.easy_alpha_composite(im, im_paste, pos, direction)

async def get_pic(url, size: Optional[Tuple[int, int]] = None) -> Image.Image:
    return await image_tools.get_pic(url, size)
