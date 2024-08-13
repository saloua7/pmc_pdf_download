# PMC Article Downloader

This Python script retrieves PMC article identifiers (PMCIDs) based on a search term, downloads the corresponding PDF files from the NCBI FTP server, and extracts the downloaded data.

## Features

- Retrieves PMC article identifiers based on a search term using NCBI's E-utilities.
- Downloads PDF files from the NCBI FTP server.
- Extracts and cleans up the downloaded files.

## Requirements

- Python 3.12
- Required Python libraries:
  - `requests`
  - `pandas`
  - `beautifulsoup4`
  - `tarfile` (included in Python standard library)
  - `shutil` (included in Python standard library)
  - `os` (included in Python standard library)

You can install the required libraries using `pip`:

```bash
pip install requests pandas beautifulsoup4
