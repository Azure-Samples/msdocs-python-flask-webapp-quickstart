from flask import render_template
from routes import bp_emp


@bp_emp.route('/')
def index():
    return render_template('employees/index.html')