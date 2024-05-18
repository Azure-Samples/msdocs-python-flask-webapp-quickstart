from flask import render_template
from app import cursor
from routes import bp_ctm


@bp_ctm.route('/')
def index():
    customers = cursor.execute("SELECT * FROM customers")
    return render_template('customers/index.html', customers=customers)
