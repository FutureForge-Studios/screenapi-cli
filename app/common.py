from enum import Enum
import re


PROVIDERS = {
    "glowroad": "/glowroad",
    "tradeindia": "/tradeindia",
    "quora": "/quora",
    "pinterest": "/pinterest",
    "youtube": "/youtube",
    "alibaba": "/alibaba",
    "indiemart": "/indiemart",
    "amazon": "/amazon",
    "telegram": "/telegram",
    "t.me": "/telegram",
    "kooapp": "/kooapp",
    "snapdeal": "/snapdeal",
    "exportersindia": "/exportersindia",
    "shopclues": "/shopclues",
    "gethuman": "/gethuman",
    "reddit": "/reddit",
    "meesho": "/meesho",
    "twitter": "/twitter",
    "facebook": "/facebook",
    "flipkart": "/flipkart",
    "shopsy": "/shopsy",
    "instagram": "/instagram",
    "linkedin": "/linkedin",
}

providers_pattern = {re.compile(key): value for key, value in PROVIDERS.items()}


class sheetType(Enum):
    ecom = "ecom"
    social = "social"
    # flipkart = "flipkart"
    # telegram = "telegram"
    # facebook = "facebook"
    # amazon = "amazon"
    # meesho = "meesho"
    # shopclues = "shopclues"
    # gethuman = "gethuman"
    # instagram = "instagram"
    # twitter = "twitter"
    # linkedin = "linkedin"
    # glowroad = "glowroad"
    # tradeindia = "tradeindia"
    # quora = "quora"
    # pinterest = "pinterest"
    # youtube = "youtube"
    # alibaba = "alibaba"
    # indiemart = "indiemart"
    # exportersindia = "exportersindia"
