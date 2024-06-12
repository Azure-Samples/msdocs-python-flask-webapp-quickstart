import os, uuid
import pandas as pd

import pymssql
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import datetime

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, session)

app = Flask(__name__)
app.secret_key = os.urandom(24)

conn = pymssql.connect(host='bonjour.database.windows.net' ,user='zander' ,password = 'KB24ts1989',database='Mavs')
cur = conn.cursor()
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

@app.route('/index')
def index():
   print('Request for index page received')
   return render_template('index.html')


@app.route('/test')
def test():
    SQL_QUERY = """
                SELECT 
                TOP 5 c.CustomerID, 
                c.CompanyName, 
                COUNT(soh.SalesOrderID) AS OrderCount 
                FROM 
                SalesLT.Customer AS c 
                LEFT OUTER JOIN SalesLT.SalesOrderHeader AS soh ON c.CustomerID = soh.CustomerID 
                GROUP BY 
                c.CustomerID, 
                c.CompanyName 
                ORDER BY 
                OrderCount DESC;
                """
    cur.execute(SQL_QUERY)
    data = cur.fetchall()
    print('Request for test page received')
    return render_template('test.html', data=data)


@app.route('/assignment1')
def assignment1():
    data_file_path = os.path.join(app.root_path, 'static', 'data', 'people.csv')
    data = pd.read_csv(data_file_path)
    print('Request for assignment1 page received')

    return render_template('assignment1.html', contain_content=False, table_content=list(data.values.tolist()), titles=data.columns.values)


@app.route('/')
def assignment2():
    
    print('Request for assignment1 page received')
    data = None
    headers = None
    return render_template('assignment2.html', contain_content=False, table_content=data, titles=headers)


@app.route('/a1-upload', methods = ['POST'])   
def upload():   
    if request.method == 'POST':   
        f = request.files['file']
        file_path = os.path.join(app.root_path, 'uploads', f.filename)
        session['file_path'] = file_path
        f.save(file_path)

        data = pd.read_csv(file_path)

        for idx, (_, row) in enumerate(data.iterrows()):
            sql_query = f"INSERT INTO dbo.Quiz1 VALUES ('{idx}', "
            for element in row:
                if pd.isna(element):
                    element = 'NULL'
                    sql_query += f"{element},"
                else:
                    sql_query += f"'{element}',"
            sql_query = sql_query[:-1] + ");"
            print(sql_query)
            cur.execute(sql_query)

        conn.commit()
        return render_template('assignment1.html', contain_content=False, table_content=list(data.values.tolist()), titles=data.columns.values)


@app.route('/a1-searchbyname', methods = ['POST', 'GET'])
def a1_searchbyname():
    name = request.form.get('queryName')
    data_file_path = session.get('file_path')
    data = pd.read_csv(data_file_path)
    query_data = data.loc[data['name'] == name]
    print(name, query_data)
    for col in query_data.columns:
            query_data[col].fillna(f"no {col} available", inplace=True)
    return render_template('assignment1.html', contain_content=True, table_content=list(query_data.values.tolist()), titles=query_data.columns.values)

@app.route('/a1-searchbycostrange', methods = ['POST', 'GET'])
def a1_searchbycostrange():
    min_cost = request.form.get('minCost')
    max_cost = request.form.get('maxCost')
    data_file_path = session.get('file_path')
    data = pd.read_csv(data_file_path)
    query_data = data.loc[(data['cost'].astype(float) >= int(min_cost)) & (data['cost'].astype(float) <= int(max_cost))]
    print(min_cost, max_cost, query_data)
    for col in query_data.columns:
            query_data[col].fillna(f"no {col} available", inplace=True)
    return render_template('assignment1.html', contain_content=True, table_content=list(query_data.values.tolist()), titles=query_data.columns.values)


@app.route('/a2-searchbymag', methods = ['POST', 'GET'])
def a2_searchbymag():
    min_mag = request.form.get('minMag')
    max_mag = request.form.get('maxMag')
    back_day = request.form.get('backDay')
    
    # query header from database
    SQL_QUERY_TITLE = """select COLUMN_NAME
                        from INFORMATION_SCHEMA.COLUMNS
                        where TABLE_NAME='earthquakes';"""
    cur.execute(SQL_QUERY_TITLE)
    headers = cur.fetchall()
    
    # query data from database
    # Get today's datetime
    today = datetime.datetime.now()

    # Modify the query to query for the latest back_day data
    SQL_QUERY = f"""
                SELECT 
                * 
                FROM 
                ass1.earthquakes 
                WHERE 
                mag >= {min_mag} AND mag <= {max_mag} AND time >= DATEADD(day, -{back_day}, GETDATE());
                """
    cur.execute(SQL_QUERY)
    data = cur.fetchall()
    print(type(headers))
    print(type(data))

    return render_template('assignment2.html', contain_content=True, table_content=data, titles=headers)


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
