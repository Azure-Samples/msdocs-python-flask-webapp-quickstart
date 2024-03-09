from flask import Flask, render_template, url_for, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id
    
class Serve(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    player = db.Column(db.Integer, nullable=False)
    first_serve_in = db.Column(db.Integer, default=0)
    first_serve_out = db.Column(db.Integer, default=0)
    second_serve_in = db.Column(db.Integer, default=0)
    second_serve_out = db.Column(db.Integer, default=0)
    total_first_serve = db.Column(db.Integer, default=0)
    total_second_serve = db.Column(db.Integer, default=0)
    first_serve_in_percent = db.Column(db.Integer, default=0)
    second_serve_in_percent = db.Column(db.Integer, default=0)
    total_serve = db.Column(db.Integer, default=0)
    total_serve_in = db.Column(db.Integer, default=0)
    total_serve_out = db.Column(db.Integer, default=0)
    total_serve_percent = db.Column(db.Integer, default=0)
    duration = db.Column(db.Integer, default=0)
    location = db.Column(db.String(200))
    comment = db.Column(db.String(1000))

    def __repr__(self):
        return '<Serve %r>' % self.id

# Hardcoded dictionary mapping user IDs to names
user_dict = {
    '1': 'Andrew',
    '2': 'Emily',
    '3': 'Alex'
}

# Define a context processor to include the "u" query string parameter and the corresponding user name
@app.context_processor
def inject_user():
    user_id = request.args.get('u', '')  # Get the "u" query string parameter from the request
    user_name = user_dict.get(user_id, '')  # Get the corresponding user name from the dictionary
    return dict(u=user_id, user_name=user_name)  # Return a dictionary with the user parameter and user name


@app.route('/')
def index():
   return render_template('index.html')

# The Serve app entries

@app.route('/serve', methods=['POST', 'GET'])
def serve_index():
    uid = request.args.get('u')

    if request.method == 'GET':
        serves = Serve.query.filter_by(player=uid).order_by(Serve.date.desc()).limit(3).all()
        current_date = datetime.now()
        return render_template('serve.html', serves=serves, now=current_date)
    else:
        # Retrieve form data
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        first_serve_in = request.form['first_serve_in']
        first_serve_out = request.form['first_serve_out']
        first_serve_in_percent = request.form['first_serve_in_percent']
        second_serve_in = request.form['second_serve_in']
        second_serve_out = request.form['second_serve_out']
        second_serve_in_percent = request.form['second_serve_in_percent']
        total_serve_in = request.form['total_serve_in']
        total_serve_out = request.form['total_serve_out']
        total_serve_percent = request.form['total_serve_percent']
        total_serve = request.form['total_serve']
        duration = request.form['duration']
        location = request.form['location']
        comment = request.form['comment']
        player = uid

        # Create an instance of Serve class
        serve_instance = Serve(
            date=date,
            first_serve_in=first_serve_in,
            first_serve_out=first_serve_out,
            second_serve_in=second_serve_in,
            second_serve_out=second_serve_out,
            total_first_serve=first_serve_in + first_serve_out,
            total_second_serve=second_serve_in + second_serve_out,
            first_serve_in_percent=first_serve_in_percent,
            second_serve_in_percent=second_serve_in_percent,
            total_serve=total_serve,
            total_serve_in=total_serve_in,
            total_serve_out=total_serve_out,
            total_serve_percent=total_serve_percent,
            duration=duration,
            location=location,
            comment=comment,
            player = player
        )

        # Add the instance to the database
        db.session.add(serve_instance)
        db.session.commit()
        return redirect('/serve?u=' + uid)
    
@app.route('/serve/delete/<int:id>')
def serve_delete(id):
    serve_to_delete = Serve.query.get_or_404(id)
    uid = request.args.get('u')

    try:
        db.session.delete(serve_to_delete)
        db.session.commit()
        return redirect('/serve?u=' + uid)
    except:
        return 'There was a problem deleting that task'

@app.route('/serve/update/<int:id>', methods=['GET', 'POST'])
def serve_update(id):
    serve = Serve.query.get_or_404(id)
    uid = request.args.get('u')

    if request.method == 'POST':
        serve.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        serve.first_serve_in = request.form['first_serve_in']
        serve.first_serve_out = request.form['first_serve_out']
        serve.first_serve_in_percent = request.form['first_serve_in_percent']
        serve.second_serve_in = request.form['second_serve_in']
        serve.second_serve_out = request.form['second_serve_out']
        serve.second_serve_in_percent = request.form['second_serve_in_percent']
        serve.total_serve_in = request.form['total_serve_in']
        serve.total_serve_out = request.form['total_serve_out']
        serve.total_serve_percent = request.form['total_serve_percent']
        serve.total_serve = request.form['total_serve']
        serve.duration = request.form['duration']
        serve.location = request.form['location']
        serve.comment = request.form['comment']

        try:
            db.session.commit()
            return redirect('/serve?u=' + uid)
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('serve_update.html', serve=serve)


# The TODO App entries

@app.route('/todo', methods=['POST', 'GET'])
def todo_index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/todo')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('todo.html', tasks=tasks)


@app.route('/todo/delete/<int:id>')
def todo_delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/todo')
    except:
        return 'There was a problem deleting that task'

@app.route('/todo/update/<int:id>', methods=['GET', 'POST'])
def todo_update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/todo')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('todo_update.html', task=task)
    
@app.route('/serve/db')
def serve_db():
    try:
        return send_file('test.db', as_attachment=True)
    except Exception as e:
        return str(e)

# The Serve practice App entries

if __name__ == "__main__":
    app.debug = True
    app.run(debug=True)