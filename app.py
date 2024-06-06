import os, uuid
import pandas as pd

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

app = Flask(__name__)

#================================================================================================
# # Create a blob client using the local simulator
# try:
#     account_url = "https://sinong.blob.core.windows.net"
#     default_credential = DefaultAzureCredential()

#     # Create the BlobServiceClient object
#     blob_service_client = BlobServiceClient(account_url, credential=default_credential)
#     container_client = blob_service_client.get_container_client(container="quiz0")
#     blob_list = container_client.list_blobs()
#     for blob in blob_list:
#         print("\t" + blob.name)
# except:
#     print("Error creating the BlobServiceClient object")
#================================================================================================

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')


@app.route('/assignment1')
def assignment1():
    data_file_path = os.path.join(app.root_path, 'static', 'data', 'people.csv')
    data = pd.read_csv(data_file_path)
    print('Request for assignment1 page received')

    return render_template('assignment1.html', contain_content=False, table_content=list(data.values.tolist()), titles=data.columns.values)


@app.route('/a1-upload', methods = ['POST'])   
def upload():   
    if request.method == 'POST':   
        f = request.files['file']
        file_path = os.path.join(app.root_path, 'uploads', f.filename)
        f.save(file_path)
        
        data = pd.read_csv(file_path)
        return render_template('assignment1.html', contain_content=False, table_content=list(data.values.tolist()), titles=data.columns.values)


@app.route('/a1-searchbyname', methods = ['POST', 'GET'])
def a1_searchbyname():
    name = request.form.get('queryName')
    data_file_path = os.path.join(app.root_path, 'static', 'data', 'people.csv')
    data = pd.read_csv(data_file_path)
    query_data = data.loc[data['Name'] == name]
    print(name, query_data)
    return render_template('assignment1.html', contain_content=True, table_content=list(query_data.values.tolist()), titles=query_data.columns.values)


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


if __name__ == '__main__':
   app.run()
