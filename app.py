#: check all installed packages.
import sys
print("Python version:")
print(sys.version)

import pkg_resources
installed_packages = [pkg.key for pkg in pkg_resources.working_set]
print("Packages from", sys.path)
print(installed_packages)



import os
# import openai
# from langchain_openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from openai import AzureOpenAI

# print(openai.__version__)

# Replace with your Key Vault name
KVUri = "https://dfci-key-vault.vault.azure.net/"
secretName = "AZURE-OPENAI-API-KEY"

# Authenticate and create a client
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)
# get secret
retrieved_secret = client.get_secret(secretName)
print(retrieved_secret)

# Azure OpenAI
# DONE: secure api_key by using one of the secret scope in Azure or databricks
api_key = os.environ['AZURE_OPENAI_API_KEY'] = retrieved_secret.value
# api_version = os.environ['AZURE_OPENAI_API_VERSION'] = "2024-10-01" # from Resource JSON in the portal of the specific Azure OpenAI page.
api_version = os.environ[
    'AZURE_OPENAI_API_VERSION'] = "2024-05-01-preview"  # from Chat playground Sample Code (key authentication)
azure_deployment = os.environ['AZURE_OPENAI_ENDPOINT'] = "https://dfci-aoai-test.openai.azure.com/"
model_name = os.environ['AZURE_OPENAI_MODEL_NAME'] = "gpt-4o"

#
# # Alternatively, we don't use managed Azure identity, and use API key authentication.
# client = AzureOpenAI(
#     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#     api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
#     azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
#     )
#
# user_input = "Could you recommend 4 different stocks across 4 different sectors to buy? Please include tech, healthcare, finance, and energy."
#
# chat_prompt = [
#     {
#         "role": "system",
#         "content": [
#             {
#                 "type": "text",
#                 "text": "Scan the stock market to recommend stocks with strong fundamentals and technical indicators that indicate a good buy price. Provide comprehensive analysis incorporating fundamental data, technical indicators, and market sentiment. Given the complexity of this task, prioritize delivering depth over the total number of stock analyses offered. Recommended output can reasonably focus on 2-3 stocks."
#             }
#         ]
#     },
#     {
#         "role": "user",
#         "content": [
#             {
#                 "type": "text",
#                 "text": f"{user_input}"
#             }
#         ]
#     },
#     {
#         "role": "assistant",
#         "content": [
#             {
#                 "type": "text",
#                 "text": ""
#             }
#         ]
#     }
# ]
#
# chat_prompt = chat_prompt
#
# # Include speech result if speech is enabled
# messages = chat_prompt
#
# completion = client.chat.completions.create(
#     model=model_name,
#     messages=messages,
#     max_tokens=4096,
#     temperature=0.7,
#     top_p=0.95,
#     frequency_penalty=0,
#     presence_penalty=0,
#     stop=None,
#     stream=False
# )
#
# print(completion.to_json())
#

# make sure we have flask >3.0. In runtime ML 15.4, it is old version of flask, so will fail.
from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)

app = Flask(__name__)


@app.route('/')
def index():
    print('Request for index page received')
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/hello', methods=['POST'])
def hello():
    req = request.form.get('req')

    # Azure OpenAI
    #
    # # Alternatively, we don't use managed Azure identity, and use API key authentication.
    client = AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_API_KEY"), api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"))

    user_input = req

    chat_prompt = [{"role": "system", "content": [{"type": "text",
        "text": "Scan the stock market to recommend stocks with strong fundamentals and technical indicators that indicate a good buy price. Provide comprehensive analysis incorporating fundamental data, technical indicators, and market sentiment. Given the complexity of this task, prioritize delivering depth over the total number of stock analyses offered. Recommended output can reasonably focus on 2-3 stocks."}]},
        {"role": "user", "content": [{"type": "text", "text": f"{user_input}"}]},
        {"role": "assistant", "content": [{"type": "text", "text": ""}]}]

    chat_prompt = chat_prompt

    # Include speech result if speech is enabled
    messages = chat_prompt

    completion = client.chat.completions.create(model=model_name, messages=messages, max_tokens=4096, temperature=0.7,
        top_p=0.95, frequency_penalty=0, presence_penalty=0, stop=None, stream=False)

    print(completion.to_json())

    text = completion.choices[0].message.content

    # OpenAI
    # llm = ChatOpenAI(openai_api_key=openai_api_key)
    # text = llm.invoke(req)

    if req:
        print('Request for hello page received with req=%s' % req)
        return render_template('hello.html', req=text)
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
