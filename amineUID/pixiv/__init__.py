import os

from jmcomic import JmModuleConfig

from gsuid_core.plugins.amineUID.amineUID.pixiv.jm import ZipEnhancedPlugin, Img2pdfEnhancedPlugin, get_album, \
    default_jm_logging
from gsuid_core.plugins.amineUID.amineUID.utils.contants import JM_PATH
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

JmModuleConfig.register_plugin(ZipEnhancedPlugin)
JmModuleConfig.register_plugin(Img2pdfEnhancedPlugin)
JmModuleConfig.EXECUTOR_LOG = default_jm_logging
os.makedirs(JM_PATH, exist_ok=True)
BASE_HTTP = "http://121.40.208.220:5244/"

sv_wiki = SV("pixiv")


@sv_wiki.on_prefix('下载')
async def download(bot: Bot, ev: Event):
    await bot.send("开始获取数据")
    texts = ev.text.strip().split(" ")
    album_id = texts[0]
    try:
        album = get_album(album_id)
        await bot.send(["成功", f"访问地址：{BASE_HTTP}{album.name}"])
    except Exception as e:
        logger.error(e)
        await bot.send("数据出现问题")
