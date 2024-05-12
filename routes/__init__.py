from flask import Blueprint

bp = Blueprint('routes', __name__)
bp_emp = Blueprint('employees', __name__)
bp_ctm = Blueprint('customers', __name__)
bp_prod = Blueprint('products', __name__)
bp_inv = Blueprint('invoices', __name__)

from routes import routes, employees, customers, products, invoices
