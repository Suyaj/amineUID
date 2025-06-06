import os
from pathlib import Path

from jmcomic import JmModuleConfig

from gsuid_core.plugins.amineUID.amineUID.bot import http_bot
from gsuid_core.plugins.amineUID.amineUID.pixiv.jm import transmission_one
from gsuid_core.plugins.amineUID.amineUID.pixiv.jm import ZipEnhancedPlugin, Img2pdfEnhancedPlugin, get_album, \
    default_jm_logging, search as jm_search, transmission
from gsuid_core.plugins.amineUID.amineUID.utils.contants import JM_PATH
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

JmModuleConfig.register_plugin(ZipEnhancedPlugin)
JmModuleConfig.register_plugin(Img2pdfEnhancedPlugin)
JmModuleConfig.EXECUTOR_LOG = default_jm_logging
os.makedirs(JM_PATH, exist_ok=True)
BASE_HTTP = "http://121.40.208.220:8083/"

sv_wiki = SV("pixiv")


@sv_wiki.on_prefix('下载')
async def download(bot: Bot, ev: Event):
    await bot.send("开始获取数据")
    texts = ev.text.strip().split(" ")
    album_id = texts[0]
    try:
        album = get_album(album_id)
        transmission_one(Path.joinpath(JM_PATH, album.name))
        await bot.send(["成功", f"访问地址：{BASE_HTTP}"])
    except Exception as e:
        logger.error(e)
        await bot.send("数据出现问题")


@sv_wiki.on_prefix("传输")
async def trans(bot: Bot, ev: Event):
    texts = ev.text.strip().split(" ")
    search_content = texts[0]
    user_id = ev.user_id
    search_path = Path.joinpath(JM_PATH, search_content)
    transmission(user_id, search_path)
    http_bot.send_private_msg(user_id, ["传输成功", f"访问地址：{BASE_HTTP}"])


@sv_wiki.on_prefix("搜索")
async def search(bot: Bot, ev: Event):
    user_id = ev.user_id
    texts = ev.text.strip().split(" ")
    search_content = texts[0]
    page = 1
    if len(texts) == 2:
        page = texts[1]
    contents = jm_search(search_content, page=int(page))
    msg_list = []
    for i in range(0, len(contents.content)):
        album = contents.getindex(i)
        album_id, album_name = album
        name = album_name['name']
        msg_list.append(f'{i}:[{album_id}]: {name}')
    await bot.send(msg_list)
    resp = await bot.receive_resp(
        '请选择获取的编号',
    )
    if resp is not None:
        index = resp.text
        if index == 'all':
            search_path = Path.joinpath(JM_PATH, search_content)
            os.makedirs(search_path, exist_ok=True)
            for i in range(0, len(contents.content)):
                album = contents.getindex(i)
                album_id = album[0]
                get_album(album_id, str(search_path))
            transmission(user_id, search_path)
            http_bot.send_private_msg(user_id, ["传输成功", f"访问地址：{BASE_HTTP}"])
        else:
            album = contents.getindex(int(index))
            album_id, album_name = album
            album = get_album(album_id)
            transmission_one(Path.joinpath(JM_PATH, album.name))
            http_bot.send_private_msg(user_id, ["传输成功", f"访问地址：{BASE_HTTP}"])
