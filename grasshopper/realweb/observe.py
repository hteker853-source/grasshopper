"""Compact page observation: DOM summary plus an accessibility-style element list."""

from __future__ import annotations

import re
import warnings
from urllib.parse import urljoin

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

_MONEY = re.compile(r"([0-9]+(?:\.[0-9]+)?)")
_TOTAL = re.compile(r"total\s*:?\s*\$[0-9]+(?:\.[0-9]{2})?", re.I)


def observe(html: str, url: str) -> dict:
    soup = BeautifulSoup(html or "", "html.parser")
    text = soup.get_text("\n", strip=True)
    books = []
    for pod in soup.select("article.product_pod"):
        link = pod.select_one("h3 a")
        price_node = pod.select_one("p.price_color")
        rating_node = pod.select_one("p.star-rating")
        rating = ""
        if rating_node is not None:
            for name in ("One", "Two", "Three", "Four", "Five"):
                if name in (rating_node.get("class") or []):
                    rating = name
        href = urljoin(url, link.get("href")) if link is not None and link.get("href") else ""
        title = ""
        if link is not None:
            title = link.get("title") or link.get_text(" ", strip=True)
        books.append({
            "title": title,
            "price": _price(price_node.get_text(" ", strip=True) if price_node else ""),
            "rating": rating,
            "href": href,
        })
    next_node = soup.select_one("li.next a")
    next_url = urljoin(url, next_node.get("href")) if next_node is not None and next_node.get("href") else ""
    hn = []
    for anchor in soup.select("span.titleline > a"):
        hn.append({"title": anchor.get_text(" ", strip=True), "href": anchor.get("href") or ""})
    papers = []
    for entry in soup.find_all("entry"):
        title_node = entry.find("title")
        names = []
        for author in entry.find_all("author"):
            name = author.find("name")
            if name is not None:
                names.append(name.get_text(" ", strip=True))
        title = title_node.get_text(" ", strip=True) if title_node else ""
        if title:
            papers.append({"title": title, "authors": ", ".join(names), "href": ""})
    for item in soup.select("li.arxiv-result"):
        title_node = item.select_one("p.title")
        author_node = item.select_one("p.authors")
        link = item.select_one("p.list-title a") or item.select_one("a")
        papers.append({
            "title": title_node.get_text(" ", strip=True) if title_node else "",
            "authors": author_node.get_text(" ", strip=True) if author_node else "",
            "href": urljoin(url, link.get("href")) if link is not None and link.get("href") else "",
        })
    paragraph = ""
    content = soup.select_one("#mw-content-text")
    if content is not None:
        for node in content.select("p"):
            snippet = node.get_text(" ", strip=True)
            if len(snippet) >= 80:
                paragraph = snippet
                break
    if not paragraph:
        wiki_p = soup.select_one("#wiki-p")
        if wiki_p is not None:
            paragraph = wiki_p.get_text(" ", strip=True)
    wiki_results = []
    for anchor in soup.select(".mw-search-result-heading a, a.wiki-result"):
        wiki_results.append({
            "title": anchor.get_text(" ", strip=True),
            "href": urljoin(url, anchor.get("href") or ""),
        })
    selected = {}
    for menu in soup.select("select"):
        chosen = menu.find("option", selected=True)
        if chosen is None:
            continue
        key = "#" + menu["id"] if menu.get("id") else "select"
        selected[key] = (chosen.get("value") or chosen.get_text(" ", strip=True) or "").strip()
    elements = []
    for tag in soup.select("a, button, input, select"):
        if len(elements) >= 40:
            break
        elements.append({
            "selector": _selector(tag),
            "tag": tag.name,
            "text": tag.get_text(" ", strip=True)[:80],
            "type": (tag.get("type") or "").lower(),
        })
    total_line = ""
    match = _TOTAL.search(text)
    if match:
        total_line = match.group(0)
    return {
        "url": url,
        "title": soup.title.get_text(" ", strip=True) if soup.title else "",
        "text": text[:4000],
        "books": books,
        "next_url": next_url,
        "hn": hn[:5],
        "papers": [paper for paper in papers if paper["title"]][:5],
        "wiki_paragraph": paragraph[:600],
        "wiki_results": wiki_results[:3],
        "selected": selected,
        "elements": elements,
        "total_line": total_line,
    }


def _price(raw: str) -> float:
    match = _MONEY.search(raw.replace(",", ""))
    return float(match.group(1)) if match else 0.0


def _selector(tag) -> str:
    if tag.get("id"):
        return "#" + tag["id"]
    classes = [item for item in (tag.get("class") or []) if item]
    if classes:
        return tag.name + "." + ".".join(classes[:2])
    if tag.get("name"):
        return f"{tag.name}[name={tag['name']}]"
    text = tag.get_text(" ", strip=True)[:40]
    if text:
        return "text=" + text
    return tag.name
