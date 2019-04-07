from flask import Flask, render_template, request, redirect, url_for, session     # инструменты Flask
import sqlite3                                                                    # для работы с БД SQLite
from datetime import date, timedelta                                              # класс для работы с датой
import random                                                                     # для генерации случайных чисел
import mail                                                                       # отправка сообщения для подтверждения регистрации
import checker                                                                    # проверки
from admin.admin import panel


app = Flask(__name__)
# Ключ шифорования для работы с сессиями
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# ---------------- начало скрипта ----------------- #

# I Главная страница
# Новости. Вход в личные кабинеты участников и админа. Переход к регистрации
@app.route('/')
def index():
    return render_template('index.html')

# II Панель администратора
# Управление пользователями
@app.route('/admn')
def admn():
    # является ли пользователь администратором
    if session.get('id') != 'admin':
        return '<span>Доступ закрыт. Войдите как администратор!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    return render_template('admn.html')


# Панель администратора (пользователь) - все пользователи (выводит всех пользователей из постоянной таблицы person
@app.route('/allusers')
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
@app.route('/deluser')
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
    return redirect(url_for('allusers'))


# Панель администратора (события) - выводит список всех событий
@app.route('/event')
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
@app.route('/eventadd', methods=['GET', 'POST'])
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
    
    return redirect(url_for('event'))

# Панель администратора (события) - удаление события и редирект к списку событий
@app.route('/deletevt/<id>')
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
    
    return redirect(url_for('event'))

# Панель администратора (события) - статистика регистраций на событие, списки волонтеров зарегистрировавшихся на конкретное событие
@app.route('/stat/<id_evt>')
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
@app.route('/check', methods=['GET', 'POST'])
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
    return redirect(url_for('event'))

# III Регистрация личного кабинета - регистрационная форма
@app.route('/person')
def person():
    return render_template('personadd.html')

# Регистрация личного кабинета - добавление нового пользователя во временную таблицу и отправка подтверждающего сообщения
@app.route('/personview', methods=['GET', 'POST'])
def personview():
    surname=request.form['surname']
    name=request.form['name']
    patronymic=request.form['patronymic']
    birthday=request.form['birthday']
    faculty=request.form['faculty']
    email=request.form['email']
    phone=request.form['phone']
    login=request.form['login']
    password=request.form['password']
    # получение текущей даты в iso формате
    today = date.today()
    # преобразование даты в строку
    date_reg = str(today)

    # Соединение с БД
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()

    # Удаление старых записей во временной таблице по проществии 30 дней с момента регистрации
    cur.execute("SELECT hash, date_reg FROM temp_user")
    for row in cur.fetchall():
        # преобразуем строку из базы в дату и вычитаем ее из текущей, если дельта больше 30 дней, удаляем строку
        if (date.today()-date.fromisoformat(row[1]))>timedelta(30): cur.execute("DELETE FROM temp_user WHERE hash='{}'".format(row[0]))
    # Сохраняем изменения
    conn.commit()

    # генерация случайного числа
    rand = str(random.randint(3245, 6000000))
    # убедимся, что такое число отсутствует во временной таблицы, для его уникальности.
    cur.execute('SELECT hash FROM temp_user')
    sec =[x[0] for x in cur.fetchall()]       # Генерируем список из первых элементов запрошенных строк
    while rand in sec:                        # Если сгенерированое число уже есть в таблице, генерируем новое
        rand = str(random.randint(3245, 6000000))

    # Запись переданных в форме данных во временную таблицу индексируя строку случайным числом, на него же будем ссылаться из письма с подтверждением регистрации
    cur.execute("INSERT INTO temp_user (hash, surname, name, patronymic, email, faculty, phone, birthday, login, password, date_reg) VALUES ('" +rand+ "', '" +surname+ "', '" +name+ "', '" +patronymic+ "', '" +email+ "', '" +faculty+ "', '" +phone+ "', '" +birthday+ "', '"  +login+ "', '" +password+ "', '" +date_reg+ "')")

    # Сохраняем изменения
    conn.commit()
    # Закрываем соединение с базой
    conn.close()

    #* Отправка почтового сообщения с подтверждением регистрации пользователю
    #* ссылка со сгенерированным числом, для перезаписи из временной таблицы в таблицу пользователей
    host = request.host_url.split(':')                       # парсим адрес хоста
    link=host[0]+':'+host[1]+url_for('confirm',hash=rand)    # собираем ссылку из хоста, страницы проверки и случайного числа сгенерированного для пользователя
    mail.to_volunteer(email, link)                           # функция отправки сообщения из файла mail.py
    return '<span>На ваш почтовый адрес отправлена ссылка для подтверждения регистрации</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))

# Регистрация личного кабинета - подтверждение регистрации по ссылке с почты
@app.route('/confirm/<hash>')
def confirm(hash):
     # Соединение с БД
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()
    # Нахождение записи во временной таблице temp_user по коду в ссылке подтверждения
    cur.execute('SELECT * FROM temp_user WHERE hash="{}"'.format(hash))
    row = cur.fetchone()
    if row==None: return '<span>Ваша ссылка подтверждения не действительна!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))
    # (Захешировать пароль перед перезаписью - не реализовано!)
    # Перезапись значений в постоянную таблицу person
    cur.execute('INSERT INTO person (surname_prsn, name_prsn, patronymic_prsn, faculty, email, phone, birthday, login, password, date_reg) VALUES ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", "{8}", "{9}")'.format(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
    conn.commit()
    # Удаление записи во временной таблице temp_user по коду в ссылке
    cur.execute('DELETE FROM temp_user WHERE hash="{}"'.format(hash))
    conn.commit()
    conn.close()

    # отправить логин и пароль на почтовый адрес
    mail.send_passw(row[5], row[8], row[9])    
    return redirect(url_for('index'))

# IV Авторизация - Вход в личный кабинет волонтера - Форма авторизации
@app.route('/login')
def login():
    return render_template('login.html')


# Личный кабинет волонтера - Вход - обработка формы
@app.route('/cabinetin', methods=['GET','POST'])
def cabinetin():
    # Получаем из формы логин и пароль
    login = request.form['login']
    password = request.form['password']

    # Если вход выполнил администратор (тест)    
    if checker.pswAdm(login,password):
        # Сохраняем id администратора в сессии
        session['id']='admin'
        # Переходим на страницу отображения ЛК
        return redirect(url_for('admn'))

    # Подключаемся к БД
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()

    # Делаем выборку всех записей из таблицы Пользователей
    cur.execute('SELECT * FROM person')
    persons = cur.fetchall()
    # Перебираем записи и ищем совпадение введенных логина и пароля
    for p in persons:
        if(p[8]==login and p[9]==password):
            # Сохраняем id этого пользователя в сессии
            session['id']=p[0]
            conn.close()
            # Переходим на страницу отображения ЛК
            return redirect(url_for('cabinet', action='nextevt'))
    
    conn.close()
    # Если записи не были найдены возвращаем пользователя на главную страницу.
    return '<span>Увы, но вы не зарегистрированы!</span><br /><a href="{}">Вернуться на главную страницу</a>'.format(url_for('index'))


# Личный кабинет волонтера - Внешний вид
@app.route('/cabinet/<action>')
def cabinet(action):
    # Переменная для сохранения отображаемого на странице контента
    content = ''
    # Подключаемся к базе данных
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()
    # Получаем ФИО пользователя по id записанного в сессию
    cur.execute('SELECT * FROM person WHERE id_prsn={}'.format(session['id']))
    # Сохраняем ФИО в переменную для передачи его в шаблон
    volonteer = cur.fetchone()

    if (action=='lastevt'):# отображается когда запрашиваются события которые посетил пользователь
        # Получаем пересекающиеся данные из таблиц События и Регистрации
        # и выбираем из них только те, которые посетил пользователь с id записанным в сессию
        cur = cur.execute('SELECT event.id_evt, event.event, event.activity, event.date FROM event JOIN registration ON event.id_evt=registration.id_evt WHERE registration.id_prsn={} AND registration.visit =1'.format(session['id']))
        # В переменной Контент формируем таблицу для вывода
        content = '<table><thead><th>Событие</th><th>Активность/Предмет</th><th>Дата</th><th></th></thead>'
        # Перебираем все полученные записи
        for row in cur:
            # формируем строки таблицы только из тех событий даты которых больше текущей даты
            content += '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>'.format( row[1],row[2],row[3], '<a href=''>Получить благодарность</a>')
        content += '</table>'
    elif (action=='regevt'): # отображается когда запрашивается события на которые зарегистрирован пользователь
        # Получаем пересекающиеся данные из таблиц События и Регистрации
        # и выбираем из них только те, на которые зарегистрирован пользователь с id записанным в сессию
        cur = cur.execute('SELECT event.id_evt, event.event, event.activity, event.date FROM event JOIN registration ON event.id_evt=registration.id_evt WHERE registration.id_prsn={}'.format(session['id']))
        # В переменной Контент формируем таблицу для вывода
        content = '<table><thead><th>Событие</th><th>Активность/Предмет</th><th>Дата</th><th></th></thead>'
        # Перебираем все полученные записи
        for row in cur:
            # Получаем из ячейки Дата данные и превращаем их в массив разделяя строку по точкам
            ls = row[3].split('.')
            # Инвертируем элементы массива
            ls.reverse()
            # объединяем обратно в единую строку и преобразуем в число
            ls = int(''.join(ls))
            # получаем и преобразуем в число текущую дату и сравниваем его с датой события
            if (ls>int(''.join(date.today().isoformat().split('-')))):
                delreg = '<a href="/unregistration/{}">Отменить регистрацию</a>'.format(row[0])
                # формируем строки таблицы только из тех событий даты которых больше текущей даты.
                content += '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>'.format( row[1],row[2],row[3],delreg)
        content += '</table>'
    else:    # Отображается когда показываются предстоящие события на которые можно зарегистрироваться
        # Делаем выборку событий в которх зарегистрировался пользователь с id сохранным в сессии из таблицы Регистриция
        # Из таблицы События выбираем события с id_evt  не входящим в первую выборку, т.е. те на которые данный пользователь еще не регистрировался
        cur = cur.execute('SELECT * FROM event WHERE id_evt NOT IN (SELECT id_evt FROM registration WHERE id_prsn ={})'.format(session['id']))
        # формируем переменную контент из строк вышеуказанной выборки
        content = '<table><thead><th>Событие</th><th>Активность/Предмет</th><th>Дата</th><th></th></thead>'
        for row in cur:
            ls = row[3].split('.')
            ls.reverse()
            ls = int(''.join(ls))
            if (ls>int(''.join(date.today().isoformat().split('-')))):
                reg = '<a href=/registration/{}>Зарегистрироваться</a>'.format(row[0])
                content += '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>'.format( row[1],row[2],row[3],reg)
        content += '</table>'
    # Закрываем БД и выводим шаблон ЛК передавая ФИО пользователя и контент для отображения на странице
    conn.close()
    return render_template('cabinet.html', volonteer=volonteer, content=content)


# Личный кабинет - регистрация пользователя на событие
@app.route('/registration/<id_evt>', methods=['GET', 'POST'])
def registration(id_evt):
    # Соединение с БД
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()
    # Вставка записи в таблицу регистраций
    cur.execute("INSERT INTO registration (id_prsn, id_evt) VALUES ('" +str(session['id'])+ "', '" +id_evt+ "')")
    # Сохраняем изменения
    conn.commit()
    conn.close()
    
    return redirect(url_for('cabinet', action='nextevt'))

# Личный кабинет - Отмена регистрации пользователя на событие
@app.route('/unregistration/<id_evt>', methods=['GET', 'POST'])
def unregistration(id_evt):
    # Соединение с БД
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()
    # Удаление записи в таблицу регистраций
    cur.execute("DELETE FROM registration WHERE id_prsn={} AND id_evt = {}".format(str(session['id']), id_evt))
    # Сохраняем изменения
    conn.commit()
    conn.close()
    
    return redirect(url_for('cabinet', action='regevt'))

# int(''.join(date.today().isoformat().split('-'))) # - получение числа из текущей даты, необходим следующий импорт: from datetime import date
# ----------------------- Конец скрипта ------------------------ #
if (__name__ == '__main__'):
    app.register_blueprint(panel, url_prefix='/admin')
    app.run(debug=False)
    