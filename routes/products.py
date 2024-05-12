from flask import render_template
from routes import bp_prod


@bp_prod.route('/')
def index():
    return render_template('products/index.html')