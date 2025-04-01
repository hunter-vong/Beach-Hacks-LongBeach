import os
import re
import PyPDF2
import docx
import ebooklib
import warnings
import contextlib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ebooklib import epub

# FastAPI app setup
# random comment
app = FastAPI()

# Helper functions (same as in your code)

def is_valid_isbn10(isbn):
    isbn = isbn.replace('-', '').replace(' ', '')
    if len(isbn) != 10 or not isbn[:-1].isdigit():
        return False
    total = sum(int(isbn[i]) * (10 - i) for i in range(9))
    check = 'X' if 11 - (total % 11) == 10 else str(11 - (total % 11))
    return isbn[-1] == check

def is_valid_isbn13(isbn):
    isbn = isbn.replace('-', '').replace(' ', '')
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    total = sum(int(isbn[i]) * (1 if i % 2 == 0 else 3) for i in range(13))
    return total % 10 == 0

def extract_isbn(text):
    isbn_pattern = re.compile(r'\b(?:ISBN(?:-1[03])?[:\s]*)?(97[89][\s-]?\d{1,5}[\s-]?\d{1,7}[\s-]?\d{1,6}[\s-]?\d|\d{9}[\dX])\b')
    return [isbn.replace('-', '').replace(' ', '') for isbn in isbn_pattern.findall(text)
            if is_valid_isbn10(isbn) or is_valid_isbn13(isbn)]

def read_file(file_path, mode='r', is_binary=False):
    try:
        with open(file_path, 'rb' if is_binary else 'r', errors='ignore') as f:
            return f.read()
    except (FileNotFoundError, IOError) as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def read_pdf_file(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as f:
            with warnings.catch_warnings(), open(os.devnull, 'w') as fnull, contextlib.redirect_stderr(fnull):
                warnings.simplefilter("ignore", category=UserWarning)
                reader = PyPDF2.PdfReader(f)
                text = '\n'.join(page.extract_text() or '' for page in reader.pages)
    except (FileNotFoundError, PyPDF2.errors.PdfReadError) as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text

def read_docx_file(file_path):
    try:
        doc = docx.Document(file_path)
        return '\n'.join(para.text for para in doc.paragraphs)
    except (FileNotFoundError, docx.opc.exceptions.PackageNotFoundError) as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return ""

def read_epub_file(file_path):
    text = ""
    try:
        book = epub.read_epub(file_path)
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                text += item.get_body_content().decode('utf-8', errors='ignore') + '\n'
    except (FileNotFoundError, ebooklib.epub.EpubException) as e:
        print(f"Error reading EPUB {file_path}: {e}")
    return text

def extract_isbns_from_file(file_path):
    file_extension = file_path.lower().split('.')[-1]
    text_extractors = {
        'txt': lambda path: read_file(path),
        'pdf': read_pdf_file,
        'docx': read_docx_file,
        'epub': read_epub_file
    }
    return extract_isbn(text_extractors.get(file_extension, lambda _: "")(file_path))

def scan_directory_for_isbns(directory_path):
    all_isbns = set()
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"Processing: {file_path}")
            all_isbns.update(extract_isbns_from_file(file_path))
    return all_isbns

# API Models
class FilePathRequest(BaseModel):
    directory_path: str

# API Endpoint for scanning ISBNS
@app.post("/scan_isbns/")
async def scan_isbns(request: FilePathRequest):
    directory_path = request.directory_path.strip()
    if not os.path.exists(directory_path):
        raise HTTPException(status_code=400, detail="Invalid folder path")

    found_isbns = scan_directory_for_isbns(directory_path)
    if found_isbns:
        return {"isbns": list(found_isbns)}
    else:
        return {"error": "No valid ISBNs found"}

import requests

def get_book_info(isbn):
    # Construct the API URL with the provided ISBN code
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    
    # Send the request to the Google Books API
    response = requests.get(url)
    
    # If the request is successful (status code 200)
    if response.status_code == 200:
        data = response.json()
        
        # Check if any book data was found
        if 'items' in data:
            book = data['items'][0]
            title = book['volumeInfo'].get('title', 'No title available')
            authors = ', '.join(book['volumeInfo'].get('authors', ['No authors available']))
            published_date = book['volumeInfo'].get('publishedDate', 'No published date available')
            description = book['volumeInfo'].get('description', 'No description available')
            
            # Display the book details
            print("\nBook Information:")
            print(f"Title: {title}")
            print(f"Authors: {authors}")
            print(f"Published Date: {published_date}")
            print(f"Description: {description}")
        else:
            print("No book found for the provided ISBN.")
    else:
        print("Failed to retrieve data. Please try again later.")

def main():
    # Get ISBN input from the user
    isbn = input("Enter the ISBN code: ").strip()
    
    # Fetch and display book info
    get_book_info(isbn)

if __name__ == "__main__":
    main()