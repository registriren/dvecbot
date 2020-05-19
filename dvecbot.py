#!/usr/bin/python
# -*- coding: utf-8 -*-

from botapitamtam import BotHandler
import smtplib as smtp
from email.mime.text import MIMEText
from email.header import Header
from datetime import date
import json
import re

config = 'config.json'
with open(config, 'r', encoding='utf-8') as c:
    conf = json.load(c)
    token = conf['access_token']
    email = conf['email']
    password = conf['password']
    dest_email = conf['dest_email']

bot = BotHandler(token)


def main():
    subject = 'Показания счетчика'
    email_text = None
    flag = 0
    #PTR = '(|([ДдНн]|[Дд][Ее][Нн][Ьь]|[Нн][Оо][Чч][Ьь])-[0-9]+(|(\.|,)[0-9]+),(| )([ДдНн]|[Дд][Ее][Нн][Ьь]|[Нн][Оо][Чч][Ьь])-)[0-9]+(|(\.|,)[0-9]+) '
    while True:
        last_update = bot.get_updates()
        today = date.today()
        data = today.strftime("%d")
        if data != '20':
            flag = 0
        if data == '20' and flag == 0:
            for i in conf['id_a']:
                bot.send_message('Напоминаю об отправке показаний электросчётчика с 20 по 25 число', chat_id=None,
                                 user_id=i)
                flag = 1
        if last_update:
            dat = today.strftime("%d.%m.%Y")
            type_upd = bot.get_update_type(last_update)
            text = bot.get_text(last_update)
            chat_id = bot.get_chat_id(last_update)
            payload = bot.get_payload(last_update)
            sender = bot.get_user_id(last_update)
            callback_id = bot.get_callback_id(last_update)
            if sender in conf['id_a']:
                if type_upd == 'bot_started':
                    bot.send_message(u'Это бот для удобной передачи показаний\n' +
                                     'электрических счетчиков в ДЭК г. Хабаровск.\n' +
                                     'Подробности в /help', chat_id)
                    text = None
                if text == '/help':
                    bot.send_message(u'Введите показания счетчика. Например: день-1234, ночь-0123 ', chat_id)
                    text = None
                if type_upd == 'message_created' and text:  # and sender in id_a:
                    #print(text)
                    #print(re.fullmatch(PTR, text))
                    if len(text) < 30: # and re.fullmatch(PTR, text):
                        email_text = 'Номер лицевого счёта: {}\nАдрес: {}\nФИО: {}\nДата снятия показаний: {}\nПоказания счетчика: {}'.format(
                            conf['ls'][str(sender)],
                            conf['adr'][str(sender)],
                            conf['fio'][str(sender)],
                            dat,
                            text)
                        bot.send_message(u'Данные будут направлены по адресу: {}'.format(dest_email), chat_id)
                        bot.send_message(u'{}'.format(email_text), chat_id)
                        buttons = [[{"type": 'callback',
                                     "text": 'Да',
                                     "payload": 'yes'},
                                    {"type": 'callback',
                                     "text": 'Нет',
                                     "payload": 'no'}]]
                        upd = bot.send_buttons('Отправить?', buttons, chat_id)
                        mid = bot.get_message_id(upd)
                    else:
                        bot.send_message('Формат данных неверный, смотри /help', chat_id)
                if payload == 'yes' and email_text:
                    bot.send_answer_callback(callback_id, 'отправляю...')
                    email_text = email_text + '\n\nОтправлено с помощью бота @dvecbot для мессенджера ТамТам'
                    # bot.send_message(u' отправляю...', chat_id)
                    bot.delete_message(mid)
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
                    # email_text = None
                elif payload == 'no':
                    bot.delete_message(mid)
                    bot.send_message(u'Жду новые данные...', chat_id)
                    # email_text = None
            else:
                bot.send_message('Доступ запрещён!', chat_id)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
