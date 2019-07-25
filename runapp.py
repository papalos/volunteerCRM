from flask import Flask, render_template, request, redirect, url_for, session     # инструменты Flask
import sqlite3                                                                               # для работы с БД SQLite
from datetime import date, timedelta                                                         # класс для работы с датой
import random                                                                                # для генерации случайных чисел
import mail                                                                                  # отправка сообщения для подтверждения регистрации
import checker                                                                               # проверки
from admin.admin import panel


app = Flask(__name__)
# Ключ шифорования для работы с сессиями
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

app.register_blueprint(panel, url_prefix='/admin')

# ---------------- начало скрипта ----------------- #

# I Главная страница
# Новости. Вход в личные кабинеты участников и админа. Переход к регистрации
@app.route('/')
def index():
    conn = sqlite3.connect('sql/volonteer.db')
    cur=conn.cursor()
    cur.execute('SELECT * FROM news ORDER BY id DESC')
    news = cur.fetchall()
    return render_template('index.html', news=news)




# Тестовая функция для проверки адресов!!!!!!!!!!
@app.route('/xxx')
def xxx():
    conn = sqlite3.connect('sql/volonteer.db')
    cur=conn.cursor()
    cur.execute('SELECT email FROM person')
    mails = cur.fetchall()
    mail = [i[0] for i in mails]
    return str(request.args['mail'] in mail)


# II Панель администратора
# Управление пользователями
# @app.route('/admn') # def admn(): # - Перенесена в blueprint admin


# Панель администратора (пользователь) - все пользователи (выводит всех пользователей из постоянной таблицы person
# @app.route('/allusers') # def allusers(): # - Перенесена в blueprint admin

# Панель администратора (пользователь) - удаляет пользователя из постоянной таблицы person
# @app.route('/deluser') # def deluser(): # - Перенесена в blueprint admin


# Панель администратора (события) - выводит список всех событий
# @app.route('/event') # def event(): # - Перенесена в blueprint admin


# Панель администратора (события) - выполняет добавление нового события и редирект к списку всех событий
# @app.route('/eventadd', methods=['GET', 'POST']) # def eventadd(): # - Перенесена в blueprint admin


# Панель администратора (события) - удаление события и редирект к списку событий
# @app.route('/deletevt/<id>') # def deletevt(id): # - Перенесена в blueprint admin


# Панель администратора (события) - статистика регистраций на событие, списки волонтеров зарегистрировавшихся на конкретное событие
# @app.route('/stat/<id_evt>') # def stat(id_evt): # - Перенесена в blueprint admin


# Панель администратора (события) - отметить волонтера на событии
# @app.route('/check', methods=['GET', 'POST']) # def check():
    

# III Регистрация личного кабинета - регистрационная форма
@app.route('/person')
def person():
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()
    cur.execute('SELECT * FROM faculty')
    facultes = cur.fetchall()
    conn.close()
    return render_template('personadd.html', facultes=facultes)

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
    sex=request.form['sex']
    year_st=request.form['year_st']

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
    cur.execute("INSERT INTO temp_user (hash, surname, name, patronymic, email, faculty, phone, birthday, login, password, date_reg, sex, year_st) VALUES ('" +rand+ "', '" +surname+ "', '" +name+ "', '" +patronymic+ "', '" +email+ "', '" +faculty+ "', '" +phone+ "', '" +birthday+ "', '"  +login+ "', '" +password+ "', '" +date_reg+ "', '" +sex+ "', '" +year_st+ "')")

    # Сохраняем изменения
    conn.commit()
    # Закрываем соединение с базой
    conn.close()
    
    #* Отправка почтового сообщения с подтверждением регистрации пользователю
    #* ссылка со сгенерированным числом, для перезаписи из временной таблицы в таблицу пользователей
    host = request.host_url.split(':')                    # парсим адрес хоста
    link=host[0]+':'+host[1]+'confirm/'+rand              # собираем ссылку из хоста, страницы проверки и случайного числа сгенерированного для пользователя
    
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
    cur.execute('INSERT INTO person (surname_prsn, name_prsn, patronymic_prsn, faculty, email, phone, birthday, login, password, date_reg, sex, year_st) VALUES ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", "{8}", "{9}", "{10}", "{11}")'.format(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12]))
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
    if (session.get('id')):
        if session.get('id')=='admin':
            return redirect(url_for('administrator.index_adm'))
        else:
            return redirect(url_for('cabinet',action='1'))
    return render_template('login.html')

@app.route('/unlogin')
def unlogin():
    if (session.get('id')):
        del session['id']
    return redirect(url_for('index'))

# Восстановление логина и пароля по почте
@app.route('/recovery')
def recovery():
    return render_template('recovery.html', message = '')

# Отправка почты
@app.route('/recovery_send', methods=['GET','POST'])
def recovery_send():
    email = request.form.get('email')
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()

    # Делаем выборку всех записей из таблицы Пользователей
    cur.execute('SELECT login, password FROM person WHERE email = "{0}"'.format(email))
    data_reg = cur.fetchone()

    if(data_reg == None):
        return render_template('recovery.html', message='Указанный адрес в базе данных не найден')
    else:
        mail.send_recovery(email, data_reg[0], data_reg[1])
        return render_template('recovery.html', message='Логин и пароль отправлены на вашу почту')

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
        return redirect(url_for('administrator.index_adm'))    
    
    

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
        content = '<table class="table table-striped"><thead><th>Событие</th><th>Активность/Предмет</th><th>Дата</th><th>Код подтверждения</th></thead><tbody>'
        # Перебираем все полученные записи
        for row in cur:
            # формируем код подтверждения посещения состоит из id события, даты события, id участника
            a,b,c = row[3].split('-')
            ls = (str(row[0]),str(int(c)),str(int(a)-2010),str(session['id']),str(int(b)))
            code = '-'.join(ls)
            # формируем строки таблицы только из тех событий даты которых больше текущей даты
            content += '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>'.format( row[1],row[2],row[3],code)
        content += '</tbody></table>'
    elif (action=='regevt'): # отображается когда запрашивается события на которые зарегистрирован пользователь
        # Получаем пересекающиеся данные из таблиц События и Регистрации
        # и выбираем из них только те, на которые зарегистрирован пользователь с id записанным в сессию
        cur = cur.execute('SELECT event.id_evt, event.event, event.activity, event.date, registration.role FROM event JOIN registration ON event.id_evt=registration.id_evt WHERE registration.id_prsn={}'.format(session['id']))
        # В переменной Контент формируем таблицу для вывода
        content = '<table class="table table-striped"><thead><th>Событие</th><th>Активность/Предмет</th><th>Дата</th><th>Роль</th><th></th></thead><tbody>'
        # Перебираем все полученные записи
        for row in cur:
            # Получаем из ячейки Дата данные и превращаем их в массив разделяя строку по точкам
            ls = row[3].split('-')
            # объединяем обратно в единую строку и преобразуем в число
            ls = int(''.join(ls))
            # получаем и преобразуем в число текущую дату и сравниваем его с датой события
            if (ls>int(''.join(date.today().isoformat().split('-')))):
                delreg = '<a href="/unregistration/{}">Отменить регистрацию</a>'.format(row[0])
                # формируем строки таблицы только из тех событий даты которых больше текущей даты.
                content += '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td></tr>'.format( row[1],row[2],row[3],row[4], delreg)
        content += '</tbody></table>'
    else:    # Отображается когда показываются предстоящие события на которые можно зарегистрироваться
        # Делаем выборку событий в которх зарегистрировался пользователь с id сохранным в сессии из таблицы Регистриция
        # Из таблицы События выбираем события с id_evt  не входящим в первую выборку, т.е. те на которые данный пользователь еще не регистрировался
        cur = cur.execute('SELECT * FROM event WHERE id_evt NOT IN (SELECT id_evt FROM registration WHERE id_prsn ={})'.format(session['id']))
        # формируем переменную контент из строк вышеуказанной выборки
        content = '<table class="table table-striped"><thead><th>Событие</th><th>Активность/Предмет</th><th>Дата</th><th>Время прихода</th><th>Адрес</th><th></th></thead><tbody>'
        for row in cur:
            ls = row[3].split('-')
            ls = int(''.join(ls))
            if (ls>int(''.join(date.today().isoformat().split('-')))):
                reg = '<a href=/registration_view/{}>Зарегистрироваться</a>'.format(row[0])
                content += '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td></tr>'.format( row[1],row[2],row[3],row[4],row[11],reg)
        content += '</tbody></table>'
    # Закрываем БД и выводим шаблон ЛК передавая ФИО пользователя и контент для отображения на странице
    conn.close()
    return render_template('cabinet.html', volonteer=volonteer, content=content)

# Личный кабинет - регистрация пользователя на событие
@app.route('/registration_view/<id_evt>', methods=['GET', 'POST'])
def registration_view(id_evt):
    if(session.get('id') is None):
        return 'Ошибка идентификации вернитесь на <a href="{}">главную страницу</a>'.format(url_for('index'))
    conn = sqlite3.connect("sql/volonteer.db")
    curI = conn.cursor()
    curII = conn.cursor()
    currIII = conn.cursor()
    
    # Получаем ФИО пользователя по id записанного в сессию
    curI.execute('SELECT * FROM person WHERE id_prsn={}'.format(session['id']))
    # Получаем данные о событии по его id
    curII.execute('SELECT * FROM event WHERE id_evt={}'.format(id_evt))
    # Количество регистраций на определенное событие по его id
    currIII.execute('SELECT role FROM registration WHERE id_evt={}'.format(id_evt))
    # Сохраняем ФИО в переменную для передачи его в шаблон
    volonteer = curI.fetchone()
    event = curII.fetchone()
    num_evt = [x[0] for x in currIII.fetchall()]
    num_staff = num_evt.count('штаб')
    num_classroom = num_evt.count('аудитория')
    
    conn.close()

    return  render_template('registration_view.html', volonteer=volonteer, event=event, num_staff = num_staff, num_classroom = num_classroom)

# Личный кабинет - регистрация пользователя на событие
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    role = request.form.get('role')
    # Соединение с БД
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()
    # Вставка записи в таблицу регистраций
    cur.execute("INSERT INTO registration (id_prsn, id_evt, role) VALUES ('" +str(session['id'])+ "', '" +request.form.get('id_evt')+ "', '" +role+ "')")
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


# ----------------------- Конец скрипта ------------------------ #
if (__name__ == '__main__'):
    
    app.run(debug=True)