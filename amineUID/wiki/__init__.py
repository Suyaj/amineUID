import asyncio
import threading

from gsuid_core.plugins.amineUID.amineUID.wiki.gs_wiki import get_future, refresh_data
from gsuid_core.plugins.WutheringWavesUID.WutheringWavesUID.wutheringwaves_newsign import get_sign_func
from gsuid_core.plugins.ZZZeroUID.ZZZeroUID.utils.hint import BIND_UID_HINT
from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.database.models import GsBind
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.sign.sign import sign_in

sv_wiki = SV("wiki")

@sv_wiki.on_fullmatch("全部签到")
async def get_all_sign_func(bot: Bot, ev: Event):
    logger.info(f'[全部签到] 用户: {ev.user_id}')
    uid = await GsBind.get_uid_by_game(ev.user_id, ev.bot_id)
    if uid is None:
        return await bot.send("你还没有绑定UID哦, 请使用 原神绑定uid 完成绑定！")
    # gs签到
    await bot.send(await sign_in(uid, 'gs'))
    # sr签到
    uid = await GsBind.get_uid_by_game(ev.user_id, ev.bot_id, 'sr')
    if uid is None:
        return await bot.send("你还没有绑定UID哦, 请使用 崩铁绑定uid 完成绑定！")
    await bot.send(await sign_in(uid, 'sr'))
    # zzz签到
    uid = await GsBind.get_uid_by_game(ev.user_id, ev.bot_id, 'zzz')
    if uid is None:
        return await bot.send(BIND_UID_HINT)
    await bot.send(await sign_in(uid, 'zzz'))
    # ww签到
    msg = await get_sign_func(bot, ev)
    await bot.send(msg)


@sv_wiki.on_prefix(('未来信息', '未来'))
async def get_future_func(bot: Bot, ev: Event):
    texts = ev.text.strip().split(" ")
    await bot.send("正在查询，请稍后！！！")
    _type = 'gs' if texts[0] == '原神' else 'sr'
    threading.Thread(target=lambda: asyncio.run(refresh_data()), daemon=True).start()
    # future = await get_future(_type)
    logger.info("未来信息，查询成功")
    # image = await convert_img(future, True)
    # await bot.send(image)

@sv_wiki.on_prefix('刷新未来信息')
async def get_refresh_data(bot: Bot, ev: Event):
    threading.Thread(target=lambda: asyncio.run(refresh_data(bot)), daemon=True).start()
    await bot.send("已经启动刷新程序，请稍后！！！")
