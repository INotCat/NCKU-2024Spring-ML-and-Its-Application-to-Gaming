from enum import auto
from os import path

from mlgame.utils.enum import StringEnum
# game
WIDTH = 950
WIDTH_OF_INFO = 250

HEIGHT = 600
BG_COLOR = "#2B2B49"
PG_COLOR = "#B3E5FC"

# ball -> squid
# BALL_COLOR = "#FFEB3B"
SQUID_W = 30
SQUID_H = 45
LEVEL_THRESHOLDS = [10, 30, 60, 100, 150,200]
LEVEL_PROPERTIES = {
    1: {'size_ratio': 1.0, 'vel': 25},
    2: {'size_ratio': 1.2, 'vel': 21},
    3: {'size_ratio': 1.4, 'vel': 18},
    4: {'size_ratio': 1.6, 'vel': 16},
    5: {'size_ratio': 1.8, 'vel': 12},
    6: {'size_ratio': 2.0, 'vel': 9},
}

COLLISION_SCORE = {
    "WIN":10,
    "LOSE":-10,
    "DRAW":-5
}



ASSET_IMAGE_DIR = path.join(path.dirname(__file__), "../asset/img")
# food
class FoodTypeEnum(StringEnum):
    FOOD_1 = auto()
    FOOD_2 = auto()
    FOOD_3 = auto()
    GARBAGE_1 = auto()
    GARBAGE_2 = auto()
    GARBAGE_3 = auto()




FOOD_LV1_SIZE = 30
FOOD_LV2_SIZE = 40
FOOD_LV3_SIZE = 50

# path of assets
ASSET_PATH = path.join(path.dirname(__file__), "..", "asset")
LEVEL_PATH = path.join(path.dirname(__file__), "..", "maps")
SOUND_PATH = path.join(path.dirname(__file__), "..", "asset", "sounds")
MUSIC_PATH = path.join(path.dirname(__file__), "..", "asset", "music")

BG_PATH = path.join(ASSET_IMAGE_DIR, "background.png")
SQUID_PATH = path.join(ASSET_IMAGE_DIR, "squid.png")
SQUID2_PATH = path.join(ASSET_IMAGE_DIR, "squid2.png")

IMG_ID_FOOD01_L = "food_01_L"
IMG_ID_FOOD02_L = "food_02_L"
IMG_ID_FOOD03_L = "food_03_L"
IMG_ID_FOOD01_R = "food_01_R"
IMG_ID_FOOD02_R = "food_02_R"
IMG_ID_FOOD03_R = "food_03_R"

FOOD01_L_PATH = path.join(ASSET_IMAGE_DIR, "food_01_L.png")
FOOD02_L_PATH = path.join(ASSET_IMAGE_DIR, "food_02_L.png")
FOOD03_L_PATH = path.join(ASSET_IMAGE_DIR, "food_03_L.png")
FOOD01_R_PATH = path.join(ASSET_IMAGE_DIR, "food_01_R.png")
FOOD02_R_PATH = path.join(ASSET_IMAGE_DIR, "food_02_R.png")
FOOD03_R_PATH = path.join(ASSET_IMAGE_DIR, "food_03_R.png")

GARBAGE01_PATH = path.join(ASSET_IMAGE_DIR, "garbage_01.png")
GARBAGE02_PATH = path.join(ASSET_IMAGE_DIR, "garbage_02.png")
GARBAGE03_PATH = path.join(ASSET_IMAGE_DIR, "garbage_03.png")


ASSET_IMG_URL = "https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/swimming-squid-battle/main/asset/img/"
BG_URL =  ASSET_IMG_URL + "background.png"
SQUID_URL =  ASSET_IMG_URL + "squid.png"
SQUID2_URL =  ASSET_IMG_URL + "squid2.png"
# Food URLs
FOOD01_L_URL = ASSET_IMG_URL + "food_01_L.png"
FOOD02_L_URL = ASSET_IMG_URL + "food_02_L.png"  # Assuming the naming pattern is similar
FOOD03_L_URL = ASSET_IMG_URL + "food_03_L.png"
FOOD01_R_URL = ASSET_IMG_URL + "food_01_R.png"
FOOD02_R_URL = ASSET_IMG_URL + "food_02_R.png"
FOOD03_R_URL = ASSET_IMG_URL + "food_03_R.png"

# Garbage URLs
GARBAGE01_URL = ASSET_IMG_URL + "garbage_01.png"
GARBAGE02_URL = ASSET_IMG_URL + "garbage_02.png"
GARBAGE03_URL = ASSET_IMG_URL + "garbage_03.png"
