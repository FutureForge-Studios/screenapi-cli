import json
import os
from pathlib import Path
import shutil
from typing import Any, Optional
import concurrent.futures
from click import echo
from rich.progress import TaskID, Progress
import pandas
import configparser
from rich import print
from httpx import Client
from app.common import providers_pattern, sheetType
from app.txt.cli import getId
from app.setup.utils import config_file

# global output_dir
config = configparser.ConfigParser()
config.read(config_file())
OUTPUT_DIR: Path = None


def read_mapping(sitename: str, swap: bool = False) -> dict:
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

    social = {
        "S.No.": "sl",
        "Image": "image",
        "Heading": "description",
        "URL": "url",
    }


    match sitename:
        case "ecom":
            if swap:
                return {ecom[key]: key for key in ecom}

            return ecom

        case "social":
            if swap:
                return {social[key]: key for key in social}
            return social


def convert_to_json(input_path: Path, site: sheetType, save: Optional[bool] = True):
    # setup input_path and output_file (excel to json)

    # read excel, rename column, fix date
    df = pandas.read_excel(input_path)
    df.rename(columns=read_mapping(site.value), inplace=True)

    if not df["Date Added"].isna().all():
        try:
            df["Date Added"] = df["Date Added"].dt.strftime("%d/%m/%Y")
        except AttributeError:
            try:
                df["Date Added"] = df["Date Added"].dt.strftime("%d-%m-%Y")
            except AttributeError:
                print(
                    "[dim]`Date Added` column is probably empty or in wrong format.[/]"
                )

    if df["sl"].isnull().all():
        sequence = range(1, len(df) + 1)
        df["sl"] = sequence

    df.fillna("0", inplace=True)

    # # Not changing key/column name here

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

    # check if facebook is in the site list
    # if (
    #     sheetType.facebook in site
    #     if isinstance(site, list)
    #     else sheetType.facebook == site
    # ):
    #     for data in jsonData:
    #         if data["url"].startswith("https://www.facebook.com/"):
    #             if not bool(
    #                 re.search(r"marketplace|posts|groups|profile", data["url"]),
    #             ):
    #                 data.update({"type": "posts"})
    #     return jsonData

    if save:
        with open(os.path.join(OUTPUT_DIR, "converted.json"), "w") as f:
            f.write(json.dumps(jsonData, indent=4))
        print(
            "[bold]Converted to json, Saved to: ",
            os.path.join(OUTPUT_DIR, "converted.json"),
        )
    return jsonData


def convert_to_xlsx(
    input_path: Path,
    output_file: str,
    site: sheetType,
    sort_by: str = "sl",
):
    global OUTPUT_DIR
    df = pandas.DataFrame()

    def process_and_append_data(file_path, df):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            for key in data.keys():
                if key == "image":
                    data[key] = f"{data['sl']}.png"
            temp_df = pandas.DataFrame([data])
        return pandas.concat([df, temp_df], ignore_index=True)

    for root, dirs, files in os.walk(input_path):
        if root.startswith(("images")):
            continue
        for file in files:
            if file.startswith("converted"):
                continue
            if file.endswith(".json"):
                df = process_and_append_data(os.path.join(root, file), df)

    df.drop(columns=["key", "endpoint", "type"], inplace=True)
    df.sort_values(by=sort_by, inplace=True)

    df.rename(columns=read_mapping(site.value, swap=True), inplace=True)

    df.to_excel(output_file, index=False)


def doneIds(output_dir: str):
    ids = []
    for root, dirs, files in os.walk(output_dir):
        if root.startswith(("images")):
            continue
        for file in files:
            if file.startswith("converted"):
                continue
            if file.endswith(".json"):
                ids.append(int(os.path.basename(file).split(".")[0]))

    print("Already done: ", len(ids))
    return ids


def request(options: dict[str, Any]):
    client: Client = options["client"]
    skipImages: bool = options["skip_images"]
    taskId: TaskID = options["task_id"]
    progress: Progress = options["progress"]
    data: dict[str, str] = options["data"]
    # keyMap: dict[str, str] = data["map"]
    global OUTPUT_DIR
    try:
        response = client.post(
            data.get("endpoint"),
            json={"url": data.get("url"), "type": data.get("type")},
            headers={"x-screenapi-key": config.get("default", "api_key")},
        )
    except Exception as error:
        print(f"Current URL: {data.get('url')}")
        print(f"Error: {error}")
        print("Exiting...")
        # exit(1)

    jsonResponse: dict[str, str] = response.json()

    if "image" in jsonResponse and not skipImages:
        with open(
            os.path.join(OUTPUT_DIR, "images", str(data["sl"]) + ".png"),
            "wb",
        ) as f:
            image_url = jsonResponse["image"]
            image_response = client.get(
                image_url,
                # headers={"x-screenapi-key": config.get("default", "api_key")},
            )
            f.write(image_response.content)

    output_filename: str = os.path.join(
        OUTPUT_DIR,
        data.get("endpoint").removeprefix("/"),
        str(data.get("sl")) + ".json",
    )

    os.makedirs(Path(output_filename).parent, exist_ok=True)

    try:
        for key, value in jsonResponse.items():
            if key in data:
                data[key] = value

            if key == "description":
                data[key] = (
                    jsonResponse.get("title")
                    if jsonResponse.get("description") == "0"
                    else jsonResponse.get("description")
                )

        with open(output_filename, "w") as file:
            json.dump(data, file, indent=2)
        # print(f"Saved to {output_filename}")
        progress.update(taskId, advance=1)
    except Exception as error:
        print(f"Error saving to {output_filename}: {error}")


def main(
    input_path: Path,
    site: sheetType,
    output_dir: Optional[Path] = None,
    # save: Optional[bool] = True,
    max_workers: Optional[int] = config.get("default", "max_workers"),
    overwrite: Optional[bool] = False,
    skip_images: Optional[bool] = False,
):
    global OUTPUT_DIR
    if output_dir is None:
        # global output_dir
        output_dir = os.path.join(
            os.path.dirname(input_path), getId(Path(input_path).stem)
        )

    if isinstance(max_workers, str):
        max_workers = int(max_workers)

    input_path = os.path.abspath(input_path)
    output_dir = OUTPUT_DIR = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)
    # try:
    data = convert_to_json(input_path=input_path, site=site)
    original_length = len(data)

    if not overwrite:
        done_already = doneIds(output_dir)
    else:
        done_already = []
    data = [i for i in data if i["sl"] not in done_already]

    client = Client(
        http2=True,
        timeout=None,
        follow_redirects=True,
        base_url=config.get("default", "api_url"),
    )

    max_workers = max_workers if max_workers is not None else 10
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        with Progress() as progress:
            scraping_tasks = progress.add_task(
                "Updating sheet", total=original_length, completed=len(done_already)
            )
            executor.map(
                request,
                [
                    {
                        "client": client,
                        "skip_images": skip_images,
                        "task_id": scraping_tasks,
                        "progress": progress,
                        "data": d,
                    }
                    for d in data
                ],
            )
            executor.shutdown(wait=True)

    print("Generating Excel Sheet")

    convert_to_xlsx(
        input_path=Path(output_dir),
        output_file=os.path.join(output_dir, f"{Path(input_path).stem}.xlsx"),
        site=site,
        sort_by="sl",
    )

    print("Moving files!")

    if not skip_images:
        shutil.move(
            os.path.join(output_dir, "images"),
            os.path.join(Path(input_path).parent, Path(input_path).stem, "images"),
        )

    shutil.move(
        os.path.join(output_dir, Path(input_path).stem + ".xlsx"),
        os.path.join(
            Path(input_path).parent,
            Path(input_path).stem,
            Path(input_path).stem + ".xlsx",
        ),
    )

    print("Done!")


# if __name__ == "__main__":
#     main(
#         input_path=Path("./dumps/Lakme Eyeconic 18-03-2024.xlsx"),
#         site=[sheetType.meesho, sheetType.flipkart],
#         max_workers=3,
#         save=True,
#     )
