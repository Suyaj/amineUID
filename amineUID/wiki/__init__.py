import asyncio
import os
import random
import threading
from pathlib import Path
from typing import Optional

from PIL import Image

from gsuid_core.plugins.RoverSign.RoverSign.roversign_sign.main import get_bbs_link_config
from gsuid_core.plugins.RoverSign.RoverSign.roversign_sign.new_sign import get_waves_signin_config, \
    get_bbs_signin_config, get_sign_status, action_waves_sign_in, action_bbs_sign_in
from gsuid_core.plugins.RoverSign.RoverSign.utils.api.api import WAVES_GAME_ID
from gsuid_core.plugins.RoverSign.RoverSign.utils.database.models import (
    RoverSign,
    WavesBind,
    WavesUser,
)
from gsuid_core.plugins.RoverSign.RoverSign.utils.database.states import SignStatus
from gsuid_core.plugins.RoverSign.RoverSign.utils.errors import WAVES_CODE_101_MSG
from gsuid_core.plugins.RoverSign.RoverSign.utils.rover_api import rover_api
from gsuid_core.plugins.amineUID.amineUID.utils.contants import FUTURE_PATH
from gsuid_core.plugins.amineUID.amineUID.wiki.core import get_future, refresh_data
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
    logger.info(f'[全部签到] 用户: {ev.user_id} bot:{ev.bot_id}')
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
    return await ww_sign(bot, ev)


async def ww_sign(bot, ev):
    # ww签到
    bind_data = await WavesBind.select_data(ev.user_id, ev.bot_id)
    if not bind_data:
        return await bot.send(f"鸣潮{WAVES_CODE_101_MSG}")
    # 获取所有 UID
    waves_uid_list = []
    if bind_data.uid:
        waves_uid_list = [u for u in bind_data.uid.split("_") if u]
    if waves_uid_list:
        for waves_uid in waves_uid_list:
            await WavesUser.update_last_used_time(
                waves_uid,
                ev.user_id,
                ev.bot_id,
                game_id=WAVES_GAME_ID,
            )
    main_uid = waves_uid_list[0] if waves_uid_list else None
    # 先检查本地签到状态，判断是否所有签到都已完成
    waves_enabled = await get_waves_signin_config()
    bbs_enabled = await get_bbs_signin_config()
    bbs_link_config = get_bbs_link_config()
    all_completed = True
    # 检查鸣潮签到状态
    if waves_enabled and waves_uid_list:
        for waves_uid in waves_uid_list:
            rover_sign = await RoverSign.get_sign_data(waves_uid)
            if not rover_sign or not SignStatus.waves_game_sign_complete(rover_sign):
                all_completed = False
                break
    # 检查社区签到状态
    if all_completed and bbs_enabled and main_uid:
        rover_sign = await RoverSign.get_sign_data(main_uid)
        if not rover_sign or not SignStatus.bbs_sign_complete(rover_sign, bbs_link_config):
            all_completed = False
    # 如果所有签到都已完成，直接返回跳过消息，不请求任何 API
    if all_completed:
        msg_list = []
        sign_status = get_sign_status()
        if waves_enabled and waves_uid_list:
            for waves_uid in waves_uid_list:
                msg_list.append(f"[鸣潮] 特征码: {waves_uid}")
                msg_list.append(f"签到状态: {sign_status['skip']}")
                msg_list.append("-----------------------------")

        if bbs_enabled and main_uid:
            msg_list.append(f"社区签到状态: {sign_status['skip']}")

        return "\n".join(msg_list) if msg_list else WAVES_CODE_101_MSG
    # 有未完成的签到，开始获取 token 并执行签到
    msg_list = []
    expire_uid = set()  # 使用 set 自动去重
    main_token = None
    sign_status = get_sign_status()
    if main_uid:
        main_token = await rover_api.get_self_waves_ck(main_uid, ev.user_id, ev.bot_id)
        if not main_token:
            expire_uid.add(main_uid)
    # 鸣潮签到
    if waves_enabled and waves_uid_list:
        for waves_uid in waves_uid_list:
            token = main_token if waves_uid == main_uid else await rover_api.get_self_waves_ck(waves_uid,
                                                                                               ev.user_id,
                                                                                               ev.bot_id)
            if not token:
                expire_uid.add(waves_uid)
                continue

            waves_signed = False
            rover_sign: Optional[RoverSign] = await RoverSign.get_sign_data(waves_uid)
            if rover_sign and SignStatus.waves_game_sign_complete(rover_sign):
                waves_signed = "skip"
            else:
                waves_signed = await action_waves_sign_in(waves_uid, token)

            msg_list.append(f"[鸣潮] 特征码: {waves_uid}")
            msg_list.append(f"签到状态: {sign_status[waves_signed]}")
            msg_list.append("-----------------------------")

            await asyncio.sleep(random.randint(1, 2))
    # 社区签到（不依赖 UID，只要有 token 就可以）
    if bbs_enabled and main_token:
        bbs_signed = False
        if main_uid:
            rover_sign: Optional[RoverSign] = await RoverSign.get_sign_data(main_uid)
            if rover_sign and SignStatus.bbs_sign_complete(rover_sign, bbs_link_config):
                bbs_signed = "skip"
            else:
                bbs_signed = await action_bbs_sign_in(main_uid, main_token)

        msg_list.append(f"社区签到状态: {sign_status[bbs_signed]}")
    # 失效 UID 提示
    if expire_uid:
        msg_list.append("-----------------------------")
        for uid in expire_uid:
            msg_list.append(f"失效特征码: {uid}")
    return "\n".join(msg_list) if msg_list else WAVES_CODE_101_MSG


@sv_wiki.on_prefix('未来数据')
async def get_future_func(bot: Bot, ev: Event):
    texts = ev.text.strip().split(" ")
    node_name = texts[0]
    path = Path.joinpath(FUTURE_PATH, 'data', f'{node_name}.png')
    if os.path.exists(path) is False:
        return await bot.send("未来信息不存在，请刷新信息！！！")
    img = Image.open(path)
    logger.info("未来信息，查询成功")
    image = await convert_img(img, True)
    await bot.send(image)


@sv_wiki.on_prefix('未来版本')
async def get_future_func(bot: Bot, ev: Event):
    texts = ev.text.strip().split(" ")
    await bot.send("正在查询，请稍后！！！")
    _type = 'gs' if texts[0] == '原神' else 'sr'
    path = Path.joinpath(FUTURE_PATH, f'{_type}_future.png')
    img = Image.open(path)
    logger.info("未来信息，查询成功")
    image = await convert_img(img, True)
    await bot.send(image)


@sv_wiki.on_prefix('刷新未来信息')
async def get_refresh_data(bot: Bot, ev: Event):
    await bot.send("正在启动刷新程序，请稍后！！！")
    texts = ev.text.strip().split(" ")
    _type = 'gs' if texts[0] == '原神' else 'sr'
    threading.Thread(target=lambda: asyncio.run(refresh_data(_type, bot)), daemon=True).start()


@sv_wiki.on_prefix("获取版本更新")
async def get_future_update(bot: Bot, ev: Event):
    texts = ev.text.strip().split(" ")
    _type = 'gs' if texts[0] == '原神' else 'sr'
    threading.Thread(target=lambda: asyncio.run(core.get_future_update(_type, bot)), daemon=True).start()
