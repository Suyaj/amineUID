""" 常量 """

from pathlib import Path

from gsuid_core.data_store import get_res_path

# base
MAIN_PATH = Path.joinpath(get_res_path(), "amineUID")
IMAGES_PATH = Path.joinpath(MAIN_PATH, "images")

# cos
COS_BASE = "https://a2cy.com"
COSPLAY_URL = "https://a2cy.com/acg/cos"

# wiki
WIKI_URL = "https://homdgcat.wiki/gi"
WIKI_CHANGE_URL = "https://homdgcat.wiki/gi/change"
