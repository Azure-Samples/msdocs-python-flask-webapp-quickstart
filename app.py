from flask import Flask, render_template, url_for, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func, extract

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

class ServeAnalysis:
    pass  # Empty class definition

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
    player_id = request.args.get('u')

    if request.method == 'GET':
        serves_all = Serve.query.filter_by(player=player_id ).order_by(Serve.date.desc()).all()
        current_date = datetime.now()

        # Query to get total serves, total duration, and count of records for the player per week
        weekly_results = Serve.query.with_entities(extract('year', Serve.date).label('year'),
                                                extract('week', Serve.date).label('week'),
                                                func.sum(Serve.total_serve),
                                                func.sum(Serve.duration),
                                                func.count(Serve.id)) \
                                    .filter(Serve.player == player_id) \
                                    .group_by('year', 'week') \
                                    .all()

        # Initialize variables for weekly data
        total_serves_weekly = 0
        total_duration_weekly = 0
        total_records_weekly = 0

        # Iterate over the weekly results and calculate totals
        for _, _, serves, duration, records in weekly_results:
            total_serves_weekly += serves or 0
            total_duration_weekly += duration or 0
            total_records_weekly += records or 0

        # Calculate the number of weeks
        num_weeks = len(weekly_results)

        # Calculate averages for weekly data
        average_serves_per_week = total_serves_weekly / num_weeks if num_weeks > 0 else 0
        average_duration_per_week = total_duration_weekly / num_weeks if num_weeks > 0 else 0
        average_records_per_week = total_records_weekly / num_weeks if num_weeks > 0 else 0

        # Query to get total serves, total duration, and count of all records for the player
        total_results = Serve.query.with_entities(func.sum(Serve.total_serve),
                                                func.sum(Serve.duration),
                                                func.count(Serve.id)) \
                                    .filter(Serve.player == player_id) \
                                    .first()

        # Extract values from the total results
        total_serves = total_results[0] or 0
        total_duration = total_results[1] or 0
        total_records = total_results[2] or 0

        # Calculate the time since the first entry
        first_entry = Serve.query.filter_by(player=player_id).order_by(Serve.date.asc()).first()
        time_since_first_entry = datetime.now() - first_entry.date if first_entry else timedelta(0)

        # Round up to days
        time_since_first_entry_rounded = timedelta(days=time_since_first_entry.days)

        # Create an instance of ServeAnalysis class
        serve_analysis = ServeAnalysis()
        serve_analysis.total_serves = total_serves
        serve_analysis.total_duration = total_duration
        serve_analysis.total_records = total_records
        serve_analysis.average_serves_per_week = average_serves_per_week
        serve_analysis.average_duration_per_week = average_duration_per_week
        serve_analysis.average_records_per_week = average_records_per_week
        serve_analysis.time_since_first_entry = time_since_first_entry_rounded

        return render_template('serve.html', serves=serves_all, now=current_date, serve_analysis=serve_analysis)
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
        player = player_id

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
        return redirect('/serve?u=' + player_id)
    
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

@app.route('/serve/analysis')
def serve_analysis():
    player_id = request.args.get('u')
    
    # Calculate the start date of the current week (Monday)
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(days=0 if today.weekday() == 6 else 1)

    # Query to get total serves, total duration, and count of records for the player per week
    results = Serve.query.with_entities(extract('year', Serve.date).label('year'),
                                        extract('week', Serve.date).label('week'),
                                        func.sum(Serve.total_serve),
                                        func.sum(Serve.duration),
                                        func.count(Serve.id)) \
                        .filter(Serve.player == player_id) \
                        .group_by('year', 'week') \
                        .all()

    # Initialize variables
    total_serves = 0
    total_duration = 0
    total_records = 0

    # Iterate over the results and calculate totals
    for _, _, serves, duration, records in results:
        total_serves += serves or 0
        total_duration += duration or 0
        total_records += records or 0

    # Calculate the number of weeks
    num_weeks = len(results)

    # Calculate averages
    average_serves_per_week = total_serves / num_weeks if num_weeks > 0 else 0
    average_duration_per_week = total_duration / num_weeks if num_weeks > 0 else 0
    average_records_per_week = total_records / num_weeks if num_weeks > 0 else 0

    # Create an instance of ServeAnalysis class
    serve_analysis = ServeAnalysis()
    serve_analysis.total_serves = total_serves
    serve_analysis.total_duration = total_duration
    serve_analysis.average_serves_per_week = average_serves_per_week
    serve_analysis.average_duration_per_week = average_duration_per_week
    serve_analysis.average_records_per_week = average_records_per_week

    # Pass the instance to the template
    return render_template('serve_analysis.html', serve_analysis=serve_analysis)

@app.route('/serve/diagram')
def serve_diagram():
    player_id = request.args.get('u')
    serves_all = Serve.query.filter_by(player=player_id).order_by(Serve.date.asc()).all()

    return render_template('serve_diagram.html', serves=serves_all)

# The TODO App entries =====================================================================

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