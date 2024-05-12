from flask import render_template
from routes import bp_inv


@bp_inv.route('/')
def index():
    return render_template('invoices/index.html')