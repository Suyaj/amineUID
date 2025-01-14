import os
from concurrent.futures.thread import ThreadPoolExecutor

from gsuid_core.aps import scheduler
from gsuid_core.gss import gss
from gsuid_core.logger import logger
from gsuid_core.config import core_config
import plugins.amineUID.amineUID.cos as cos


@scheduler.scheduled_job('cron', hour=0)
async def get_cos_job():
    logger.info("开始刷新cos列表")
    cos_list = cos.get_cos_list()
    with ThreadPoolExecutor(max_workers=os.cpu_count(), thread_name_prefix='COS_THREAD_') as executor:
        for item in cos_list.items():
            executor.submit(cos.async_get_cos, item[0], item[1])
        executor.shutdown()
    masters = core_config.get_config('masters')
    for bot_id in gss.active_bot:
        bot = gss.active_bot[bot_id]
        for master in masters:
            await bot.target_send("cos列表刷新成功", "direct", master, 'onebot', bot_id)
    logger.info("刷新cos列表完成")
