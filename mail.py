import smtplib as smtp
import ssl
#Библиотека для работы с кириллицей
from email.mime.text import MIMEText
from email.header    import Header
import json

def to_volunteer(destination, link):
    """to_volunteer(destination, link)"""
    # читаем файл конфиг, берем из него логин и пароль для smtp
    fp = open('conn.fig')
    s=fp.read()
    dic = json.loads(s)    
    login = dic.get('login')
    password = dic.get('password')
    fp.close()

    msg = MIMEText('Здравствуйте, вы прошли регистрирацию в системе волонтерского движения дирекции по профориентации, для завершения регистрации прейдите по ссылке {}'.format(link), 'plain', 'utf-8')
    msg['Subject'] = Header('Подтверждение регистрации волонтера', 'utf-8')
    msg['From'] = login
    msg['To'] = destination
    

    server = smtp.SMTP('localhost',25)
    server.set_debuglevel(True)
    #server.ehlo('volunteer.na4u.ru')
#    if server.has_extn('STARTTLS'):
#        server.starttls()
#        server.ehlo('volunteer.na4u.ru')
#    server.login(login, password)
    server.sendmail(login, destination, msg.as_string())
    server.quit()

def send_passw(destination:'dest_adr', log:'login', pwd:'password')->None:
    # читаем файл конфиг, берем из него логин и пароль для smtp
    fp = open('conn.fig')
    s=fp.read()
    dic = json.loads(s)    
    login = dic.get('login')
    password = dic.get('password')
    fp.close()

    msg = MIMEText('Ваша регистрация подтверждена!\n Логин: {}\n Пароль: {}'.format(log, pwd))
    msg['Subject'] = Header('Подтверждение регистрации волонтера', 'utf-8')
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
