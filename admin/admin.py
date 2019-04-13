from flask import Blueprint, session, url_for, render_template

panel = Blueprint('administrator', __name__, template_folder='templates')


# Панель администратора
# Управление пользователями
@panel.route('/')
def index_adm():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    return render_template('admn.html')
