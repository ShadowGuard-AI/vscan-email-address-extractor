# vscan-email-address-extractor

Extracts email addresses from web pages, files, and directories, for uncovering exposed email addresses. Part of a lightweight web application vulnerability scanning collection focused on common misconfigurations.

![Logo](logo.png)
![Banner](banner.png)

## How it works

- URL source: the page is fetched and searched both in its visible text and in its raw source, so addresses in mailto hrefs, meta tags, scripts, and HTML comments are found as well as addresses in body text.
- File source: the file is read as text and searched.
- Directory source: every file in the directory is searched, and subdirectories too when `-r` is given. If files are found but every one fails to read, that is reported as an error rather than a successful empty extraction.
- Results are unique and printed or saved in sorted order, so repeated runs over the same source produce the same output.

If the source is invalid or cannot be read, the tool prints an error and exits with status 1. If the output file cannot be written, the tool also exits 1. A source that reads correctly keeps the normal exit status 0, including when no addresses are found.

## Install

`git clone https://github.com/ShadowGuard-AI/vscan-email-address-extractor`

Requires Python 3 with requests and beautifulsoup4 (see requirements.txt).

## Usage

`python3 main.py <source> [-r] [-o OUTPUT]`

Examples:

- `python3 main.py http://127.0.0.1:8000/page.html`
- `python3 main.py my_document.txt`
- `python3 main.py ./my_directory -r -o output.txt`

## Parameters

- `source`: Source to extract emails from (URL, file path, or directory).
- `-h`: Show help message and exit.
- `-r`, `--recursive`: Recursively search directories.
- `-o`, `--output`: Output file to save the extracted email addresses.

## License

MIT. See LICENSE.
