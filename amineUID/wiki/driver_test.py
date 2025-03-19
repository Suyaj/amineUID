import asyncio
from io import BytesIO

from PIL import Image
from playwright.async_api import async_playwright

async def test():
    playwright = await async_playwright().start()
    launch = await playwright.chromium.launch(headless=True)
    page = await launch.new_page()
    await page.goto("https://homdgcat.wiki")
    await page.wait_for_function("()=>{return document.getElementsByClassName('n1').length > 0;}")
    await page.wait_for_function('''
    () => {
        let images = document.getElementsByClassName("n1")[0].getElementsByTagName('img');
        for (let image of images) {
            if(!image.complete){
              return false;
            }
        }
        return true;
    }
    ''')
    node = await page.query_selector("body > container > div > section.n1")
    binary_data = await node.screenshot()
    elements = await node.query_selector_all("a")
    size = len(elements)
    box = await elements[0].bounding_box()
    _width = box['width']
    img_width = (_width + 8) * size
    image_data = BytesIO(binary_data)
    img = Image.open(image_data)
    height = img.size[1]
    im = img.crop((0, 0, img_width, height))
    im.save('test.png')
    await page.close()
    await launch.close()
    await playwright.stop()

if __name__ == '__main__':
    asyncio.run(test())
