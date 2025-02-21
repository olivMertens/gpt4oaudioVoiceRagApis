import re, httpx, os
from typing import Any
import logging
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from dotenv import load_dotenv
from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("toolingCall")

if not os.environ.get("RUNNING_IN_PRODUCTION"):
    logger.info("Running in development mode, loading from .env file")
    load_dotenv()
else:
    logger.info("Running in production mode")


AZURE_API_ENDPOINT = os.environ.get("AZURE_API_ENDPOINT")

_search_tool_schema = {
    "type": "function",
    "name": "search",
    "description": "Search the knowledge base. The knowledge base is in English, translate to and from English if " + \
                   "needed. Results are formatted as a source name first in square brackets, followed by the text " + \
                   "content, and a line with '-----' at the end of each result.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }
}

_grounding_tool_schema = {
    "type": "function",
    "name": "report_grounding",
    "description": "Report use of a source from the knowledge base as part of an answer (effectively, cite the source). Sources " + \
                   "appear in square brackets before each knowledge base passage. Always use this tool to cite sources when responding " + \
                   "with information from the knowledge base.",
    "parameters": {
        "type": "object",
        "properties": {
            "sources": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of source names from last statement actually used, do not include the ones not used to formulate a response"
            }
        },
        "required": ["sources"],
        "additionalProperties": False
    }
}

_incident_tool_schema = {
    "type": "function",
    "name": "incident",
    "description": "Retrieve incident information for orange pro customer by the id of the incident or the name of the person",
    "parameters": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "incident ID"
            },
            "name": {
                "type": "string",
                "description": "Name of the person"
            }
        },
        "required": [],
        "additionalProperties": False
    }
}


_friendly_tool_schema = {
    'type': 'function',
    'name': 'friendly',
    "description": 'Friendly tool to add some nice joke and say something nice about Alexandra',
    'parameters': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'The name of the person to greet'
            }
        },
        'required': ['name'],
        "additionalProperties": False
    }
}

async def _search_tool(
    search_client: SearchClient, 
    semantic_configuration: str,
    identifier_field: str,
    content_field: str,
    embedding_field: str,
    use_vector_query: bool,
    args: Any) -> ToolResult:
    print(f"Searching for '{args['query']}' in the knowledge base.")
    # Hybrid + Reranking query using Azure AI Search
    vector_queries = []
    if use_vector_query:
        vector_queries.append(VectorizableTextQuery(text=args['query'], k_nearest_neighbors=50, fields=embedding_field))
    search_results = await search_client.search(
        search_text=args['query'], 
        query_type="semantic",
        semantic_configuration_name=semantic_configuration,
        top=5,
        vector_queries=vector_queries,
        select=", ".join([identifier_field, content_field])
    )
    result = ""
    async for r in search_results:
        result += f"[{r[identifier_field]}]: {r[content_field]}\n-----\n"
    return ToolResult(result, ToolResultDirection.TO_SERVER)

KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_=\-]+$')

# TODO: move from sending all chunks used for grounding eagerly to only sending links to 
# the original content in storage, it'll be more efficient overall
async def _report_grounding_tool(search_client: SearchClient, identifier_field: str, title_field: str, content_field: str, args: Any) -> None:
    sources = [s for s in args["sources"] if KEY_PATTERN.match(s)]
    list = " OR ".join(sources)
    print(f"Grounding source: {list}")
    # Use search instead of filter to align with how detailt integrated vectorization indexes
    # are generated, where chunk_id is searchable with a keyword tokenizer, not filterable 
    search_results = await search_client.search(search_text=list, 
                                                search_fields=[identifier_field], 
                                                select=[identifier_field, title_field, content_field], 
                                                top=len(sources), 
                                                query_type="full")
    
    # If your index has a key field that's filterable but not searchable and with the keyword analyzer, you can 
    # use a filter instead (and you can remove the regex check above, just ensure you escape single quotes)
    # search_results = await search_client.search(filter=f"search.in(chunk_id, '{list}')", select=["chunk_id", "title", "chunk"])

    docs = []
    async for r in search_results:
        docs.append({"chunk_id": r[identifier_field], "title": r[title_field], "chunk": r[content_field]})
    return ToolResult({"sources": docs}, ToolResultDirection.TO_CLIENT)

async def _incident_tool(args: Any) -> ToolResult:
    print(f"Retrieving incident for customer '{args.get('id')}' and name '{args.get('name')}'.")
    async with httpx.AsyncClient() as client:
        response = await client.get(AZURE_API_ENDPOINT+"/api/incidents", params=args)
        response.raise_for_status()
        incidents = response.json()
    return ToolResult({"incidents": incidents}, ToolResultDirection.TO_SERVER)

async def _friendly_tool(args: Any) -> ToolResult:
    print(f"Friendly tool called with name '{args.get('name')}'.")
    async with httpx.AsyncClient() as client:
        response = await client.get("https://official-joke-api.appspot.com/jokes/general/random")
        response.raise_for_status()
        jokes = response.json()
        if jokes and isinstance(jokes, list):
            joke = jokes[0]
            joke_message = f"{joke.get('setup')} ... {joke.get('punchline')}"
        else:
            joke_message = "No joke found."
    message = f"{args.get('name')}! Alexandra is doing great, thank you for asking! Here's a joke for you: {joke_message}"
    return ToolResult({"message": message}, ToolResultDirection.TO_SERVER)


def attach_rag_tools(rtmt: RTMiddleTier,
    credentials: AzureKeyCredential | DefaultAzureCredential,
    search_endpoint: str, search_index: str,
    semantic_configuration: str,
    identifier_field: str,
    content_field: str,
    embedding_field: str,
    title_field: str,
    use_vector_query: bool
    ) -> None:
    if not isinstance(credentials, AzureKeyCredential):
        credentials.get_token("https://search.azure.com/.default") # warm this up before we start getting requests
    search_client = SearchClient(search_endpoint, search_index, credentials, user_agent="RTMiddleTier")
    logger.info("Attaching Rag tool")
    rtmt.tools["search"] = Tool(schema=_search_tool_schema, target=lambda args: _search_tool(search_client, semantic_configuration, identifier_field, content_field, embedding_field, use_vector_query, args))
    rtmt.tools["report_grounding"] = Tool(schema=_grounding_tool_schema, target=lambda args: _report_grounding_tool(search_client, identifier_field, title_field, content_field, args))
    logging.info("Attaching friendly tool")
    rtmt.tools["friendly"] = Tool(schema=_friendly_tool_schema, target=lambda args: _friendly_tool(args))
    logger.info("Attaching incidents tool")
    rtmt.tools["incident"] = Tool(schema=_incident_tool_schema, target=lambda args: _incident_tool(args))
