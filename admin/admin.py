from flask import Blueprint, Flask, render_template, request, redirect, url_for, session, send_file     # инструменты Flask
import sqlite3                                                                    # для работы с БД SQLite
from datetime import date, timedelta                                              # класс для работы с датой
import random                                                                     # для генерации случайных чисел
# import mail                                                                       # отправка сообщения для подтверждения регистрации
# import checker                                                                    # проверки
import xlsxwriter                                                                 # создание документа .xmlx


FOR_TABLE = ('Номер_события', 'Событие', 'Активность', 'Дата _проведения', 'Время начала', 'Продолжительность', 'Адрес проведения', 'Номер_волонтера', 'Фамилия', 'Имя', 'Отчество', 'Факультет', 'e-mail', 'Телефон', 'Дата_рождения', 'Пол', 'Курс', 'Отметка_о_посещении', 'Роль выбраная при регистрации', 'Аудитория')
FOR_TABLE_ALLUSERS = ('id', 'Фамилия', 'Имя', 'Отчество', 'Факультет', 'e-mail', 'Телефон', 'Дата рожедния', 'Логин', 'Пароль' , 'Дата регистрации', 'Пол', 'Курс')
FOR_TABLE_SOMEEVENTS = ('id', 'Событие', 'Активность', 'Дата проведения', 'Время прихода', 'Время начала', 'Продолжительность', 'Штаб_min', 'Штаб_max', 'Аудитория_min', 'Аудитория_max', 'Адресс')
FOR_TABLE_USERREGISTERONEVENT = ('id', 'Фамилия', 'Имя', 'Отчество', 'Факультет', 'e-mail', 'Телефон', 'День рождения', 'Роль')
FOR_TABLE_USERVISIT = ('id', 'Фамилия', 'Имя', 'Отчество', 'Факультет', 'e-mail', 'Телефон', 'Дата рождения', 'Пол', 'Курс', 'Аудитория')

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
    cur.execute('''SELECT p.*, r.num, t.num
                   FROM person AS p 
                   LEFT JOIN (SELECT id_prsn, COUNT(visit) AS num FROM registration GROUP BY id_prsn) AS r ON p.id_prsn = r.id_prsn
                   LEFT JOIN (SELECT id_prsn, COUNT(visit) AS num FROM registration WHERE visit=1 GROUP BY id_prsn) AS t ON p.id_prsn = t.id_prsn
                ''')
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
    cur.execute('SELECT * FROM event ORDER BY date DESC')
    events = cur.fetchall()
    conn.close()
    return render_template('event.html', events=events)

# Панель администратора (события) - выводит список всех событий
@panel.route('/event_add_html')
def event_add_html():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    return render_template('event_add_html.html')

# Панель администратора (события) - выполняет добавление нового события и редирект к списку всех событий
@panel.route('/eventadd', methods=['GET', 'POST'])
def eventadd():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    
    event=request.form['event']
    activity=request.form['activity']
    date=request.form['date']
    time_in=request.form['time_in']
    time_start=request.form['time_start']
    duration=request.form['duration']
    staff_min=request.form['staff_min']
    staff_max=request.form['staff_max']
    classroom_min=request.form['classroom_min']
    classroom_max=request.form['classroom_max']
    address=request.form['address']

    # Соединение с БД
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()    
    # Вставка записи в таблицу событий
    cur.execute("INSERT INTO event (event, activity, date, time_in, time_start, duration, staff_min, staff_max, classroom_min, classroom_max, address) VALUES ('" +event+ "', '" +activity+ "', '" +date+ "', '" +time_in+ "', '" +time_start+ "', '" +duration+ "', '" +staff_min+ "', '" +staff_max+ "', '" +classroom_min+ "', '" +classroom_max+ "', '" +address+ "')")
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
    curI.execute("SELECT p.id_prsn, surname_prsn, name_prsn, patronymic_prsn, faculty, email, phone, birthday, r.role FROM registration AS r JOIN person AS p ON r.id_prsn=p.id_prsn WHERE r.id_evt = {} ORDER BY surname_prsn".format(id_evt))
    # Данные о событии по его id
    curII.execute("SELECT * FROM event WHERE id_evt = {}".format(id_evt))
    registration = curI.fetchall()
    x_count = [x[8] for x in registration]
    x_staff = x_count.count('штаб')
    x_classroom = x_count.count('аудитория')
    event = curII.fetchone()
    
    conn.close()


    # дописать тело. Показывает сколько человек зарегистрировалось на событие и вы водит поименный список с возможностью отмечать присутствие
    return render_template('stat.html', registration=registration, event=event, x_staff=x_staff, x_classroom=x_classroom, id_evt=id_evt)

# Панель администратора (события) - статистика регистраций на событие, списки волонтеров зарегистрировавшихся на конкретное событие
@panel.route('/visit/<id_evt>')
def visit(id_evt):
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    
    conn = sqlite3.connect("sql/volonteer.db")
    curI = conn.cursor()
    curII = conn.cursor()
    # Выборка волонтеров зарегистрированных на конкретное событие
    curI.execute("SELECT p.id_prsn, surname_prsn, name_prsn, patronymic_prsn, faculty, email, phone, birthday, sex, year_st, classroom FROM registration AS r JOIN person AS p ON r.id_prsn=p.id_prsn WHERE r.id_evt = {} AND visit=1".format(id_evt))
    # Данные о событии по его id
    curII.execute("SELECT * FROM event WHERE id_evt = {}".format(id_evt))
    visited = curI.fetchall()
    count = len(visited)
    event = curII.fetchone()
    # дописать тело. Показывает сколько человек зарегистрировалось на событие и вы водит поименный список с возможностью отмечать присутствие
    return render_template('visit.html', visited=visited, event=event, count=count, id_evt=id_evt)


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
            cur.execute("UPDATE registration SET visit = 1, classroom={2} WHERE id_prsn = {0} AND id_evt={1}".format(key, event, _form.get('classroom_for_'+key)))
        conn.commit()

    conn.close()    
    return redirect(url_for('administrator.event'))

# ------------------------------------- Раздел о факультетах -----------------------------------------------------------

# Форма для информации о факультетах
@panel.route('/faculty')
def faculty():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))

    conn=sqlite3.connect("sql/volonteer.db")
    cur=conn.cursor()
    cur.execute('SELECT * FROM faculty ORDER BY full_name')
    faculty = cur.fetchall()
    conn.close()

    return render_template('faculty.html', faculty=faculty)

# Добавления факультета
@panel.route('/facultyadd', methods = ['GET', 'POST'])
def facultyadd():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))

    full_name = request.form.get('full_name')
    short_name = request.form.get('short_name')
    leader_name = request.form.get('leader_name')
    phone = request.form.get('phone')
    email = request.form.get('email')


    conn=sqlite3.connect("sql/volonteer.db")
    cur=conn.cursor()
    cur.execute('INSERT INTO faculty (full_name, short_name, leader_name, phone, email) VALUES ("{0}", "{1}", "{2}", "{3}", "{4}")'.format(full_name, short_name, leader_name, phone, email))
    conn.commit()
    conn.close()

    return redirect(url_for('administrator.faculty'))

# Удаление факультета
@panel.route('/facultydel/<f_id>')
def facultydel(f_id):
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))

    conn=sqlite3.connect("sql/volonteer.db")
    cur=conn.cursor()
    cur.execute('DELETE FROM faculty WHERE f_id="{}"'.format(f_id))
    conn.commit()
    conn.close()

    return redirect(url_for('administrator.faculty'))

# Форма редактирования факультета
@panel.route('/facultyedit/<f_id>')
def facultyedit(f_id):
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))

    conn=sqlite3.connect("sql/volonteer.db")
    cur=conn.cursor()
    cur.execute('SELECT * FROM faculty WHERE f_id="{}"'.format(f_id))
    fac = cur.fetchone()
    conn.close()

    return render_template('faculty_edit.html', fac = fac)

# Функция редактирования факультета
@panel.route('/facultyeditfoo', methods = ['GET', 'POST'])
def facultyeditfoo():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    f_id = request.form.get('f_id')
    full_name = request.form.get('full_name')
    short_name = request.form.get('short_name')
    leader_name = request.form.get('leader_name')
    phone = request.form.get('phone')
    email = request.form.get('email')


    conn=sqlite3.connect("sql/volonteer.db")
    cur=conn.cursor()
    cur.execute('UPDATE faculty SET full_name = "{0}", short_name = "{1}", leader_name = "{2}", phone = "{3}", email = "{4}" WHERE f_id = "{5}"'.format(full_name, short_name, leader_name, phone, email, f_id))
    conn.commit()
    conn.close()

    return redirect(url_for('administrator.faculty'))

# --------------- Блок новостей -------------------------------------------------------------------------

# Форма для новости
@panel.route('/post')
def post():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))

    conn=sqlite3.connect("sql/volonteer.db")
    cur=conn.cursor()
    cur.execute('SELECT * FROM news ORDER BY date DESC')
    news = cur.fetchall()
    conn.close()

    return render_template('posts.html', news=news)

# Публикация новости
@panel.route('/addpost', methods=['GET','POST'])
def addpost():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))

    title = request.form.get('titlepost')
    body = request.form.get('bodypost')
    type = request.form.get('type')    

    conn=sqlite3.connect("sql/volonteer.db")
    cur=conn.cursor()
    cur.execute('INSERT INTO news (date, title, body, type) VALUES ("{}","{}","{}", "{}")'.format(date.today(), title, body, type))
    conn.commit()
    conn.close()
    return redirect(url_for('administrator.post'))

# Редактирование новости интерфейс
@panel.route('/postrecovery/<id_new>')
def postrecovery(id_new):
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))

    conn=sqlite3.connect("sql/volonteer.db")
    cur=conn.cursor()
    cur.execute('SELECT * FROM news WHERE id="{}"'.format(id_new))
    new = cur.fetchone()
    conn.close()
    return render_template('post_recovery.html', new=new)

# Редактирование новости обработка формы
@panel.route('/postrecoveryfoo', methods=['GET','POST'])
def postrecoveryfoo():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))

    id = request.form.get('id_new')
    date = request.form.get('date')
    title = request.form.get('titlepost')
    body = request.form.get('bodypost')
    type = request.form.get('type')    
    
    conn=sqlite3.connect("sql/volonteer.db")
    cur=conn.cursor()
    cur.execute('UPDATE news SET date="{0}", title="{1}", body="{2}", type="{3}" WHERE id = "{4}"'.format(date, title, body, type, id))
    conn.commit()
    conn.close()
    return redirect(url_for('administrator.post'))

# Удаление новости
@panel.route('/delpost/<id_new>')
def delpost(id_new):
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))

    conn=sqlite3.connect("sql/volonteer.db")
    cur=conn.cursor()
    cur.execute('DELETE FROM news WHERE id = "{}"'.format(id_new))
    conn.commit()
    conn.close()
    return redirect(url_for('administrator.post'))


# ----------------------------------------------------------- Отчеты -------------------------------------------------------------------------------

# Выгружает всех зарегистрированных пользователей в виде excel файла
@panel.route('/getdata', methods=['GET','POST'])
def getdata():
    conn=sqlite3.connect('sql/volonteer.db')
    cur = conn.cursor()
    _since = request.form.get('since')
    _to = request.form.get('to')
    if(_since==None and _to==None):
        cur.execute('''SELECT ev.id_evt, ev.event, ev.activity, ev.date, ev.time_start,  ev.duration, ev.address, p.id_prsn, p.surname_prsn, p.name_prsn, p.patronymic_prsn, p.faculty, p.email, p.phone, p.birthday, p.sex, p.year_st, reg.visit, reg.role, reg.classroom
                   FROM registration AS reg 
                   JOIN person AS p ON reg.id_prsn = p.id_prsn
                   JOIN event AS ev ON reg.id_evt = ev.id_evt
                   ORDER BY ev.id_evt DESC''')
    else:
        cur.execute('''SELECT ev.id_evt, ev.event, ev.activity, ev.date, ev.time_start,  ev.duration, ev.address, p.id_prsn, p.surname_prsn, p.name_prsn, p.patronymic_prsn, p.faculty, p.email, p.phone, p.birthday, p.sex, p.year_st, reg.visit, reg.role, reg.classroom
                   FROM registration AS reg 
                   JOIN person AS p ON reg.id_prsn = p.id_prsn
                   JOIN event AS ev ON reg.id_evt = ev.id_evt
                   WHERE ev.date >= '{0}' AND ev.date <= "{1}"
                   ORDER BY ev.id_evt DESC'''.format(_since, _to))
    all = cur.fetchall()
    length = len(all)

    # Создаем книку и лист.
    workbook = xlsxwriter.Workbook('registr.xlsx')
    worksheet = workbook.add_worksheet()
    
    # Заносим данные в таблицу
    row = 0
    col = 0
    for h in FOR_TABLE:
        worksheet.write(row, col, h)
        col += 1
    row += 1
    for item in all:
        col = 0
        for element in item:
            worksheet.write(row, col, element)
            col += 1
        row += 1

    worksheet.write(row, 0, date.today().strftime("%Y-%m-%d %H:%M:%S"))

    workbook.close()

    try:
        send = send_file('registr.xlsx', cache_timeout=0)
    except:
        send='Ошибка создания файла!'
    finally:
        conn.close()
    return send

# Выгружает всех зарегистрированных пользователей
@panel.route('/getallusers')
def getallusers():
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()
    cur.execute('SELECT * FROM person')
    persons = cur.fetchall()
    length = len(persons)

    # Создаем книку и лист.
    workbook = xlsxwriter.Workbook('allusers.xlsx')
    worksheet = workbook.add_worksheet()
    
    # Заносим данные в таблицу
    row = 0
    col = 0
    for h in FOR_TABLE_ALLUSERS:
        worksheet.write(row, col, h)
        col += 1
    row += 1
    for item in persons:
        col = 0
        for element in item:
            worksheet.write(row, col, element)
            col += 1
        row += 1

    worksheet.write(row, 0, date.today().strftime("%Y-%m-%d %H:%M:%S"))

    workbook.close()

    try:
        send = send_file('allusers.xlsx', cache_timeout=0)
    except:
        send='Ошибка создания файла!'
    finally:
        conn.close()
    return send

# Выгружает события по заданным срокам
@panel.route('/getsomeevents', methods=['GET', 'POST'])
def getsomeevents():
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    _since = request.form.get('since')
    _to = request.form.get('to')

    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()
    cur.execute('SELECT * FROM event WHERE date >= "{0}" AND date <= "{1}"'.format(_since, _to))
    someevents = cur.fetchall()
    length = len(someevents)

    # Создаем книку и лист.
    workbook = xlsxwriter.Workbook('someevents.xlsx')
    worksheet = workbook.add_worksheet()
    
    # Заносим данные в таблицу
    row = 0
    col = 0
    for h in FOR_TABLE_SOMEEVENTS:
        worksheet.write(row, col, h)
        col += 1
    row += 1
    for item in someevents:
        col = 0
        for element in item:
            worksheet.write(row, col, element)
            col += 1
        row += 1

    worksheet.write(row, 0, date.today().strftime("%Y-%m-%d %H:%M:%S"))

    workbook.close()

    try:
        send = send_file('someevents.xlsx', cache_timeout=0)
    except:
        send='Ошибка создания файла!'
    finally:
        conn.close()
    return send

# Выгружает зарегистрированных пользователей по конкретному событию
@panel.route('/getuserregistronevent/<id_evt>', methods=['GET', 'POST'])
def getuserregistronevent(id_evt):
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))

    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()
    cur.execute("SELECT p.id_prsn, surname_prsn, name_prsn, patronymic_prsn, faculty, email, phone, birthday, r.role FROM registration AS r JOIN person AS p ON r.id_prsn=p.id_prsn WHERE r.id_evt = {} ORDER BY surname_prsn".format(id_evt))
    userregistronevent = cur.fetchall()
    length = len(userregistronevent)

    # Создаем книку и лист.
    workbook = xlsxwriter.Workbook('userregistronevent.xlsx')
    worksheet = workbook.add_worksheet()
    
    # Заносим данные в таблицу
    row = 0
    col = 0
    for h in FOR_TABLE_USERREGISTERONEVENT:
        worksheet.write(row, col, h)
        col += 1
    row += 1
    for item in userregistronevent:
        col = 0
        for element in item:
            worksheet.write(row, col, element)
            col += 1
        row += 1

    worksheet.write(row, 0, date.today().strftime("%Y-%m-%d %H:%M:%S"))

    workbook.close()

    try:
        send = send_file('userregistronevent.xlsx', cache_timeout=0)
    except:
        send='Ошибка создания файла!'
    finally:
        conn.close()
    return send

# Выгружает посетивших конкретное событие
@panel.route('/getvisit/<id_evt>', methods=['GET', 'POST'])
def getvisit(id_evt):
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))

    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()
    cur.execute("SELECT p.id_prsn, surname_prsn, name_prsn, patronymic_prsn, faculty, email, phone, birthday, sex, year_st, classroom FROM registration AS r JOIN person AS p ON r.id_prsn=p.id_prsn WHERE r.id_evt = {} AND visit=1".format(id_evt))
    uservisit = cur.fetchall()
    length = len(uservisit)

    # Создаем книку и лист.
    workbook = xlsxwriter.Workbook('uservisit.xlsx')
    worksheet = workbook.add_worksheet()
    
    # Заносим данные в таблицу
    row = 0
    col = 0
    for h in FOR_TABLE_USERVISIT:
        worksheet.write(row, col, h)
        col += 1
    row += 1
    for item in uservisit:
        col = 0
        for element in item:
            worksheet.write(row, col, element)
            col += 1
        row += 1

    worksheet.write(row, 0, date.today().strftime("%Y-%m-%d %H:%M:%S"))

    workbook.close()

    try:
        send = send_file('uservisit.xlsx', cache_timeout=0)
    except:
        send='Ошибка создания файла!'
    finally:
        conn.close()
    return send