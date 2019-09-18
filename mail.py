import smtplib as smtp
import ssl
#Библиотека для работы с кириллицей
from email.mime.text import MIMEText
from email.header    import Header
import json

def to_volunteer(destination, link, name):
    """to_volunteer(destination, link)"""
    # читаем файл конфиг, берем из него логин и пароль для smtp
    fp = open('conn.fig')
    s=fp.read()
    dic = json.loads(s)    
    login = dic.get('login')
    password = dic.get('password')
    fp.close()

    msg = MIMEText('Привет, {0}! \n\nТы прошел(-ла) регистрацию в системе волонтерского движения на олимпиадах и конкурсах НИУ ВШЭ. Для завершения регистрации перейди по ссылке {1} \n\nЭто автоматически сгенерированное письмо, не нужно отвечать на него. Если у тебя возникли трудности, напиши на olymp@hse.ru. \n--- \nДирекция по профориентации \nolymp@hse.ru'.format(name, link), 'plain', 'utf-8')
    msg['Subject'] = Header('Волонтерское движение: подтверждение регистрации', 'utf-8')
    msg['From'] = login
    msg['To'] = destination
    

    server = smtp.SMTP('localhost',25)
    server.set_debuglevel(True)
    server.sendmail(login, destination, msg.as_string())
    server.quit()

def send_passw(destination:'dest_adr', log:'login', pwd:'password', name)->None:
    # читаем файл конфиг, берем из него логин и пароль для smtp
    fp = open('conn.fig')
    s=fp.read()
    dic = json.loads(s)    
    login = dic.get('login')
    password = dic.get('password')
    fp.close()

    msg = MIMEText('Привет, {0}! \n\nТвоя регистрация в системе волонтерского движения на олимпиадах и конкурсах НИУ ВШЭ подтверждена!\n\n Логин: {1}\n Пароль: {2} \nСпасибо за регистрацию! Зайди в личный кабинет: {3}, чтобы зарегистрироваться на мероприятия. \n\nДо встречи на олимпиаде! \n\nЭто автоматически сгенерированное письмо, не нужно отвечать на него. Если у тебя возникли трудности, напиши на olymp@hse.ru. \n--- \nДирекция по профориентации olymp@hse.ru'.format(name, log, pwd, 'https://volunteer.na4u.ru/login'))
    msg['Subject'] = Header('Волонтерское движение: Логин и пароль', 'utf-8')
    msg['From'] = login
    msg['To'] = destination

    server = smtp.SMTP('localhost',25)
    server.sendmail(login, destination, msg.as_string())
    server.quit


def send_recovery(destination:'dest_adr', log:'login', pwd:'password')->None:
    # читаем файл конфиг, берем из него логин и пароль для smtp
    fp = open('conn.fig')
    s=fp.read()
    dic = json.loads(s)    
    login = dic.get('login')
    password = dic.get('password')
    fp.close()

    msg = MIMEText('Дорогой Волонтер! \n\nНапоминаем твои учетные данные в системе волонтерского движения на олимпиадах и конкурсах НИУ ВШЭ.\n\n Логин: {}\n Пароль: {} \n\nЛичный кабинет: https://volunteer.na4u.ru/login \n\nДо встречи на олимпиаде! \n\nЭто автоматически сгенерированное письмо, не нужно отвечать на него. Если у тебя возникли трудности, напиши на olymp@hse.ru. \n\n--- \nДирекция по профориентации olymp@hse.ru'.format(log, pwd))
    msg['Subject'] = Header('Восстановление учетных данных', 'utf-8')
    msg['From'] = login
    msg['To'] = destination

    server = smtp.SMTP('localhost',25)
#    server.ehlo()
#    if server.has_extn('STARTTLS'):
#        server.starttls()
#        server.ehlo()
#    server.login(login, password)
    server.sendmail(login, destination, msg.as_string())
    server.quit()

if __name__ == '__main__':
    to_volunteer('patro1@yandex.ru', 'какая-нибудь сгенерированя херобуда')
    send_passw('patro1@yandex.ru', 'ух ты', 'мы вышли из бухты')
