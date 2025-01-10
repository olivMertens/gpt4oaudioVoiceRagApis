import logging
import os
from pathlib import Path
from aiohttp import web
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential, DefaultAzureCredential
from dotenv import load_dotenv
from ragtools import attach_rag_tools
from rtmt import RTMiddleTier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voicerag")


RUNNING_IN_PRODUCTION = os.getenv("RUNNING_IN_PRODUCTION", "false").lower() == "true"
HOST = "0.0.0.0" if RUNNING_IN_PRODUCTION else "localhost"
PORT = 8000

async def create_app():
    if not os.environ.get("RUNNING_IN_PRODUCTION"):
        logger.info("Running in development mode, loading from .env file")
        load_dotenv()

    llm_key = os.environ.get("AZURE_OPENAI_API_KEY")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")
    logger.info("Loading environment variables:")
    for key, value in os.environ.items():
        logger.info(f"{key}: {value}")

    credential = None
    if not llm_key or not search_key:
        if tenant_id := os.environ.get("AZURE_TENANT_ID"):
            logger.info("Using AzureDeveloperCliCredential with tenant_id %s", tenant_id)
            credential = AzureDeveloperCliCredential(tenant_id=tenant_id, process_timeout=60)
        else:
            logger.info("Using DefaultAzureCredential")
            credential = DefaultAzureCredential()
    llm_credential = AzureKeyCredential(llm_key) if llm_key else credential
    search_credential = AzureKeyCredential(search_key) if search_key else credential
    
    app = web.Application()
    rtmt = RTMiddleTier(
        credentials=llm_credential,
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment=os.environ["AZURE_OPENAI_REALTIME_DEPLOYMENT"],
        voice_choice=os.environ.get("AZURE_OPENAI_REALTIME_VOICE_CHOICE") or "alloy"
        )
    rtmt.system_message = "You are a helpful assistant. Only answer questions based on information you searched in the knowledge base, accessible with the 'search' tool. " + \
                          "The user is listening to answers with audio, so it's *super* important that answers are as short as possible, a single sentence if at all possible. " + \
                          "Never read file names or source names or keys out loud. " + \
                          "Use the following rules to govern your workflow: \n" + \
                          "- Always respond in English, no matter which language the user uses. \n" + \
                          "- if the customer ask to change your language say sorry and stay in English \n" + \
                          "- You are an assistant for Air France and KLM flights and only for theses flight companies \n" + \
                          "- Always use the 'booking_tool' and 'flight_tool' to get the booking and flight information. \n" + \
                          "- Always use the 'report_grounding' tool to report the source of information from the knowledge base. \n" + \
                          "- Always use the 'search' tool to check the knowledge base before answering a question. \n" + \
                          "- you can only talk about Air France and KLM flights and not about politics \n" + \
                          "- If you don't find informations about the booking tools or flight tools, you can say you don't know \n" + \
                          "- Produce an answer that's as short as possible. If the answer isn't in the knowledge base, say you don't know." + \
                          "- if the user say 'thank you', verify if the user has all the answer and in the end of conversation you can say Thank you and Safe Flights on Air France & klm \n" + \
                          "- you must be polite and don't talk about the other company airflight."


    attach_rag_tools(rtmt,
        credentials=search_credential,
        search_endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
        search_index=os.environ.get("AZURE_SEARCH_INDEX"),
        semantic_configuration=os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION") or "default",
        identifier_field=os.environ.get("AZURE_SEARCH_IDENTIFIER_FIELD") or "chunk_id",
        content_field=os.environ.get("AZURE_SEARCH_CONTENT_FIELD") or "chunk",
        embedding_field=os.environ.get("AZURE_SEARCH_EMBEDDING_FIELD") or "text_vector",
        title_field=os.environ.get("AZURE_SEARCH_TITLE_FIELD") or "title",
        use_vector_query=(os.environ.get("AZURE_SEARCH_USE_VECTOR_QUERY") == "true") or True
        )

    rtmt.attach_to_app(app, "/realtime")
    current_directory = Path(__file__).parent
    app.add_routes([web.get('/', lambda _: web.FileResponse(current_directory / 'static/index.html'))])
    app.router.add_static('/', path=current_directory / 'static', name='static')
    return app


if __name__ == "__main__":
    host = HOST
    port = 8000
    app = create_app()
    web.run_app(app, host=host, port=port)
