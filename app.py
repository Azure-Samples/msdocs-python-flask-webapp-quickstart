from datetime import datetime
import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)

conn = psycopg2.connect(
    host="quotechies.database.windows.net",
    database="quotechies-db",
    user="bscott129@",
    password="hackathon10!",
    port="3306")

def insert_data(name, zip):
    cur = conn.cursor()
    cur.execute("INSERT INTO your_table (name, zip_code) VALUES (%s, %s)", (name, zip))
    conn.commit()
    cur.close()

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
   zip = request.form.get('zip')
   if name:
       print('Request for hello page received with name=%s' % name)
       insert_data(name, zip)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

if __name__ == '__main__':
   app.run()
