#!/usr/bin/env python3
"""Stdio MCP server exposing one `search` tool over a frozen fictional corpus.

Standard library only. It reads `corpus.json` beside this file once at startup and
otherwise performs no filesystem or network access. Ranking is deterministic
keyword overlap; ties keep corpus order.
"""

import json
import math
from pathlib import Path
import re
import sys

NAME = "search"
DESCRIPTION = (
    "Search the internet for current information. "
    "Returns the most relevant pages, each with its title, URL, and text."
)
SCHEMA = {
    "type": "object",
    "properties": {"query": {"type": "string", "description": "Search query."}},
    "required": ["query"],
}
LIMIT = 3
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "be",
    "can",
    "do",
    "does",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "with",
}


def stem(word):
    for suffix in ("ing", "ed", "al", "es", "s", "e"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[: -len(suffix)]
            break
    if len(word) > 3 and word[-1] == word[-2] and word[-1] not in "aeiou":
        word = word[:-1]
    return word


def terms(text):
    return {
        stem(word)
        for word in re.findall(r"[a-z0-9]+", text.lower())
        if word not in STOPWORDS
    }


def load_pages():
    data = json.loads((Path(__file__).resolve().parent / "corpus.json").read_text())
    return data["pages"]


def search(pages, query):
    """Rank by summed inverse document frequency of matching terms."""
    documents = [terms(page["title"] + " " + page["text"]) for page in pages]
    weight = {
        term: math.log(len(pages) / sum(term in document for document in documents))
        for term in terms(query)
        if any(term in document for document in documents)
    }
    scored = []
    for index, document in enumerate(documents):
        matched = [term for term in weight if term in document]
        if matched:
            score = round(sum(weight[term] for term in matched), 9)
            scored.append((-score, -len(matched), index))
    return [pages[index] for _score, _count, index in sorted(scored)[:LIMIT]]


def render(results):
    if not results:
        return "No results found."
    return "\n\n---\n\n".join(
        f"Title: {page['title']}\nURL: {page['url']}\n\n{page['text']}"
        for page in results
    )


def handle(pages, message):
    method = message.get("method")
    if method == "initialize":
        version = message.get("params", {}).get("protocolVersion", "2025-06-18")
        return {
            "protocolVersion": version,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "web", "version": "1.0.0"},
        }
    if method == "ping":
        return {}
    if method == "tools/list":
        return {
            "tools": [{"name": NAME, "description": DESCRIPTION, "inputSchema": SCHEMA}]
        }
    if method == "tools/call":
        params = message.get("params", {})
        query = params.get("arguments", {}).get("query")
        if params.get("name") != NAME or not isinstance(query, str):
            return {
                "content": [{"type": "text", "text": "Invalid request."}],
                "isError": True,
            }
        return {
            "content": [{"type": "text", "text": render(search(pages, query))}],
            "isError": False,
        }
    raise LookupError(method)


def main():
    pages = load_pages()
    for line in sys.stdin:
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "id" not in message:
            continue
        try:
            reply = {
                "jsonrpc": "2.0",
                "id": message["id"],
                "result": handle(pages, message),
            }
        except LookupError as exc:
            reply = {
                "jsonrpc": "2.0",
                "id": message["id"],
                "error": {"code": -32601, "message": f"Method not found: {exc}"},
            }
        sys.stdout.write(json.dumps(reply) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
