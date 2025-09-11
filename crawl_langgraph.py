#!/usr/bin/env python3
"""
crawl_langgraph.py
Crawl all internal pages under the base docs site, extract main text, chunk it,
and write to:
  - docs_raw/<path>.md   (mirror of pages as markdown)
  - output/langgraph.jsonl  (chunks with metadata, suitable for embeddings or RAG)
"""
import os
import json
import time
import urllib.parse
from collections import deque

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from tenacity import retry, wait_exponential, stop_after_attempt
from tqdm import tqdm
from requests.exceptions import HTTPError, RequestException

BASE = "https://langchain-ai.github.io/langgraph/"
OUT_DIR = "docs_raw"
JSONL_OUT = "output/langgraph.jsonl"
HEADERS = {"User-Agent": "langgraph-crawler/1.0 (+https://example.com)"}
MAX_PAGES = 1000  # safety cap

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(JSONL_OUT), exist_ok=True)

@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
def get(url):
    """
    Fetch URL and return tuple (text, content_type, status_code, headers)
    Raises HTTPError for non-200 responses so retry applies.
    """
    r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
    # If status is not OK, raise to trigger retry (tenacity)
    try:
        r.raise_for_status()
    except HTTPError as e:
        # re-raise so tenacity can retry
        raise

    content_type = r.headers.get("Content-Type", "")
    return r.text, content_type, r.status_code, r.headers

# --- In your crawl() main loop, replace the try/except block with this more informative version ---
def crawl():
    visited = set()
    q = deque([BASE])
    pages = 0
    failed = []
    with open(JSONL_OUT, "w", encoding="utf-8") as out:
        while q and pages < MAX_PAGES:
            url = q.popleft()
            if url in visited:
                continue
            print("Fetching:", url)               # live feedback
            try:
                html, content_type, status, headers = get(url)
            except RequestException as e:
                print("Failed to fetch", url, type(e), str(e))
                failed.append({"url": url, "error": str(e)})
                visited.add(url)
                continue

            # Skip non-HTML content
            if not content_type or "html" not in content_type.lower():
                print(f"Skipping non-HTML content: {url} (Content-Type: {content_type})")
                visited.add(url)
                continue

            visited.add(url)
            pages += 1

            title, markdown = extract_text(html, url)
            # save markdown mirror
            file_path = save_page_as_md(url.replace(BASE, "/"), f"# {title}\n\n{markdown}\n\n[Source]({url})\n")
            # chunk
            chunks = chunk_text(markdown, max_words=250)
            for i, chunk in enumerate(chunks):
                doc = {
                    "id": f"{url}#chunk-{i}",
                    "source": url,
                    "path": file_path,
                    "title": title,
                    "text": chunk
                }
                out.write(json.dumps(doc, ensure_ascii=False) + "\n")
            # find internal links
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if href.startswith("mailto:") or href.startswith("#") or href.startswith("tel:"):
                    continue
                joined = urllib.parse.urljoin(url, href)
                parsed = urllib.parse.urlparse(joined)
                normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if is_internal(normalized) and normalized not in visited:
                    q.append(normalized)
            # polite pause
            time.sleep(0.2)

    # write failures for debugging
    if failed:
        os.makedirs(os.path.dirname(JSONL_OUT), exist_ok=True)
        with open("output/failed_urls.txt", "w", encoding="utf-8") as f:
            for item in failed:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Done. Crawled {len(visited)} pages. JSONL written to {JSONL_OUT}. Markdown mirror in {OUT_DIR}/")
    if failed:
        print(f"{len(failed)} URLs failed. See output/failed_urls.txt")

def is_internal(url):
    parsed = urllib.parse.urljoin(BASE, url)
    return parsed.startswith(BASE)

def extract_text(html, url):
    soup = BeautifulSoup(html, "html.parser")
    # Try common main/article tags
    main = soup.find("main") or soup.find("article") or soup.body
    # Remove nav, footer, script, style
    for tag in main.find_all(["nav","footer","script","style","aside", "form"]):
        tag.decompose()
    # If mkdocs uses divs with .md-content etc, capture them as well
    text_html = str(main)
    markdown = md(text_html, heading_style="ATX")
    # Simple cleanup
    markdown = "\n".join(line.rstrip() for line in markdown.splitlines() if line.strip())
    title = soup.title.string.strip() if soup.title else url
    return title, markdown

def chunk_text(text, max_words=250):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk_words = words[i:i+max_words]
        chunks.append(" ".join(chunk_words))
    return chunks

def save_page_as_md(path_url, markdown):
    # create filesystem safe path
    parsed = urllib.parse.urlparse(path_url)
    path = parsed.path
    if path.endswith("/"):
        path = path + "index.md"
    if path == "" or path == "/":
        path = "/index.md"
    file_path = os.path.join(OUT_DIR, path.lstrip("/"))
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    return file_path

def crawl():
    visited = set()
    q = deque([BASE])
    pages = 0
    with open(JSONL_OUT, "w", encoding="utf-8") as out:
        while q and pages < MAX_PAGES:
            url = q.popleft()
            if url in visited:
                continue
            try:
                html = get(url)
            except Exception as e:
                print("Failed to fetch", url, e)
                continue
            visited.add(url)
            pages += 1
            title, markdown = extract_text(html, url)
            # save markdown mirror
            file_path = save_page_as_md(url.replace(BASE, "/"), f"# {title}\n\n{markdown}\n\n[Source]({url})\n")
            # chunk
            chunks = chunk_text(markdown, max_words=250)
            for i, chunk in enumerate(chunks):
                doc = {
                    "id": f"{url}#chunk-{i}",
                    "source": url,
                    "path": file_path,
                    "title": title,
                    "text": chunk
                }
                out.write(json.dumps(doc, ensure_ascii=False) + "\n")
            # find internal links
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if href.startswith("mailto:") or href.startswith("#") or href.startswith("tel:"):
                    continue
                joined = urllib.parse.urljoin(url, href)
                # normalize remove query/fragment for crawling
                parsed = urllib.parse.urlparse(joined)
                normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if is_internal(normalized) and normalized not in visited:
                    q.append(normalized)
            # polite pause
            time.sleep(0.2)
    print(f"Done. Crawled {len(visited)} pages. JSONL written to {JSONL_OUT}. Markdown mirror in {OUT_DIR}/")

if __name__ == "__main__":
    crawl()
