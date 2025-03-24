import asyncio
import threading
import time
import platform
from pathlib import Path
from typing import List

from playwright.async_api import async_playwright, ElementHandle, Browser

from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

from tomlkit import value

from gsuid_core.plugins.amineUID.amineUID.model.wiki import WikiBind
from gsuid_core.logger import logger
from gsuid_core.plugins.amineUID.amineUID.utils.contants import WIKI_URL, FUTURE_PATH, WIKI_GS_CHANGE_URL, \
    WIKI_SR_CHANGE_URL
from gsuid_core.bot import Bot

time_out = 60
host = WIKI_URL
executable_path = '/root/.cache/ms-playwright/chromium_headless_shell-1161/chrome-linux/headless_shell'
gs_future = Path.joinpath(FUTURE_PATH, 'gs_future')
versions = Path.joinpath(FUTURE_PATH, 'versions')
sr_future = Path.joinpath(FUTURE_PATH, 'sr_future')
data_future = Path.joinpath(FUTURE_PATH, 'data')

lock = threading.Lock()


async def refresh_data(bot: Bot = None):
    if lock.acquire(timeout=5):
        try:
            await send(bot, "已经启动刷新程序，请等待处理！！！")
            playwright = await async_playwright().start()
            await send(bot, "启动playwright")
            os_name = platform.system()
            if os_name.lower() == 'windows':
                launch = await playwright.chromium.launch(headless=True)
            elif os_name.lower() == 'linux':
                launch = await playwright.chromium.launch(executable_path=executable_path, headless=True)
            else:
                logger.error("当前系统不支持")
                return await send(bot, "当前系统不支持")
            await send(bot, "启动launch")
        except Exception as e:
            logger.exception(e)
            lock.release()
            return
        try:
            page_source = await get_future(launch)
            logger.info("未来信息目录加载完成")
            await send(bot, "未来信息目录加载完成")
            html = BeautifulSoup(page_source, 'html.parser')
            target_list = get_text(html)
            text_list = target_list['gs']
            await get_gs_node_images(launch, html, text_list)
            logger.info("原神未来信息加载完成")
            await send(bot, "原神未来信息加载完成，包含：" + ",".join(text_list))
            text_list = target_list['sr']
            await get_sr_node_images(launch, html, text_list)
            logger.info("崩铁未来信息加载完成")
            await send(bot, "崩铁未来信息加载完成，包含：" + ",".join(text_list))
            await get_versions(launch, bot)
        except Exception as e:
            logger.exception(e)
        finally:
            await launch.close()
            await playwright.stop()
            lock.release()
    else:
        await bot.send("程序已经启动了")


async def get_gs_node_images(launch, html, text_list):
    for text in text_list:
        target = get_url_target(html, text)
        url_split = target.split('/')
        avatar_target = get_avatar_target(html, text)
        avatar_split = avatar_target.split("/")
        await insert_wiki_bind(url_split[len(url_split) - 1], text, avatar_split[len(avatar_split) - 1], 'gs')
        logger.info("处理{}数据", text)
        await gs_screen_shot(launch, target, text)
        logger.info("{}数据处理完成", text)


async def insert_wiki_bind(_value, text, avatar, _type):
    wiki_bind = await WikiBind.base_select_data(value=_value)
    if wiki_bind is None:
        await WikiBind.full_insert_data(name=text, value=_value, type=_type, avatar=avatar)


async def get_sr_node_images(launch, html, text_list):
    for text in text_list:
        target = get_url_target(html, text)
        url_split = target.split('/')
        avatar_target = get_avatar_target(html, text)
        avatar_split = avatar_target.split("/")
        await insert_wiki_bind(url_split[len(url_split) - 1], text, avatar_split[len(avatar_split) - 1], 'sr')
        logger.info("处理{}数据", text)
        await sr_screen_shot(launch, target, text)
        logger.info("{}数据处理完成", text)


async def sr_screen_shot(launch, url: str, name: str):
    request_url = host + url
    page = await launch.new_page()
    await page.goto(request_url)
    await page.wait_for_load_state("networkidle")
    data = await page.query_selector(".t_skill")
    if data is None:
        length = await page.evaluate("document.getElementsByClassName('mon_body')[0].childNodes.length")
        selector_targets = []
        for i in range(0, length):
            if i == 1:
                continue
            selector_targets.append(f"#content_2 > div > div:nth-child({i + 1})")
    else:
        selector_targets = ["#content_2 > div > div:nth-child(1)",
                            "#content_2 > div > div.a_section.t_skill",
                            "#content_2 > div > div:nth-child(3)"]
    await page.evaluate("document.body.style.zoom='0.1'")
    await wait(page, "mon_body")
    await page.evaluate("document.body.style.zoom='1'")
    await set_max_view(page, "#content_2")
    if data_future.exists() is False:
        data_future.mkdir()
    await to_images(page, selector_targets, str(Path.joinpath(data_future, name)).rstrip("\\"))
    await page.close()


async def gs_screen_shot(launch, url: str, name: str):
    request_url = host + url
    page = await launch.new_page()
    await page.goto(request_url)
    await page.wait_for_load_state("networkidle")
    data = await page.query_selector(".a_data")
    if data is not None:
        wait_class_name = "a_data"
        selector_targets = ["body > div.scroller > container > divv > section.a_data > div:nth-child(1)",
                            "body > div.scroller > container > divv > section.a_data > div:nth-child(3)",
                            "body > div.scroller > container > divv > section.a_data > div:nth-child(4)",
                            "body > div.scroller > container > divv > section.a_data > div:nth-child(5)",
                            "body > div.scroller > container > divv > section.a_data > div:nth-child(6)",
                            "body > div.scroller > container > divv > section.a_data > div:nth-child(7)",
                            "body > div.scroller > container > divv > section.a_data > div:nth-child(8)",
                            "body > div.scroller > container > divv > section.a_data > div:nth-child(9)",
                            "body > div.scroller > container > divv > section.a_data > div:nth-child(10)",
                            "body > div.scroller > container > divv > section.a_data > div:nth-child(11)",
                            "body > div.scroller > container > divv > section.a_data > div:nth-child(12)",
                            "body > div.scroller > container > divv > section.a_data > div:nth-child(13)",
                            "body > div.scroller > container > divv > section.a_data > div:nth-child(14)",
                            "body > div.scroller > container > divv > section.a_data > div:nth-child(15)"]
    else:
        data = await page.query_selector(".r_data")
        if data is not None:
            wait_class_name = "r_data"
            selector_targets = ["body > div.scroller > container > divv > section.r_data > div:nth-child(1)"]
        else:
            wait_class_name = "weapon_section"
            selector_targets = ["body > div.scroller > container > divv > section.weapon_section > div:nth-child(1)",
                                "body > div.scroller > container > divv > section.weapon_section > div.a_section.weapon_skill",
                                "body > div.scroller > container > divv > section.weapon_section > div:nth-child(2)"]
    await page.evaluate("document.body.style.zoom='0.1'")
    await wait(page, wait_class_name)
    await page.evaluate("document.body.style.zoom='1'")
    time.sleep(0.5)
    await set_max_view(page, "body > div.scroller > container")
    if data_future.exists() is False:
        data_future.mkdir()
    await to_images(page, selector_targets, str(Path.joinpath(data_future, name)).rstrip("\\"))
    await page.close()


async def get_version(launch, url: str):
    page = await launch.new_page()
    await page.goto(url)
    await page.wait_for_load_state("networkidle")
    select = await page.query_selector("select")
    options = await select.query_selector_all("option")
    versionList = []
    for option in options:
        value = await option.get_attribute("value")
        _version = f'V{value[0]}'
        versionList.append(_version)
        await select.select_option(value=value)
        await page.evaluate("document.body.style.zoom='0.1'")
        await wait(page, "cl_data")
        await page.evaluate("document.body.style.zoom='1'")
        length = await page.evaluate("document.getElementsByClassName('cl_data')[0].childNodes.length")
        cl_data = await page.query_selector(".cl_data")
        sections = await cl_data.query_selector_all(".a_section")
        for i in range(1, int(length)):
            await sections[i].click()
        await set_max_view(page, ".content")
        image_map = await get_images(sections)
        await save_images(image_map, _version)
        logger.info(f"{_version}版本数据获取成功")
    return ",".join(versionList)


async def save_images(image_map, version: str):
    versions.mkdir(parents=True, exist_ok=True)
    for (avatar, images) in image_map.items():
        bind = await WikiBind.base_select_data(avatar=avatar)
        avatar_path = Path.joinpath(versions, bind.name)
        avatar_path.mkdir(parents=True, exist_ok=True)
        await splicing(images, str(Path.joinpath(avatar_path, version)).rstrip("\\"))


async def get_images(sections):
    images = {}
    for (index, section) in enumerate(sections):
        if index == 0:
            continue
        image = await to_image(section)
        head = await section.query_selector(".a_section_head")
        img = await head.query_selector("img")
        src = await img.get_attribute("src")
        split = src.split("/")
        avatar = split[len(split) - 1]
        if images.get(avatar) is None:
            images[avatar] = []
        images[avatar].append(image)
    return images


async def get_versions(launch: Browser, bot: Bot = None):
    msg = await get_version(launch, WIKI_GS_CHANGE_URL)
    logger.info(f"原神改动获取成功,{msg}")
    await send(bot, f"原神改动获取成功,{msg}")
    msg = await get_version(launch, WIKI_SR_CHANGE_URL)
    logger.info(f"崩铁改动获取成功,{msg}")
    await send(bot, f"崩铁改动获取成功,{msg}")


async def set_max_view(page, target):
    container = await page.query_selector(target)
    box = await container.bounding_box()
    width = box["width"]
    height = box["height"]
    await page.set_viewport_size({"width": int(width), "height": int(height)})


async def to_images(page, selector_targets: List[str], path: str):
    images = []
    for target in selector_targets:
        node = await get_node(page, target)
        images.append(await to_image(node))
    await splicing(images, path)


async def get_node(page, target):
    node = await page.query_selector(f'css={target}')
    while node is None:
        time.sleep(0.5)
        node = await page.query_selector(f'css={target}')
    return node


async def get_future(launch):
    request_url = host
    page = await launch.new_page()
    await page.goto(request_url)
    await page.wait_for_function("()=>{return document.getElementsByClassName('n1').length > 0;}")
    await wait(page, "n1")
    node = await page.query_selector("body > container > div > section.n1")
    await to_future_image(node, gs_future)
    await page.click(selector="body > container > div > section.home_select > schedule:nth-child(2)")
    await wait(page, "n2")
    node = await page.query_selector("body > container > div > section.n2")
    await to_future_image(node, sr_future)
    content = await page.content()
    await page.close()
    return content


async def to_future_image(node, path: str):
    elements = await node.query_selector_all("a")
    size = len(elements)
    box = await elements[0].bounding_box()
    _width = box['width']
    img_width = (_width + 8) * size
    img = await to_image(node)
    height = img.size[1]
    im = img.crop((0, 0, img_width, height))
    if FUTURE_PATH.exists() is False:
        FUTURE_PATH.mkdir()
    im.save(f'{path}.png')


def get_text(html: BeautifulSoup):
    gs = html.find("section", {"class": "n1"})
    gs_text_list = get_text_list(gs)
    sr = html.find("section", {"class": "n2"})
    sr_text_list = get_text_list(sr)
    return {"gs": gs_text_list, "sr": sr_text_list}


def get_text_list(html):
    a_list = html.find_all("a", {"target": "_blank"})
    text_list = []
    for a in a_list:
        p = a.find_next("p", {"class": "new_text"})
        text_list.append(p.get_text())
    return text_list


def get_url_target(html, target):
    a_list = html.find_all("a", {"target": "_blank"})
    for a in a_list:
        p = a.find_next("p", {"class": "new_text"})
        if p.get_text() == target:
            return a['href']


def get_avatar_target(html, target):
    a_list = html.find_all("a", {"target": "_blank"})
    for a in a_list:
        p = a.find_next("p", {"class": "new_text"})
        if p.get_text() == target:
            images = a.find_all("img")
            return images[0]['src']


def get_wait_exec(class_name: str):
    return '''
    () => {
        elements = document.getElementsByClassName("''' + class_name + '''")
        if (elements.length == 0) {
            return false;
        }
        let images = elements[0].getElementsByTagName('img');
        for (let image of images) {
            if(!image.complete){
              return false;
            }
        }
        return true;
    }
    '''


async def wait(page, class_name: str):
    time.sleep(0.5)
    status = await page.evaluate(get_wait_exec(class_name))
    while status is False:
        time.sleep(0.5)
        status = await page.evaluate(get_wait_exec(class_name))


async def send(bot: Bot, msg: str):
    if bot is not None:
        await bot.send(msg)


async def splicing(images: List[Image], path: str):
    if len(images) == 0:
        return
    _width = images[0].width
    _height = 0
    for image in images:
        _height += image.height
    new = Image.new('RGB', (_width, _height))
    _height = 0
    for image in images:
        new.paste(image, (0, _height))
        _height += image.height
    new.save(f'{path}.png')


async def to_image(node: ElementHandle):
    binary_data = await node.screenshot(timeout=60000)
    image_data = BytesIO(binary_data)
    img = Image.open(image_data)
    return img


if __name__ == '__main__':
    asyncio.run(refresh_data())
    # asyncio.run(screen_shot('/gi/char/Varesa',  "test"))
