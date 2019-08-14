#!/usr/bin/python
# -*- coding: utf-8 -*-

from botapitamtam import BotHandler
import smtplib as smtp
from email.mime.text import MIMEText
from email.header import Header
from datetime import date
import json

config = 'config.json'
with open(config, 'r', encoding='utf-8') as c:
    conf = json.load(c)
    token = conf['access_token']
    email = conf['email']
    password = conf['password']
    dest_email = conf['dest_email']
    ls = conf['ls']
    adr = conf['adr']
    fio = conf['fio']
    id_a = conf['id_a']

subject = 'Показания счетчика'
email_text = None

bot = BotHandler(token)

def body():
    if type_upd == 'bot_started':
            bot.send_message(u'Это бот для удобной передачи показаний\n' +
                                'электрических счетчиков в ДЭК г. Хабаровск.\n' +
                                'Подробности в /help', chat_id)
            text = None
        if text == '/help':
            bot.send_message(u'Введите показания счетчика цифрами', chat_id)
            text = None
        if type_upd == 'message_created' and text != None: #and sender in id_a:
            email_text = 'Номер лицевого счёта: {}\nАдрес: {}\nФИО: {}\nДата снятия показаний: {}\nПоказания счетчика: {}'.format(
                            ls,
                            adr,
                            fio,
                            dat,
                            text)
            bot.send_message(u'Данные будут направлены по адресу: {}'.format(dest_email), chat_id)
            bot.send_message(u'{}'.format(email_text), chat_id)
            buttons = [{"type": 'callback',
                        "text": 'Да',
                        "payload": 'yes'},
                       {"type": 'callback',
                        "text": 'Нет',
                        "payload": 'no'}]
            bot.send_buttons('Отправить?', buttons, chat_id)
        if payload == 'yes' and email_text != None:
            bot.send_message(u' отправляю...', chat_id)
            msg = MIMEText(email_text, 'plain', 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = email
            msg['To'] = dest_email
            server = smtp.SMTP_SSL('smtp.yandex.ru')
            server.set_debuglevel(1)
            server.ehlo(email)
            server.login(email, password)
            server.auth_plain()
            server.sendmail(msg['From'], dest_email, msg.as_string())
            server.quit()
            bot.send_message(u'Ваши показания переданы', chat_id)
            email_text = None
        elif payload == 'no':
            bot.send_message(u'Жду новые данные...', chat_id)
            email_text = None
    

def main():

    while True:
        last_update = bot.get_updates()
        if last_update == None: #проверка на пустое событие, если пусто - возврат к началу цикла
            continue
        today = date.today()
        dat = today.strftime("%d.%m.%Y")
        type_upd = bot.get_update_type(last_update)
        text = bot.get_text(last_update)
        chat_id = bot.get_chat_id(last_update)
        payload = bot.get_payload(last_update)
        sender = bot.get_user_id(last_update)
        
        if sender in id_a:
            body()
        else:
            bot.send_message('Доступ запрещён!', chat_id)
        
        

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()

