"""
Author: Saloua Chlaily
Date: August 13, 2024

Description:
This script is designed to retrieve PMC article identifiers (PMCIDs) based on a search term,
download the corresponding PDF files from the NCBI FTP server, and clean up the downloaded data.

Modules Used:
- tarfile: For handling tar.gz files.
- shutil: For file operations such as moving and deleting files.
- requests: For making HTTP requests to download files.
- os: For interacting with the file system.
- bs4 (BeautifulSoup): For parsing XML data.
- pandas: For handling CSV data.

Functions:
- get_url(file_csv, pmc_id): Retrieves the URL path for a specific PMC ID from a CSV file.
- download_file(url, save_dir, file_name=None): Downloads a file from a given URL.
- download_pmc_pdf(pmc_id, file_csv, save_dir): Downloads and extracts a PMC article's PDF.
- unzip_and_clean(pmc_id, save_dir): Unzips the downloaded tar.gz file, moves the PDF, and cleans up.
- get_pmc_ids(search_term, save_dir, file_name, RetMax=20): Retrieves PMCIDs based on a search term.

Usage:
1. Configure the search term and directories in the `__main__` section.
2. Ensure that the CSV file with file paths (`oa_comm_use_file_list.csv`) is present. It can be downloaded from https://ftp.ncbi.nlm.nih.gov/pub/pmc/
3. Run the script to download and process PMC PDFs.
"""

import tarfile
import shutil
import requests
import os
from bs4 import BeautifulSoup
import pandas as pd

def get_url(file_csv, pmc_id):
    """
    Retrieve the URL path for a specific PMC ID from the provided CSV file.
    
    Parameters:
    file_csv (pd.DataFrame): DataFrame containing the CSV data.
    pmc_id (str): The PMC ID to look up.
    
    Returns:
    str or None: The URL path if found, else None.
    """
    # Filter the CSV for the given PMC ID
    response = file_csv.loc[file_csv["Accession ID"] == f"PMC{pmc_id}", "File"]
    if response.empty:
        return None
    return response.values[0]

def download_file(url, save_dir, file_name=None):
    """
    Download a file from a given URL and save it to the specified directory.
    
    Parameters:
    url (str): The URL of the file to download.
    save_dir (str): Directory to save the downloaded file.
    file_name (str, optional): Custom file name. If not provided, the file name is extracted from the URL.
    
    Returns:
    None
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # Create the directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        
        # Use the last part of the URL as the file name if none is provided
        if file_name is None:
            file_name = url.split("/")[-1]
        file_path = os.path.join(save_dir, file_name)
        
        # Save the downloaded content to a file
        with open(file_path, 'wb') as file:
            file.write(response.content)
        
        print(f"File downloaded and saved as {file_path}")
    else:
        print(f"Failed to download file from {url}. HTTP status code: {response.status_code}")

def download_pmc_pdf(pmc_id, file_csv, save_dir):
    """
    Download and extract a PMC article's PDF given its PMC ID.
    
    Parameters:
    pmc_id (str): The PMC ID of the article.
    file_csv (pd.DataFrame): DataFrame containing the CSV data with file paths.
    save_dir (str): Directory to save the PDF file.
    
    Returns:
    None
    """
    base_url = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/"
    
    # Get the URL path for the given PMC ID
    link = get_url(file_csv, pmc_id)
    if link is None:
        print(f"No PDF found for {pmc_id}")
        return
    
    # Construct the full URL and download the file
    url = f"{base_url}{link}"
    download_file(url, save_dir)
    
    # Extract the downloaded file and clean up
    unzip_and_clean(pmc_id, save_dir)
        
def unzip_and_clean(pmc_id, save_dir):
    """
    Unzip the downloaded tar.gz file, move the PDF to the main directory, and clean up.
    
    Parameters:
    pmc_id (str): The PMC ID of the article.
    save_dir (str): Directory where the tar.gz file is located and where the PDF will be saved.
    
    Returns:
    None
    """
    tar_gz_file = f"PMC{pmc_id}.tar.gz"
    tar_gz_path = os.path.join(save_dir, tar_gz_file)
    
    # Extract the tar.gz file
    with tarfile.open(tar_gz_path, "r:gz") as tar:
        tar.extractall(path=save_dir)
    
    # Locate the extracted PDF file
    extracted_dir = os.path.join(save_dir, f"PMC{pmc_id}")
    pdf_files = [f for f in os.listdir(extracted_dir) if f.endswith('.pdf')]
    
    if pdf_files:
        # Move each PDF file to the main directory
        for pdf_file in pdf_files:
            target_path = os.path.join(save_dir, pdf_file)
            if not os.path.exists(target_path):
                shutil.move(os.path.join(extracted_dir, pdf_file), save_dir)
                print(f"Extracted PDF: {pdf_file}")
            else:
                print(f"File {pdf_file} already exists!")
    else:
        print("No PDF found in the archive.")
    
    # Clean up the extracted directory and the tar.gz file
    shutil.rmtree(extracted_dir)
    os.remove(tar_gz_path)

def get_pmc_ids(search_term, save_dir, file_name, RetMax=20):
    """
    Retrieve PMC article identifiers (PMCIDs) based on a search term.
    For more details check this website https://www.ncbi.nlm.nih.gov/pmc/tools/get-pmcids/
    
    Parameters:
    search_term (str): The search term to query.
    save_dir (str): Directory to save the search results.
    file_name (str): Name of the file to save the search results.
    RetMax (int): Maximum number of results to retrieve.
    
    Returns:
    list: List of retrieved PMC IDs.
    """
    # NCBI E-utilities search URL
    esearch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term={search_term}&RetMax={RetMax}"
    
    # Download the search result XML
    download_file(esearch_url, save_dir, file_name=file_name)

    # Parse the XML file to extract PMC IDs
    with open(os.path.join(save_dir, file_name), 'r') as f:
        data = f.read()
    soup = BeautifulSoup(data, "xml")
    ids = soup.find_all('Id')
    
    return [id_tag.text for id_tag in ids]

if __name__ == "__main__":
    # Configuration
    search_term = "gene"
    save_dir = "genes_dataset"
    
    # Retrieve PMC IDs based on the search term
    pmc_ids = get_pmc_ids(search_term, save_dir, f"esearch_pmd_{search_term}_id.xml", RetMax=20)
    
    # Load the CSV file containing file paths
    file_csv = pd.read_csv("oa_comm_use_file_list.csv")
    
    # Download PDFs for each PMC ID
    for pmc_id in pmc_ids:
        pdf_save_dir = os.path.join(save_dir, "pdfs")  # Directory to save PDFs
        download_pmc_pdf(pmc_id, file_csv, pdf_save_dir)
