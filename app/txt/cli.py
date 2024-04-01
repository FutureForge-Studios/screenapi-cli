import configparser
import os
import re
from json import dump
from httpx import Client
from typing import Optional, Any
from uuid import UUID, uuid5
from app.setup.utils import config_file
from app.common import providers_pattern
import concurrent.futures
from rich import print
from rich.progress import TaskID, Progress

config = configparser.ConfigParser()
scraping_tasks = ""
config.read(config_file())


def getId(url: str):
    return str(uuid5(UUID(config.get("default", "namespace")), url))


def read_urls_from_file(file_path: str) -> list[str]:
    """
    Reads a list of URLs from a file and returns them as a list of strings.

    Args:
        file_path (str): The path to the file containing the URLs.

    Returns:
        list[str]: A list of URLs read from the file.

    Raises:
        FileNotFoundError: If the specified file does not exist.

    Example:
        >>> read_urls_from_file('urls.txt')
        ['https://example.com', 'https://google.com', 'https://github.com']
    """
    with open(file_path) as f:
        return f.read().splitlines()


def generate_mapped_urls(urls: list[str]):

    mapped_urls = []

    for url in urls:
        org_url = url
        for regex, endpoint in providers_pattern.items():
            if regex.search(url):
                if "," in url:
                    url, type = url.split(",")
                    type = type.strip()

                mapped_urls.append(
                    {
                        "key": regex.pattern,
                        "endpoint": endpoint,
                        "url": url.strip(),
                        "type": type if "," in org_url else None,
                    }
                )
                break

    return mapped_urls


def doneIds(output_dir: str = config.get("default", "output_dir")) -> list[str]:
    ids = []
    for root, dirs, files in os.walk(output_dir):
        if root.endswith("images"):
            continue
        for file in files:
            if file.endswith(".json"):
                ids.append(os.path.basename(file).split(".")[0])

    return ids


def _request(
    options: dict[str, Any],
):
    client: Client = options["client"]
    endpoint: str = options["endpoint"]
    target_url: str = options["url"]
    type: Optional[str] = options["type"]
    skipImages: bool = options["skip_images"]
    taskId: TaskID = options["task_id"]
    progress: Progress = options["progress"]

    try:
        response = client.post(
            endpoint,
            json={"url": target_url, "type": type},
            headers={"x-screenapi-key": config.get("default", "api_key")},
        )
    except Exception as error:
        print(f"Current URL: {target_url}")
        print(f"Error: {error}")
        print("Exiting...")
        exit(1)

    jsonResponse = response.json()

    if "image" in jsonResponse and not skipImages:
        # print("id: " + jsonResponse["id"], "saving image")
        image_url = jsonResponse["image"]
        image_response = client.get(
            image_url,
            headers={"x-screenapi-key": config.get("default", "api_key")},
        )
        with open(
            os.path.join(
                config.get("default", "output_dir"), image_url.removeprefix("/")
            ),
            "wb",
        ) as f:
            f.write(image_response.content)

    output_filename = os.path.join(
        config.get("default", "output_dir"),
        endpoint.removeprefix("/"),
        jsonResponse.get("id") + ".json",
    )

    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    try:
        with open(output_filename, "w") as file:
            dump(jsonResponse, file, indent=2)
        progress.update(taskId, advance=1)
    except Exception as error:
        print(f"Error saving to {output_filename}: {error}")


async def main(
    urls_file: str,
    max_workers: Optional[int] = config.get("default", "max_workers"),
    overwrite: Optional[bool] = False,
    skip_images: Optional[bool] = False,
):
    global scraping_tasks
    urls = read_urls_from_file(urls_file)
    mapped_urls = generate_mapped_urls(urls)
    done_already = []
    if not overwrite:
        done_already = doneIds()

    os.makedirs(
        os.path.join(config.get("default", "output_dir"), "images"), exist_ok=True
    )

    client = Client(
        http2=True,
        timeout=None,
        follow_redirects=True,
        base_url=config.get("default", "api_url"),
    )

    max_workers = max_workers if max_workers is not None else 10
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        with Progress() as progress:
            mapped_urls = [
                d for d in mapped_urls if getId(d["url"]) not in done_already
            ]
            scraping_tasks = progress.add_task("Scraping", total=len(mapped_urls))
            executor.map(
                _request,
                [
                    {
                        "client": client,
                        "skip_images": skip_images,
                        "endpoint": d["endpoint"],
                        "key": d["key"],
                        "url": d["url"],
                        "type": d["type"],
                        "task_id": scraping_tasks,
                        "progress": progress,
                    }
                    for d in mapped_urls
                ],
            )
            executor.shutdown(wait=True)
    print("Done!")


# if __name__ == "__main__":
# from dotenv import load_dotenv

# load_dotenv()

# print(doneIds())
# asyncio.run(main())
# async with AsyncClient() as client:
#     for url in generate_mapped_urls(urls):
#         await _request(client, url["endpoint"], url["url"], url["type"])
