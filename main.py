import argparse
import re
import requests
from bs4 import BeautifulSoup
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_argparse():
    """
    Sets up the argument parser for the script.

    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    parser = argparse.ArgumentParser(description='Extracts email addresses from web pages, files, and directories.')
    parser.add_argument('source', type=str, help='Source to extract emails from (URL, file path, or directory).')
    parser.add_argument('-r', '--recursive', action='store_true', help='Recursively search directories.')
    parser.add_argument('-o', '--output', type=str, help='Output file to save the extracted email addresses.')
    return parser


def extract_emails_from_url(url):
    """
    Extracts email addresses from a given URL.

    Args:
        url (str): The URL to extract email addresses from.

    Returns:
        set: A set of unique email addresses found in the URL.  Returns None on error.
    """
    try:
        response = requests.get(url, timeout=10)  # Add timeout to prevent indefinite hanging
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')
        # get_text keeps only visible text. Addresses that live in mailto
        # hrefs, in meta tags, in scripts, or in HTML comments are dropped by
        # the parse before the regex ever runs, and those are common places
        # for a contact address to sit.
        text = soup.get_text()
        emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))
        return emails
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error processing URL {url}: {e}")
        return None


def extract_emails_from_file(file_path):
    """
    Extracts email addresses from a given file.

    Args:
        file_path (str): The path to the file to extract email addresses from.

    Returns:
        set: A set of unique email addresses found in the file. Returns None on error.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        # The pattern needs a dot and at least two letters at the end, so
        # addresses under a one letter or numeric ending never match. It
        # also matches inside longer strings, so the middle of a token can
        # be harvested as an address that nobody wrote.
        emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))
        return emails
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")
        return None


def extract_emails_from_directory(directory_path, recursive=False):
    """
    Extracts email addresses from all files in a given directory.

    Args:
        directory_path (str): The path to the directory to extract email addresses from.
        recursive (bool): Whether to recursively search subdirectories.

    Returns:
        set: A set of unique email addresses found in the directory. Returns None on error.
    """
    all_emails = set()
    try:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                emails = extract_emails_from_file(file_path)
                if emails is not None:
                    all_emails.update(emails)
            # The break still walks the top directory fully first. A directory
            # whose files all failed to read returns an empty set rather than
            # None, because per file failures are swallowed in the loop above,
            # so main exits 0 and reports a successful empty extraction.
            if not recursive:
                break
        return all_emails
    except Exception as e:
        logging.error(f"Error processing directory {directory_path}: {e}")
        return None


def save_emails_to_file(emails, output_file):
    """
    Saves the extracted email addresses to a file.

    Args:
        emails (set): A set of email addresses to save.
        output_file (str): The path to the output file.
    """
    try:
        with open(output_file, 'w') as f:
            for email in emails:
                f.write(email + '\n')
        logging.info(f"Extracted emails saved to {output_file}")
    except Exception as e:
        logging.error(f"Error saving emails to file: {e}")


def main():
    """
    Main function to run the email extractor.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    source = args.source
    recursive = args.recursive
    output_file = args.output

    if source.startswith("http://") or source.startswith("https://"):
        emails = extract_emails_from_url(source)
    elif os.path.isfile(source):
        emails = extract_emails_from_file(source)
    elif os.path.isdir(source):
        emails = extract_emails_from_directory(source, recursive)
    else:
        logging.error("Invalid source provided.  Must be a URL, file, or directory.")
        sys.exit(1)

    if emails is None:
        logging.error("No emails extracted or an error occurred.")
        sys.exit(1)

    if output_file:
        save_emails_to_file(emails, output_file)
    else:
        # Results live in a set end to end, so print order and saved file
        # order change from run to run with hash randomisation. Diffing two
        # saved outputs shows churn that is not a change in findings.
        for email in emails:
            print(email)

    logging.info("Email extraction complete.")


if __name__ == "__main__":
    # Usage Examples:
    # python vscan_email_address_extractor.py https://www.example.com
    # python vscan_email_address_extractor.py my_document.txt
    # python vscan_email_address_extractor.py ./my_directory -r -o output.txt
    main()