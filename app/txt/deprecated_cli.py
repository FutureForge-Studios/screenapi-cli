import asyncio
import configparser
from enum import Enum
import os
import re
from json import dump
from httpx import AsyncClient
from typing import Optional
from uuid import UUID, uuid5
from aiofile import async_open
from app.setup.utils import config_file


config = configparser.ConfigParser()
config.read(config_file())

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
    """
    Generates a list of mapped URLs based on a list of input URLs and a set of regular expressions.

    Parameters:
        urls (list[str]): A list of input URLs.

    Returns:
        list[dict]: A list of dictionaries containing the mapped URLs. Each dictionary has the following keys:
            - key (str): The regular expression pattern used to match the URL.
            - endpoint (str): The endpoint associated with the regular expression pattern.
            - url (str): The original URL.
            - type (str or None): The type of the URL, if specified in the input URL.
    """
    regex_patterns = {re.compile(key): value for key, value in PROVIDERS.items()}
    mapped_urls = []

    for url in urls:
        org_url = url
        for regex, endpoint in regex_patterns.items():
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


async def _request(
    client: AsyncClient,
    endpoint: str,
    target_url: str,
    type: Optional[str] = None,
    skipImages: bool = False,
):
    response = await client.post(
        endpoint,
        json={"url": target_url, "type": type},
        headers={"x-screenapi-key": config.get("default", "api_key")},
    )
    jsonResponse = response.json()

    if "image" in jsonResponse and not skipImages:
        print("id: " + jsonResponse["id"], "saving image")
        image_url = jsonResponse["image"]
        image_response = await client.get(
            image_url,
            headers={"x-screenapi-key": config.get("default", "api_key")},
        )
        async with async_open(
            os.path.join(
                config.get("default", "output_dir"), image_url.removeprefix("/")
            ),
            "wb",
        ) as f:
            await f.write(image_response.content)

    output_filename = os.path.join(
        config.get("default", "output_dir"),
        endpoint.removeprefix("/"),
        jsonResponse.get("id") + ".json",
    )

    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    try:
        with open(output_filename, "w") as file:
            dump(jsonResponse, file, indent=2)
        print(f"Saved to {output_filename}")
    except Exception as error:
        print(f"Error saving to {output_filename}: {error}")


async def main(
    urls_file: str,
    concurrency: Optional[int] = config.get("default", "concurrency"),
    overwrite: Optional[bool] = False,
    skip_images: Optional[bool] = False,
):
    tasks = []
    urls = read_urls_from_file(urls_file)
    mapped_urls = generate_mapped_urls(urls)
    done_already = []
    if not overwrite:
        done_already = doneIds()

    os.makedirs(
        os.path.join(config.get("default", "output_dir"), "images"), exist_ok=True
    )

    client = AsyncClient(
        http2=True,
        timeout=None,
        base_url=config.get("default", "api_url"),
    )
    for d in mapped_urls:
        if getId(d["url"]) not in done_already:
            tasks.append(
                _request(client, d["endpoint"], d["url"], d["type"], skip_images)
            )

    concurrency_limit = concurrency if concurrency is not None else 10
    for i in range(0, len(tasks), concurrency_limit):
        batch = tasks[i : i + concurrency_limit]
        await asyncio.gather(*batch)

    await client.aclose()
    print("Done!")


# if __name__ == "__main__":
# from dotenv import load_dotenv

# load_dotenv()

# print(doneIds())
# asyncio.run(main())
# async with AsyncClient() as client:
#     for url in generate_mapped_urls(urls):
#         await _request(client, url["endpoint"], url["url"], url["type"])
