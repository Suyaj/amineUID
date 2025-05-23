""" 常量 """

from pathlib import Path

from gsuid_core.data_store import get_res_path

# base
MAIN_PATH = Path.joinpath(get_res_path(), "amineUID")
IMAGES_PATH = Path.joinpath(MAIN_PATH, "images")
FUTURE_PATH = Path.joinpath(MAIN_PATH, "futures")
JM_PATH = Path.joinpath(MAIN_PATH, "jm")
BOT_PATH = Path.joinpath(MAIN_PATH, "bot.yml")

# cos
COS_BASE = "https://a2cy.com"
COSPLAY_URL = "https://a2cy.com/acg/cos"

# wiki
WIKI_URL = "https://homdgcat.wiki"
WIKI_GS_CHANGE_URL = "https://homdgcat.wiki/gi/change"
WIKI_SR_CHANGE_URL = "https://homdgcat.wiki/sr/change"
