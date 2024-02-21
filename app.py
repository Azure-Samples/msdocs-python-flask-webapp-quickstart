import os
import pandas as pd
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

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
   name = request.form.get('name')
   order = request.form.get('value')
   data = {'Country': [name], 'Orders': [order]
           }
   df = pd.DataFrame(data)
   df.to_csv('push.csv', mode='a', index=False, header=False)


   block_blob_service = BlockBlobService(account_name='storagesaphanatestdl',
                                         account_key='vsqZoXBJW3SRTROGAfkyRuLW6egrlCjK/vOFtiShaawzwYhXarYbmHqBKxluOSjmfyJY88rgpFgs+AStUsxu+w==')
   block_blob_service.create_container('testdata')

   # Upload the CSV file to Azure cloud
   block_blob_service.create_blob_from_path(
       'testdata',
       'testdata.csv',
       'push.csv',
       content_settings=ContentSettings(content_type='application/CSV')
   )

   # Check the list of blob
   generator = block_blob_service.list_blobs('testdata')
   for blob in generator:
       print(blob.name)

   # Download the CSV file From Azure storage
   block_blob_service.get_blob_to_path('testdata', 'testdata.csv', 'push.csv')


   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run(host="127.0.0.1", port="12345")
