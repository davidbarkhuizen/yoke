from urllib.parse import urlencode

import httpx

from model.model import Tool, ToolTag


async def http_get_json(url) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/10.0"},
        )
        response.raise_for_status()
        return response.json()


async def search_duckduckgo(query):
    """
    Query DuckDuckGo Instant Answer API.
    Returns JSON data containing abstracts, answers, and related topics.
    """

    p = {
        "q": query,
    }

    url: str = f"https://www.searchapi.io/api/v1/search?engine=duckduckgo&{urlencode(p)}"
    response_json: dict = await http_get_json(url)  # Raise error for bad status codes

    return response_json


async def search(query: str) -> str:
    """
    search the internet using the supplied query

    Args:
        query: the search query

    Returns:
        A string containing the search result
    """

    print(query)

    response: dict = await search_duckduckgo(query)
    print(response)

    return str(response)


def new_tool() -> Tool:
    return Tool("search", search, [ToolTag.SEARCH, ToolTag.INTERNET])
