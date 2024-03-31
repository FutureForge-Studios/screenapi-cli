import configparser
import os
import sys
config = configparser.ConfigParser()
try:
    config.add_section("default")
except configparser.DuplicateSectionError:
    pass



def config_file(dir_only: bool = False):
    if sys.platform.startswith("win"):
        # Windows
        config_dir = os.path.join(os.environ["APPDATA"], "screenapi-cli")
    elif sys.platform.startswith("linux"):
        # Linux
        config_dir = os.path.join(os.path.expanduser("~"), ".config", "screenapi-cli")
    else:
        config_dir = os.path.join(os.path.expanduser("~"), ".config", "screenapi-cli")

    # Ensure the directory exists
    os.makedirs(config_dir, exist_ok=True)

    if dir_only:
        return config_dir
        
    return os.path.join(config_dir, "config.ini")


def add_to_config(key: str, value: str):
    config.read(config_file())

    config["default"][key] = value
    with open(config_file(), "w") as configfile:
        config.write(configfile)

async def main():
    pass


# if __name__ == "__main__":
    # add_to_config("api_key", "user_3ZN3pvAqHvZLCbDASxFp4Qz3")
