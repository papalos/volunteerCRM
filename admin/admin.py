from flask import Blueprint

panel = Blueprint('posts', __name__, template_folder='templates')

@panel.route('/')
def index():
    return 'Hello All'