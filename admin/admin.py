from flask import Blueprint, Flask, render_template, request, redirect, url_for, session     # инструменты Flask
import sqlite3                                                                    # для работы с БД SQLite
from datetime import date, timedelta                                              # класс для работы с датой
import random                                                                     # для генерации случайных чисел
import mail                                                                       # отправка сообщения для подтверждения регистрации
import checker                                                                    # проверки


panel = Blueprint('administrator', __name__, template_folder='templates')


# Панель администратора
# Управление пользователями
@panel.route('/')
def index_adm():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    return render_template('admn.html')

# Панель администратора (пользователь) - все пользователи (выводит всех пользователей из постоянной таблицы person
@panel.route('/allusers')
def allusers():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()
    cur.execute('SELECT * FROM person')
    persons = cur.fetchall()
    conn.close()
    return render_template('allusers.html', persons=persons)
