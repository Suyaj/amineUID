from gsuid_core.plugins.ZZZeroUID.ZZZeroUID.utils.hint import BIND_UID_HINT
from gsuid_core.plugins.amineUID.amineUID.bot import http_bot
from gsuid_core.aps import scheduler
from gsuid_core.logger import logger
from gsuid_core.config import core_config
from gsuid_core.utils.database.models import GsBind


@scheduler.scheduled_job('cron', minute='*/5')
async def sign_in():
    logger.info("开始签到")
    masters = core_config.get_config('masters')
    for master in masters:
        msg_list = []
        uid = await GsBind.get_uid_by_game(master, "3490728073")
        if uid is None:
            msg_list.append(f"[{master}]你还没有绑定UID哦, 请使用原神绑定uid 完成绑定！")
        else:
            # gs签到
            msg = await sign_in(uid, 'gs')
            msg_list.append(msg)
        # sr签到
        uid = await GsBind.get_uid_by_game(master, "3490728073", 'sr')
        if uid is None:
            msg_list.append(f"[{master}]你还没有绑定UID哦, 请使用崩铁绑定uid 完成绑定！")
        else:
            msg = await sign_in(uid, 'sr')
            msg_list.append(msg)
        # zzz签到
        uid = await GsBind.get_uid_by_game(master, "3490728073", 'zzz')
        if uid is None:
            msg_list.append(f"[{master}]{BIND_UID_HINT}")
        else:
            msg = await sign_in(uid, 'zzz')
            msg_list.append(msg)
        http_bot.send_private_msg(master, msg_list)
    logger.info("签到结束")
