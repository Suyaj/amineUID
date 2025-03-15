from webdriver_manager.chrome import ChromeDriverManager

from gsuid_core.plugins.amineUID.amineUID.wiki.gs_wiki import get_future
from gsuid_core.plugins.WutheringWavesUID.WutheringWavesUID.wutheringwaves_newsign import do_sign_task
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
    msg = await do_sign_task(bot, ev)
    await bot.send(msg)

@sv_wiki.on_prefix('未来信息')
async def get_future_func(bot: Bot, ev: Event):
    texts = ev.text.strip().split(" ")
    _type = 'gs' if texts[0] == '原神' else 'sr'
    future = get_future(_type)
    image = await convert_img(future, True)
    await bot.send(image)

