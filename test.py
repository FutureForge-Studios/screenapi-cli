from difflib import SequenceMatcher
import json
import re
import pandas

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

df = pandas.read_excel("/home/rony/Projects/screenapi-cli/dumps/shopsy10k.xlsx")
firstColumnMatchRatio = SequenceMatcher(a="S.No.", b=df.columns[0]).real_quick_ratio()

# print({ "firstColumnMatchRatio": firstColumnMatchRatio })
if firstColumnMatchRatio > 0.7 and firstColumnMatchRatio != 1.0:
    print("[dim]`S.No.` column is probably in wrong format, fixing..[/]")
    df.rename(columns={df.columns[0]: "S.No."}, inplace=True)

ecom = {
    "S.No.": "sl",
    "Image": "image",
    "URL": "url",
    "Title": "title",
    "MRP": "mrp",
    "Price": "price",
    "Discount Percentage": "discount",
    "Rating": "productRating",
    "Seller Rating": "sellerRating",
    "UserName": "sellerName",
    "Number of Ratings": "totalRating",
    "Number of Reviews": "totalReview",
    "PID": "pid",
    "LID": "lid",
    "Flipkart Assured": "flipkarAssured",
}

df.rename(columns=ecom, inplace=True)
if df["sl"].isnull().all():
    sequence = range(1, len(df) + 1)
    df["sl"] = sequence

df.fillna("0", inplace=True)

jsonData = df.to_dict(orient="records")
for data in jsonData:
    for regex, endpoint in providers_pattern.items():
        if regex.search(data["url"]):
            data.update(
                {
                    "key": regex.pattern,
                    "endpoint": endpoint,
                    "type": None,
                }
            )
            with open(f"dumps/shopsy10k/{data['sl']}.json", "w") as _f:
                _f.write(json.dumps(data))
