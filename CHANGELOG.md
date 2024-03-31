## Change Log

### Version [0.1.4](https://pypi.org/project/screenapi-cli/0.1.4/)

- **cmd:scrape-from-file** renamed `scrape` to `scrape-from-file`, See more `sapi scrape-from-file --help`
- **cmd:scrape-from-sheet** added `scrape-from-sheet` to scrape from a input sheet
- Misc changes


### Version [0.1.3](https://pypi.org/project/screenapi-cli/0.1.3/)
- **--version** fixed version checking logic
- **cmd:scrape** Added a basic progressbar
- **cmd:export** Added a basic progressbar
- added alias `sapi` (default: `screenapi-cli`)


### Version [0.1.3b0](https://pypi.org/project/screenapi-cli/0.1.3b0/)
- **cmd:scraper**: If any kind of exception occurs during the post request, print the error details and exit
- **cmd:list** Renamed `list` to `config`.
- Added some try...except blocks

### Version [0.1.3a0](https://pypi.org/project/screenapi-cli/0.1.3a0/)
- **cmd:scraper**: Fixed Typo 

### Version [0.1.2](https://pypi.org/project/screenapi-cli/0.1.2/)

#### Features

- **cmd:scrape**: Renamed `--concurrency` option to `--max-workers` for better clarity. ([1f1cf30](https://github.com/FutureForge-Studios/screenapi-cli/commit/1f1cf3069c37919677543ee7f00677b732314418))

#### Fixes

- **cmd:export**: Fixed issue where serial number counting started from 0. ([1f1cf30](https://github.com/FutureForge-Studios/screenapi-cli/commit/1f1cf3069c37919677543ee7f00677b732314418))

#### Breaking Changes

- **Update**: Switched from `asyncio.gather` to `concurrent.futures.Threadpool`. This may affect speed ([1f1cf30](https://github.com/FutureForge-Studios/screenapi-cli/commit/1f1cf3069c37919677543ee7f00677b732314418))

### Previous Version: [0.1.1](https://pypi.org/project/screenapi-cli/0.1.1/)