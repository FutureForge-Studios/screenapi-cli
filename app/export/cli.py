import json
import os

import pandas as pd
from rich.progress import Progress


def process_and_append_data(file_path, df):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        for key, value in data.items():
            if value is None or value is False:
                data[key] = 0
            if key == "Image" or key == "image" and value not in ["", "0", None]:
                data[key] = os.path.basename(value)  # Extract only the filename
        temp_df = pd.DataFrame([data])
    return pd.concat([df, temp_df], ignore_index=True)


def main(input_dir: str, output: str, sort_by: str):
    df = pd.DataFrame()
    json_files = [f for f in os.listdir(input_dir) if f.endswith(".json")]

    if len(json_files) == 0:
        print("No JSON files found in the input directory.", input_dir)
        return

    with Progress() as progress:
        task = progress.add_task("Processing JSON file", total=len(json_files))
        for file_name in json_files:
            file_path = os.path.join(input_dir, file_name)
            df = process_and_append_data(file_path, df)
            progress.update(
                task,
                advance=1,
            )

    # print(df.head())
    df["sl"] = pd.RangeIndex(start=1, stop=len(df) + 1)
    df = df.reindex(columns=[sort_by, *df.columns[:-1]])
    df.sort_values(by=sort_by, inplace=True)
    df.to_excel(output, index=False)
