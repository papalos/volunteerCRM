from flask import Blueprint, Flask, render_template, request, redirect, url_for, session, send_file     # инструменты Flask
import sqlite3                                                                    # для работы с БД SQLite
from datetime import date, timedelta                                              # класс для работы с датой
import random                                                                     # для генерации случайных чисел
# import mail                                                                       # отправка сообщения для подтверждения регистрации
# import checker                                                                    # проверки
import xlsxwriter                                                                 # создание документа .xmlx


cabin = Blueprint('user', __name__, template_folder='templates')


############## Личные кабинеты пользователей ############
# Личный кабинет волонтера - Внешний вид
@cabin.route('/cabinet/<action>')
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
                delreg = '<a href="/us/unregistration/{}">Отменить регистрацию</a>'.format(row[0])
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
                reg = '<a href=/us/registration_view/{}>Зарегистрироваться</a>'.format(row[0])
                content += '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td></tr>'.format( row[1],row[2],row[3],row[4],row[11],reg)
        content += '</tbody></table>'
    # Закрываем БД и выводим шаблон ЛК передавая ФИО пользователя и контент для отображения на странице
    conn.close()
    return render_template('cabinet.html', volonteer=volonteer, content=content)

# Личный кабинет - регистрация пользователя на событие
@cabin.route('/registration_view/<id_evt>', methods=['GET', 'POST'])
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
@cabin.route('/registration', methods=['GET', 'POST'])
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
    
    return redirect(url_for('user.cabinet', action='nextevt'))

# Личный кабинет - Отмена регистрации пользователя на событие
@cabin.route('/unregistration/<id_evt>', methods=['GET', 'POST'])
def unregistration(id_evt):
    # Соединение с БД
    conn = sqlite3.connect("sql/volonteer.db")
    cur = conn.cursor()
    # Удаление записи в таблицу регистраций
    cur.execute("DELETE FROM registration WHERE id_prsn={} AND id_evt = {}".format(str(session['id']), id_evt))
    # Сохраняем изменения
    conn.commit()
    conn.close()
    
    return redirect(url_for('user.cabinet', action='regevt'))