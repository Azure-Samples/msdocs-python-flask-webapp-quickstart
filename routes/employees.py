from flask import render_template
from app import cursor
from routes import bp_emp


@bp_emp.route('/')
def index():
    employees = cursor.execute("SELECT * FROM employees")
    return render_template('employees/index.html', employees=employees)