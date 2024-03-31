# screenapi-cli

## Installation

```bash
python -m pip install screenapi-cli

screenapi-cli --help
```

## Step 1 - setup cli
```bash
screenapi-cli setup --api-url "<api-url>" --api-key "<api-key>" --max_workers 15
```

check all options with `screenapi-cli setup --help`

## Step 2 - start scraping

```bash
touch urls.txt # create a urls.txt file and add urls, one line == one url

screenapi-cli scrape urls.txt #
```
check all options with `screenapi-cli scrape --help`

## Step 3 - export to excel sheet
```bash
screenapi-cli export --input-dir "<path to scraper's output>" # check below
```

* example : scraped flipkart urls, and export execl file in default location
    ```bash
    screenapi-cli export --input-dir "flipkart" # `flipkart` will convert into `/path/to/screenapi-cli/config/output/flipkart` and --output-file will be `/path/to/screenapi-cli/config/output/flipkart.xlsx` and --sort-by will be `sl`
    ```

* example: custom input-dir , custom output-file
    ```bash
    screenapi-cli export --input-dir "~/Downloads/scraped" --output-file "./flipkart.xlsx"
    ```

## command: `screenapi-cli list`
```bash
[default]
output_dir = /path/to/output
max_workers = 15
api_url = *****************
api_key = *************************
namespace = ******-****-****-****-*********
export_dir = /path/to/export
```
check all options with `screenapi-cli export --help`
