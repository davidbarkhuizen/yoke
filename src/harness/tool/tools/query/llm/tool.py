import uuid

import httpx
from pydantic import BaseModel

from model.model import Tool, ToolTag

URL: str = "http://localhost:8081"


class QueryRequest(BaseModel):
    uuid: str
    query: str


class QueryResponse(BaseModel):
    uuid: str
    markdown: str


async def query_external_brave_llm(query: str) -> str:

    uuid_str: str = str(uuid.uuid4())
    rq: QueryRequest = QueryRequest(uuid=uuid_str, query=query)

    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=1, read=100, write=1, pool=None)) as client:
        response = await client.post(URL, json=rq.model_dump())
        response.raise_for_status()
        query_rsp = QueryResponse.model_validate_json(response.text)
        return query_rsp.markdown


async def query_llm(query: str) -> str:
    """
    query LLM using the supplied query string

    Args:
        query: the query

    Returns:
        A string containing the query response, in markdown format
    """

    query_rsp_markdown: str = await query_external_brave_llm(query)
    return query_rsp_markdown


def new_tool() -> Tool:
    return Tool(query_llm, [ToolTag.QUERY, ToolTag.LLM, ToolTag.EXTERNAL])
