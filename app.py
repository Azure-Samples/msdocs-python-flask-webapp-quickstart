import os 
import base64
# import openai
from langchain_openai import AzureOpenAI  
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
# print(openai.__version__)

# Azure OpenAI
api_key = os.environ['AZURE_OPENAI_API_KEY'] = dbutils.secrets.get(scope="yyang_secret_scope", key="AZURE_OPENAI_API_KEY")
# api_version = os.environ['AZURE_OPENAI_API_VERSION'] = "2024-10-01" # from Resource JSON in the portal of the specific Azure OpenAI page.
api_version = os.environ['AZURE_OPENAI_API_VERSION'] = "2024-05-01-preview" # from Chat playground Sample Code (key authentication)
azure_deployment = os.environ['AZURE_OPENAI_ENDPOINT'] = "https://dfci-aoai-test.openai.azure.com/"
model_name = os.environ['AZURE_OPENAI_MODEL_NAME'] = "gpt-4o"


# Alternatively, we don't use managed Azure identity, and use API key authentication.
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )


# make sure we have flask >3.0. In runtime ML 15.4, it is old version of flask, so will fail.
from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)

app = Flask(__name__)


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
   req = request.form.get('req')

   # Azure OpenAI
   llm = AzureOpenAI(
       api_key=api_key,
       api_version=api_version,
       azure_deployment=azure_deployment,
       model_name=model_name,
   )
   text = llm.invoke(req)

   # OpenAI
	 # llm = ChatOpenAI(openai_api_key=openai_api_key)
	 # text = llm.invoke(req)

   if req:
       print('Request for hello page received with req=%s' % req)
       return render_template('hello.html', req = text)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))
   
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000, debug=False)

