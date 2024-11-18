import json
import logging
import os
import subprocess

from azure.core.exceptions import ResourceExistsError
from azure.identity import AzureDeveloperCliCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    AzureOpenAIParameters,
    AzureOpenAIVectorizer,
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
)
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from rich.logging import RichHandler
from openai import AzureOpenAI
import uuid
import json


def load_azd_env():
    """Get path to current azd env file and load file using python-dotenv"""
    result = subprocess.run("azd env list -o json", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("Error loading azd env")
    env_json = json.loads(result.stdout)
    env_file_path = None
    for entry in env_json:
        if entry["IsDefault"]:
            env_file_path = entry["DotEnvPath"]
    if not env_file_path:
        raise Exception("No default azd env file found")
    logger.info(f"Loading azd env from {env_file_path}")
    load_dotenv(env_file_path, override=True)


def setup_index(azure_credential, index_name, azure_search_endpoint, azure_storage_connection_string, azure_storage_container, azure_openai_embedding_endpoint, azure_openai_embedding_deployment, azure_openai_embedding_model, azure_openai_embeddings_dimensions):
    index_client = SearchIndexClient(azure_search_endpoint, azure_credential)

    index_names = [index.name for index in index_client.list_indexes()]
    if index_name in index_names:
        logger.info(f"Index {index_name} already exists, not re-creating")
    else:
        logger.info(f"Creating index: {index_name}")
        index_client.create_index(
            SearchIndex(
                name=index_name,
                fields=[
                    SearchableField(name="chunk_id", key=True, analyzer_name="keyword", sortable=True),
                    SimpleField(name="category", type=SearchFieldDataType.String, filterable=True),
                    SearchableField(name="title"),
                    SearchableField(name="chunk"),
                    SearchField(
                        name="text_vector", 
                        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        vector_search_dimensions=EMBEDDINGS_DIMENSIONS,
                        vector_search_profile_name="vp",
                        stored=True,
                        hidden=False)
                ],
                vector_search=VectorSearch(
                    algorithms=[
                        HnswAlgorithmConfiguration(name="algo", parameters=HnswParameters(metric=VectorSearchAlgorithmMetric.COSINE))
                    ],
                    vectorizers=[
                        AzureOpenAIVectorizer(
                            name="openai_vectorizer",
                            azure_open_ai_parameters=AzureOpenAIParameters(
                                resource_uri=azure_openai_embedding_endpoint,
                                deployment_id=azure_openai_embedding_deployment,
                                model_name=azure_openai_embedding_model
                            )
                        )
                    ],
                    profiles=[
                        VectorSearchProfile(name="vp", algorithm_configuration_name="algo", vectorizer="openai_vectorizer")
                    ]
                ),
                semantic_search=SemanticSearch(
                    configurations=[
                        SemanticConfiguration(
                            name="default",
                            prioritized_fields=SemanticPrioritizedFields(title_field=SemanticField(field_name="title"), content_fields=[SemanticField(field_name="chunk")])
                        )
                    ],
                    default_configuration_name="default"
                )
            )
        )

def upload_documents(azure_credential, index_name, azure_search_endpoint, azure_openai_embedding_endpoint, azure_openai_embedding_deployment):
    search_client = SearchClient(endpoint=azure_search_endpoint, index_name=index_name, credential=azure_credential)
    openai_client = AzureOpenAI(
        azure_endpoint=azure_openai_embedding_endpoint,
        azure_deployment=azure_openai_embedding_deployment,
        azure_ad_token_provider=get_bearer_token_provider(azure_credential, "https://cognitiveservices.azure.com/.default"),
        api_version="2023-05-15"
    )

    def generate_embeddings(text):
        response = openai_client.embeddings.create(
            input=text,
            model=azure_openai_embedding_deployment,
        )
        return response.data[0].embedding

    with open("data/faq.json", "r") as file:
        faq = json.load(file)
        faq_documents = []

        for i, item in enumerate(faq):
            faq_documents.append({
                "chunk_id": str(uuid.uuid4()),
                "category": item["category"],
                "title": item["title"],
                "chunk": item["chunk"],
                "text_vector": generate_embeddings(item["chunk"])
            })
        
        search_client.upload_documents(faq_documents)
        logger.info(f'Uploaded {len(faq_documents)} documents to Azure AI Search index {index_name}')



if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)])
    logger = logging.getLogger("voicerag")
    logger.setLevel(logging.INFO)

    logger = logging.getLogger("voicerag")

    load_azd_env()

    logger.info("Checking if we need to set up Azure AI Search index...")
    if os.environ.get("AZURE_SEARCH_REUSE_EXISTING") == "true":
        logger.info("Since an existing Azure AI Search index is being used, no changes will be made to the index.")
        exit()
    else:
        logger.info("Setting up Azure AI Search index and integrated vectorization...")

    # Used to name index, indexer, data source and skillset
    AZURE_SEARCH_INDEX = os.environ["AZURE_SEARCH_INDEX"]
    AZURE_OPENAI_EMBEDDING_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
    AZURE_OPENAI_EMBEDDING_MODEL = os.environ["AZURE_OPENAI_EMBEDDING_MODEL"]
    EMBEDDINGS_DIMENSIONS = 3072
    AZURE_SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
    AZURE_STORAGE_ENDPOINT = os.environ["AZURE_STORAGE_ENDPOINT"]
    AZURE_STORAGE_CONNECTION_STRING = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    AZURE_STORAGE_CONTAINER = os.environ["AZURE_STORAGE_CONTAINER"]

    azure_credential = AzureDeveloperCliCredential(tenant_id=os.environ["AZURE_TENANT_ID"], process_timeout=60)

    setup_index(azure_credential,
        index_name=AZURE_SEARCH_INDEX, 
        azure_search_endpoint=AZURE_SEARCH_ENDPOINT,
        azure_storage_connection_string=AZURE_STORAGE_CONNECTION_STRING,
        azure_storage_container=AZURE_STORAGE_CONTAINER,
        azure_openai_embedding_endpoint=AZURE_OPENAI_EMBEDDING_ENDPOINT,
        azure_openai_embedding_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        azure_openai_embedding_model=AZURE_OPENAI_EMBEDDING_MODEL,
        azure_openai_embeddings_dimensions=EMBEDDINGS_DIMENSIONS)

    upload_documents(azure_credential,
        index_name=AZURE_SEARCH_INDEX,
        azure_search_endpoint=AZURE_SEARCH_ENDPOINT,
        azure_openai_embedding_endpoint=AZURE_OPENAI_EMBEDDING_ENDPOINT,
        azure_openai_embedding_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT)