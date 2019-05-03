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

# Панель администратора (пользователь) - удаляет пользователя из постоянной таблицы person
@panel.route('/deluser')
def deluser():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()
    del_num = request.args.get('idu')
    cur.execute('DELETE FROM person WHERE id_prsn = {}'.format(del_num))
    conn.commit()
    conn.close()
    return redirect(url_for('administrator.allusers'))

# Панель администратора (события) - выводит список всех событий
@panel.route('/event')
def event():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()
    cur.execute('SELECT * FROM event')
    events = cur.fetchall()
    conn.close()
    return render_template('event.html', events=events)

# Панель администратора (события) - выполняет добавление нового события и редирект к списку всех событий
@panel.route('/eventadd', methods=['GET', 'POST'])
def eventadd():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    
    event=request.form['event']
    activity=request.form['activity']
    date=request.form['date']

    # Соединение с БД
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()    
    # Вставка записи в таблицу событий
    cur.execute("INSERT INTO event (event, activity, date) VALUES ('" +event+ "', '" +activity+ "', '" +date+ "')")
    # Фиксируем изменения в базе
    conn.commit()    
    # Закрываем соединение
    conn.close()
    
    return redirect(url_for('administrator.event'))

# Панель администратора (события) - удаление события и редирект к списку событий
@panel.route('/deletevt/<id>')
def deletevt(id):
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    
    # Соединение с БД
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()    
    cur.execute("DELETE FROM event WHERE id_evt = " + id)
    conn.commit()
    conn.close()
    
    return redirect(url_for('administrator.event'))

# Панель администратора (события) - статистика регистраций на событие, списки волонтеров зарегистрировавшихся на конкретное событие
@panel.route('/stat/<id_evt>')
def stat(id_evt):
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    
    conn = sqlite3.connect("sql/volonteer.db")
    curI = conn.cursor()
    curII = conn.cursor()
    # Выборка волонтеров зарегистрированных на конкретное событие
    curI.execute("SELECT p.id_prsn, surname_prsn, name_prsn, patronymic_prsn, faculty, email, phone, birthday FROM registration AS r JOIN person AS p ON r.id_prsn=p.id_prsn WHERE r.id_evt = {}".format(id_evt))
    # Данные о событии по его id
    curII.execute("SELECT * FROM event WHERE id_evt = {}".format(id_evt))
    registration = curI.fetchall()
    count = len(registration)
    event = curII.fetchone()
    # дописать тело. Показывает сколько человек зарегистрировалось на событие и вы водит поименный список с возможностью отмечать присутствие
    return render_template('stat.html', registration=registration, event=event, count=count)


# Панель администратора (события) - отметить волонтера на событии
@panel.route('/check', methods=['GET', 'POST'])
def check():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    

    # Соединение с БД
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()

    event=request.form['event']
    _form=request.form
    for key in _form:
        if _form[key] == 'on':
            # Меняем нолик на единицу в таблице регистраций, устанавливая посещение волонтером с id = key мероприятия с id = event
            cur.execute("UPDATE registration SET visit = 1 WHERE id_prsn = {0} AND id_evt={1}".format(key, event))
        conn.commit()

    conn.close()    
    return redirect(url_for('administrator.event'))

# Форма для новости
@panel.route('/post')
def post():
    return render_template('posts.html')

# Публикация новости
@panel.route('/addpost', methods=['GET','POST'])
def addpost():
    conn=sqlite3.connect("sql/volonteer.db")
    cur=conn.cursor()
    cur.execute('INSERT INTO news (date, title, body) VALUES ("{}","{}","{}")'.format(date.today(), request.form['titlepost'], request.form['bodypost']))
    conn.commit()
    conn.close()
    return redirect(url_for('administrator.index_adm'))