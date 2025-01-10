import os
from concurrent.futures.thread import ThreadPoolExecutor

from gsuid_core.aps import scheduler
from gsuid_core.gss import gss
import plugins.amineUID.amineUID.cos as cos


@scheduler.scheduled_job('cron', minute='*/720')
async def get_cos_job():
    cos_list = cos.get_cos_list()
    with ThreadPoolExecutor(max_workers=os.cpu_count(), thread_name_prefix='COS_THREAD_') as executor:
        for item in cos_list.items():
            executor.submit(cos.async_get_cos, item[0], item[1])
        executor.shutdown()
    for bot_id in gss.active_bot:
        bot = gss.active_bot[bot_id]
        await bot.target_send("cos列表刷新成功", "direct", "2739618360", bot_id)
    pass
