from json import loads
import os

output_dir = "dumps/d1677a86-5917-5759-8991-6a8669f5d469/meesho"

ids = []
for root, dirs, files in os.walk(output_dir):
    if root.startswith(("images")):
        continue
    for file in files:
        if file.startswith("converted"):
            continue
        if file.endswith(".json"):
            with open(os.path.join(root, file), "r") as f:
                data = loads(f.read())
                if (
                    data["title"]
                    in [
                        "0",
                        # "Not Enough Ratings",
                        # "(New Seller)",
                    ]
                    and data["price"] == "0"
                ):
                    os.remove(os.path.join(root, file))
                    print(file)
            # ids.append(int(os.path.basename(file).split(".")[0]))
