import os
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
)

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

from flask import request
from config import *

app = Flask(__name__)


'''
endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
credential = AzureKeyCredential(os.environ["AZURE_SEARCH_ADMIN_KEY"]) if len(os.environ["AZURE_SEARCH_ADMIN_KEY"]) > 0 else DefaultAzureCredential()
# index_name = os.environ["AZURE_SEARCH_INDEX"]
azure_openai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
# Llama Index does not support RBAC authentication, an API key is required
azure_openai_key = os.environ["AZURE_OPENAI_KEY"]
if len(azure_openai_key) == 0:
    raise Exception("API key required")
azure_openai_embedding_model = os.environ["AZURE_OPENAI_EMBEDDING_MODEL"]
azure_openai_embedding_deployment = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
azure_openai_chatgpt_deployment = os.environ["AZURE_OPENAI_CHATGPT_DEPLOYMENT"]
azure_openai_api_version = os.environ["AZURE_OPENAI_API_VERSION"]
# embedding_dimensions = int(os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", 1536))
'''

endpoint = AZURE_SEARCH_SERVICE_ENDPOINT
credential = AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY) if len(AZURE_SEARCH_ADMIN_KEY) > 0 else DefaultAzureCredential()
azure_openai_endpoint = AZURE_OPENAI_ENDPOINT
azure_openai_key = AZURE_OPENAI_KEY
azure_openai_embedding_model = AZURE_OPENAI_EMBEDDING_MODEL
azure_openai_embedding_deployment = AZURE_OPENAI_EMBEDDING_DEPLOYMENT
azure_openai_chatgpt_deployment = AZURE_OPENAI_CHATGPT_DEPLOYMENT
azure_openai_api_version = AZURE_OPENAI_API_VERSION

index = None

def initialize_index():
    global index
    from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
    embeddings = AzureOpenAIEmbedding(
        model_name=azure_openai_embedding_model,
        deployment_name=azure_openai_embedding_deployment,
        api_version=azure_openai_api_version,
        azure_endpoint=azure_openai_endpoint,
        api_key=azure_openai_key
    )
    
    from llama_index.llms.azure_openai import AzureOpenAI
    llm = AzureOpenAI(
        deployment_name=azure_openai_chatgpt_deployment,
        api_version=azure_openai_api_version,
        azure_endpoint=azure_openai_endpoint,
        api_key=azure_openai_key
    )
    
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents import SearchClient
    # Index name to use
    index_name = "llamaindex-vector-test-blog"

    # Use index client to demonstrate creating an index
    index_client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=credential,
    )
    
    from llama_index.vector_stores.azureaisearch import AzureAISearchVectorStore
    from llama_index.vector_stores.azureaisearch import (
        IndexManagement,
        MetadataIndexFieldType,
    )

    metadata_fields = {

    }

    vector_store = AzureAISearchVectorStore(
        search_or_index_client=index_client,
        filterable_metadata_field_keys=metadata_fields,
        # index_name=index_name,
        index_management=IndexManagement.VALIDATE_INDEX,
        id_field_key="id",
        chunk_field_key="chunk",
        embedding_field_key="embedding",
        embedding_dimensionality=1536,
        metadata_string_field_key="metadata",
        doc_id_field_key="doc_id",
    )
    

    from llama_index.core import (
        SimpleDirectoryReader,
        StorageContext,
        VectorStoreIndex,
        load_index_from_storage,
    )
    from llama_index.core.settings import Settings

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    Settings.llm = llm
    Settings.embed_model = embeddings

    index = VectorStoreIndex.from_documents(
        [],
        storage_context=storage_context,
    )
    print("Index Initialized")
    
@app.route("/query", methods=["GET"])
def query_index():
    global index
    query_text = request.args.get("text", None)
    if query_text is None:
        return (
            "No text found, please include a ?text=blah parameter in the URL",
            400,
        )
    
    blog_query_engine = index.as_query_engine()
    
    from llama_index.core.query_engine import SubQuestionQueryEngine
    from llama_index.core.tools import QueryEngineTool, ToolMetadata

    import pandas as pd
    from bs4 import BeautifulSoup
    from llama_index.experimental.query_engine import PandasQueryEngine

    # url = 'https://www.espn.com/nhl/player/_/id/2563060'
    url = 'https://www.espncricinfo.com/records/most-runs-in-career-223646'
    tables = pd.read_html(url)
    df = tables[0]
    
    df_query_engine = PandasQueryEngine(df=df, verbose=True)
    
    from llama_index.core.tools import QueryEngineTool


    blog_tool = QueryEngineTool.from_defaults(
        query_engine=blog_query_engine,
        description=(
            "Useful for summarization questions related to Prime Minister of India"
        ),
    )

    df_tool = QueryEngineTool.from_defaults(
        query_engine=df_query_engine,
        description=(
            "Useful for retrieving information about cricket batsment runs and records"
        ),
    )
    
    from llama_index.core.selectors import (
    PydanticMultiSelector,
    PydanticSingleSelector,
    )
    
    from llama_index.core.query_engine import RouterQueryEngine
    query_engine = RouterQueryEngine(
        selector=PydanticMultiSelector.from_defaults(),
        query_engine_tools=[
            blog_tool,
            df_tool,
        ],
    )
    
    response = query_engine.query(query_text)
    return str(response), 200

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


# if __name__ == '__main__':
#    app.run()

if __name__ == "__main__":
    # init the global index
    print("initializing index...")
    initialize_index()

    app.run(host="0.0.0.0", port=5601)