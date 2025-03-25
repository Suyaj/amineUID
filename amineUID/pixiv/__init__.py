import os

from jmcomic import JmModuleConfig

from amineUID.pixiv.jm import ZipEnhancedPlugin, Img2pdfEnhancedPlugin, get_album_zip, file_to_base64
from amineUID.utils.contants import JM_PATH
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.segment import MessageSegment
from gsuid_core.sv import SV

JmModuleConfig.register_plugin(ZipEnhancedPlugin)
JmModuleConfig.register_plugin(Img2pdfEnhancedPlugin)
os.makedirs(JM_PATH, exist_ok=True)

sv_wiki = SV("pixiv")


@sv_wiki.on_prefix('下载')
async def download(bot: Bot, ev: Event):
    await bot.send("开始获取数据")
    texts = ev.text.strip().split(" ")
    album_id = texts[0]
    try:
        get_album_zip(album_id)
        msg = MessageSegment.file("https://docs.sayu-bot.com/bg.png", f"{album_id}.zip")
        await bot.send(msg)
    except Exception as e:
        logger.error(e)
        await bot.send("数据出现问题")
