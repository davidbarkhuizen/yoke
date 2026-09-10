import os
import uuid

import httpx
from pydantic import BaseModel

from model.model import Tool, ToolTag

DEFAULT_URL: str = "http://localhost:8081"
URL_ENV_VAR: str = "YOKE_QUERY_LLM_URL"


def service_url() -> str:
    return os.environ.get(URL_ENV_VAR, DEFAULT_URL)


class QueryRequest(BaseModel):
    uuid: str
    query: str


class QueryResponse(BaseModel):
    uuid: str
    markdown: str


async def post_query(query: str) -> str:

    uuid_str: str = str(uuid.uuid4())
    rq: QueryRequest = QueryRequest(uuid=uuid_str, query=query)

    timeout = httpx.Timeout(connect=5, read=120, write=30, pool=5)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(service_url(), json=rq.model_dump())
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

    try:
        return await post_query(query)
    except httpx.HTTPError as e:
        return f"error querying LLM service at {service_url()}: {e}"


def new_tool() -> Tool:
    return Tool(query_llm, [ToolTag.QUERY, ToolTag.LLM, ToolTag.EXTERNAL])
