from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)


@app.route('/')
def index():   
   return render_template('index.html')


@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')
   if name:
       return render_template('hello.html', name = name)
   else:
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()