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

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns Titles, URLs and Content"""
    results = tavily.search(query=query,max_results=5)

    out = []

    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
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
            return text.strip()

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
            return text

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

        return text

    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}"

    except Exception as e:
        return f"Error scraping URL: {e}"