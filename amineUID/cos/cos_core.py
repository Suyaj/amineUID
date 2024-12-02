""" cos core """

import os
import asyncio
import urllib.request
from time import sleep
from pathlib import Path
from typing import List

from PIL import Image
from bs4 import BeautifulSoup

from gsuid_core.logger import logger
from gsuid_core.utils.download_resource.download_file import download
from gsuid_core.utils.image.convert import convert_img

from ..utils.contants import COS_BASE, COSPLAY_URL, IMAGES_PATH


def get_cos_list(index: str = None):
    """
    获取cos目录

    Args:
        index (str, optional): _description_. Defaults to None.
    """
    data = {}
    start_url = (
        COSPLAY_URL
        if index is None or index == "1"
        else COSPLAY_URL + "/" + f"index_{index}.html"
    )
    urlopen = urllib.request.urlopen(start_url)
    html = urlopen.read()
    html_soup = BeautifulSoup(html, "html.parser")
    cos_list = html_soup.find("ul", {"class": "cy2-coslist clr"})
    cos_li_list = cos_list.find_all("li")
    cos_box = html_soup.find(
        "ul", {"class": "cy2-cosBox clr animated fadeInUp"}
    )
    cos_box_li_list = cos_box.find_all("li")
    for cos in cos_li_list:
        cos_box_li_list.append(cos)
    for cos in cos_box_li_list:
        div_img = cos.find_next("div", {"class": "showImg"})
        a = div_img.find_next("a")
        href = a.get("href")
        img = a.find("img")
        title = img.get("alt")
        data[title] = href
    return data

async def get_cos(title: str, href: str):
    """
    下载cos目录

    Args:
        title:
        href:
    """
    url = COS_BASE + href
    images = os.listdir(IMAGES_PATH)
    img_dir = os.path.join(IMAGES_PATH, title)
    if title in images:
        return get_images(Path(img_dir))
    os.makedirs(img_dir, exist_ok=True)
    await download_one_cos(url, img_dir, title)
    return await get_images(Path(img_dir))


async def get_images(path: Path) -> list[bytes]:
    """
    获取图片

    Args:
        path:

    Returns:

    """
    images = os.listdir(path.as_posix())
    data = []
    for image in images:
        img_path = Path.joinpath(path, image)
        img = Image.open(img_path)
        data.append(await convert_img(img, True))
    return data



async def download_one_cos(url: str, img_dir: str, title: str):
    """
    下载

    Args:
        url (str): _description_
        img_dir (str): _description_
        title (str): _description_
    """
    logger.info(f'URL:{url} 开始下载')
    cos_html = urllib.request.urlopen(url).read()
    cos_html_soup = BeautifulSoup(cos_html, "html.parser")
    cos_find = cos_html_soup.find("div", {"class": "imgBox"})
    if cos_find is None:
        cos_find = cos_html_soup.find("div", {"class": "w maxImg tc"})
    cos_p_list = cos_find.find_all("p")  # type: ignore
    for cos in cos_p_list:
        cos_img = cos.find("img")
        img_src = cos_img.get("src")
        if img_src is None:
            img_src = cos_img.get("data-loadsrc")
        print(img_src)
        img_urls = os.path.split(img_src)
        file_name = img_urls[len(img_urls) - 1]
        file_url = COS_BASE + img_src
        await download_img(file_url, Path(img_dir), file_name)
    logger.info(f'{title} 下载完成')


async def download_img(url: str, path: Path, name: str, error_count: int = 0):
    """
    下载图片

    Args:
        url (str): _description_
        path (Path): _description_
        name (str): _description_
        error_count (int, optional): _description_. Defaults to 0.
    """
    code = await download(url, path, name)
    if code is None or code != 200:
        if error_count > 9:
            sleep(2)
            return
        await download_img(url, path, name, error_count + 1)


if __name__ == "__main__":
    get_cos_list()
