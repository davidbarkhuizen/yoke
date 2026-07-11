from urllib.parse import urlencode

import httpx

from model.model import Tool, ToolTag

USER_AGENT: str = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)


async def http_get_json(url, user_agent: str = USER_AGENT) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={"user-agent": user_agent},
        )
        response.raise_for_status()
        return response.json()


async def search_duckduckgo(query):
    """
    Query DuckDuckGo Instant Answer API.
    Returns JSON data containing abstracts, answers, and related topics.
    """

    p = {"q": query, "format": "json"}
    url: str = f"https://api.duckduckgo.com/?{urlencode(p)}"
    print(url)
    response_json: dict = await http_get_json(url)
    print(response_json)

    return response_json


async def search_internet(query: str) -> str:
    """
    search the internet using the supplied query

    Args:
        query: the search query

    Returns:
        A string containing the search result
    """

    # raise NotImplementedError(query)
    response: dict = await search_duckduckgo(query)

    return str(response)


def new_tool() -> Tool:
    return Tool(search_internet, [ToolTag.SEARCH, ToolTag.INTERNET])
