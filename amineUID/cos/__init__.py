""" cos命令 """
import os

from PIL import Image

from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event, Message
from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img

from .cos_core import get_cos_list, get_cos
from ..utils.contants import IMAGES_PATH

sv_am_get_cos_images = SV("cosPlay")


@sv_am_get_cos_images.on_fullmatch("获取图片")
async def get_cos_images(bot: Bot, ev: Event):
    """
    获取目录

    Args:
        bot (Bot): _description_
        ev (Event): _description_

    Returns:
        _type_: _description_
    """
    logger.info("获取cos目录")
    await bot.send('正在获取目录，请稍等', )
    data = get_cos_list()
    msg = ""
    for i, title in enumerate(data.keys()):
        msg += f'{i}: {title}\n'
    await bot.send(msg)
    resp = await bot.receive_resp(
        '请选择获取的目录编号',
    )
    if resp is not None:
        text = resp.text
        # noinspection PyBroadException
        try:
            cos = None
            for i, item in enumerate(data.items()):
                if i == int(text):
                    cos = item
                    break
            logger.info(f"目录地址：{cos[1]}")
            await get_cos(cos[0], cos[1])
            await bot.send("完成")
        except Exception as e:
            logger.error(e)
            await bot.send('输入错误')


@sv_am_get_cos_images.on_fullmatch("test")
async def get_cos_images(bot: Bot, ev: Event):
    img_dir = os.path.join(IMAGES_PATH, "【COS正片】碧蓝航线 柴郡猫性感女仆cos cn香草喵露露")
    image_open = Image.open(
        os.path.join(img_dir, "0c932ae2f40e687a7ae5fa5ab119609a.jpg"))
    img = await convert_img(image_open)
    msgs = [img, img]
    await bot.send(msgs)
