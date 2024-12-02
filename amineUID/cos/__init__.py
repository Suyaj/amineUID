""" cos命令 """
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor, wait
from pathlib import Path

from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event, Message
from gsuid_core.logger import logger

from .cos_core import get_cos_list, get_cos, get_images, async_get_cos
from ..utils import IMAGES_PATH

sv_am_get_cos_images = SV("cosPlay")


@sv_am_get_cos_images.on_prefix("获取图片")
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
    ev_text = ev.text.strip()
    cmds = convert_cmd(ev_text)
    msg = ""
    await bot.send('正在获取目录，请稍等')
    if "local" in cmds:
        data = os.listdir(IMAGES_PATH)
        for i, title in enumerate(data):
            msg += f'{i}: {title}\n'
    elif "down" in cmds:
        await bot.send("开始下载")
        data = get_cos_list(cmds["down"])
        for title in data.keys():
            msg += f'{title}\n'
        await bot.send(msg)
        with ThreadPoolExecutor(max_workers=os.cpu_count(), thread_name_prefix='COS_THREAD_') as executor:
            for item in data.items():
                executor.submit(async_get_cos, item[0], item[1])
            executor.shutdown()
        return bot.send("下载完成")
    else:
        if "index" in cmds:
            data = get_cos_list(cmds["index"])
        else:
            data = get_cos_list()
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
            if "local" in cmds:
                for i, title in enumerate(data):
                    if i == int(text):
                        cos = title
                        break
                img_dir = os.path.join(IMAGES_PATH, cos)
                images = await get_images(Path(img_dir))
            else:
                for i, item in enumerate(data.items()):
                    if i == int(text):
                        cos = item
                        break
                logger.info(f"目录地址：{cos[1]}")
                images = await get_cos(cos[0], cos[1])
            await bot.send(images)
        except Exception as e:
            logger.error(e)
            await bot.send('输入错误')


def convert_cmd(text: str) -> dict[str, str]:
    cmd = {}
    texts = text.split(" ")
    i = 0
    while i < len(texts):
        if i == len(texts) - 1:
            cmd[texts[i]] = ""
            break
        cmd[texts[i]] = texts[i + 1]
        i += 2
    return cmd


@sv_am_get_cos_images.on_fullmatch("test")
async def get_cos_images(bot: Bot, ev: Event):
    await bot.send("test")
