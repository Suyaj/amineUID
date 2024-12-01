""" init """
import os

from gsuid_core.plugins.amineUID.amineUID.utils.contants import MAIN_PATH, IMAGES_PATH

os.makedirs(MAIN_PATH, exist_ok=True)
os.makedirs(IMAGES_PATH, exist_ok=True)
