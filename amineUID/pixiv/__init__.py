import os

from jmcomic import JmModuleConfig

from gsuid_core.plugins.amineUID.amineUID.pixiv.jm import ZipEnhancedPlugin, Img2pdfEnhancedPlugin, get_album, \
    default_jm_logging, search as jm_search
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

@sv_wiki.on_prefix("搜索")
async def search(bot: Bot, ev: Event):
    texts = ev.text.strip().split(" ")
    search_content = texts[0]
    page = 1
    if len(texts) == 2:
        page = texts[1]
    contents = await jm_search(search_content, page=int(page))
    msg_list = []
    for index in range(1, contents.page_size):
        album = contents.getindex(index)
        album_id, album_name = album
        msg_list.append(f'{index}:[{album_id}]: {album_name}')
    await bot.send(msg_list)
    resp = await bot.receive_resp(
        '请选择获取的编号',
    )
    if resp is not None:
        index = resp.text
        album = contents.getindex(index)
        album_id, album_name = album
        album = get_album(album_id)
        await bot.send(["获取成功", f"访问地址：{BASE_HTTP}{album.name}"])
