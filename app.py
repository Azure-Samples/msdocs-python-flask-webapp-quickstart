import os

from flask import Flask, redirect, render_template, request,url_for, abort, send_from_directory
from werkzeug.utils import secure_filename
from azure.storage.blob import ContainerClient, __version__
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10240 * 10240
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif', '.PNG', '.JPG','.jpeg','.JPEG']
#app.config['UPLOAD_PATH'] = 'C:\\uploads'

connect_str = "BlobEndpoint=https://minkonto.blob.core.windows.net/;QueueEndpoint=https://minkonto.queue.core.windows.net/;FileEndpoint=https://minkonto.file.core.windows.net/;TableEndpoint=https://minkonto.table.core.windows.net/;SharedAccessSignature=sv=2021-12-02&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2023-06-30T13:41:12Z&st=2023-05-03T05:41:12Z&spr=https&sig=YRtN%2FYiPlnSv4HGaxiVMcnoHUepI4lcLt4i8KkCfG6w%3D"
container_name = "photos" # container name in which images will be store in the storage account
blob_service_client = BlobServiceClient.from_connection_string(conn_str=connect_str) # create a blob service client to interact with the storage account
container_client = blob_service_client.get_container_client(container=container_name) # get container client to interact with the container in which images will be stored
#container_client.get_container_properties() # get properties of the container to force exception to be thrown if container does not exist
container = ContainerClient.from_connection_string(conn_str=connect_str, container_name=container_name)

@app.route('/')
def index():
   return render_template('index.html', title='Start')

@app.route('/blob')
def blob():
    img_html = []
    blob_items = container_client.list_blobs()
    for blob in blob_items:
        blob_client = container_client.get_blob_client(blob=blob.name)
        #img_html += "<img src='{}' width='auto' height='200'/>".format(blob_client.url)
        img_html.append(blob_client.url)
        #img_html += format(blob_client.url)
        #blob = blob_client.url
    return render_template('ListBlob.html', title='List Blobs', img_html=img_html)

@app.route('/table')
def table():
    img_html = []
    blob_items = container_client.list_blobs()
    for blob in blob_items:
        blob_client = container_client.get_blob_client(blob=blob.name)
        #img_html += "<img src='{}' width='auto' height='200'/>".format(blob_client.url)
        img_html.append(blob_client.url)
        #img_html += format(blob_client.url)
        #blob = blob_client.url
    return render_template('blobTable.html', title='List Blobs', img_html=img_html)

@app.route('/listblob')
def listblob():
    blob_list = container.list_blobs()
    return render_template('testListBlob.html', title='Lister Blobs', blob_list=blob_list)


if __name__ == '__main__':
   app.run()
