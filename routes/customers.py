from flask import render_template
from routes import bp_ctm


@bp_ctm.route('/')
def index():
    return render_template('customers/index.html')