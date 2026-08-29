from langchain.tools import tool
import requests
from dotenv import load_dotenv
import os
from tavily import TavilyClient
from rich import print
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
MAX_SCRAPED_CHARS = 6000

def _limit_scraped_content(text: str) -> str:
    text = text.strip()
    if len(text) <= MAX_SCRAPED_CHARS:
        return text
    return text[:MAX_SCRAPED_CHARS] + "\n\n[Content truncated]"

def _extract_with_tavily(url: str) -> str:
    extracted = tavily.extract(urls=[url])
    results = extracted.get("results", [])

    if results and results[0].get("raw_content"):
        return _limit_scraped_content(results[0]["raw_content"])

    return ""

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information."""

    results = tavily.search(
        query=query,
        max_results=3
    )

    out = []

    for r in results["results"]:
        out.append(
            f"Title: {r['title']}\n"
            f"URL: {r['url']}\n"
            f"Snippet: {r['content'][:150]}\n"
        )

    return "\n---\n".join(out)

@tool
def scrape_url(url: str) -> str:
    """
    Scrape and extract the main readable content from a webpage URL.
    Returns the cleaned text from the webpage.
    """

    try:
        # Send HTTP request
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                )
            }
        )

        if response.status_code == 403:
            extracted_text = _extract_with_tavily(url)
            if extracted_text:
                return extracted_text

        response.raise_for_status()

        html = response.text

        # --------------------------------
        # 1. Try Trafilatura
        # --------------------------------
        text = trafilatura.extract(
            html,
            include_links=True,
            include_tables=True,
            include_comments=False
        )

        if text:
            return _limit_scraped_content(text)

        # --------------------------------
        # 2. Fallback: Readability
        # --------------------------------
        doc = Document(html)
        clean_html = doc.summary()

        soup = BeautifulSoup(clean_html, "html.parser")

        text = soup.get_text(
            separator="\n",
            strip=True
        )

        if text:
            return _limit_scraped_content(text)

        # --------------------------------
        # 3. Final fallback: BeautifulSoup
        # --------------------------------
        soup = BeautifulSoup(html, "html.parser")

        # Remove unnecessary elements
        for element in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside"
        ]):
            element.decompose()

        text = soup.get_text(
            separator="\n",
            strip=True
        )

        return _limit_scraped_content(text)

    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}"

    except Exception as e:
        return f"Error scraping URL: {e}"