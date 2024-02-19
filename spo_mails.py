import imaplib
import email
from email.header import decode_header
import os
from datetime import datetime
from datetime import datetime, timedelta
from email.parser import BytesParser
from email import policy
import base64
from html.parser import HTMLParser
import os
import sys
import configparser

config = configparser.ConfigParser()
config.sections()
config.read('config.ini')


base_path = os.path.dirname(os.path.abspath(__file__))


def mail_grabber():
    class MLStripper(HTMLParser):
        def __init__(self):
            super().__init__()
            self.reset()
            self.strict = False
            self.convert_charrefs = True
            self.fed = []
        def handle_data(self, d):
            self.fed.append(d)
        def get_data(self):
            return ''.join(self.fed)

    def strip_tags(html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()



    # Получение вчерашней даты
    yesterday = datetime.now() - timedelta(1)
    date = yesterday.strftime("%d-%b-%Y")  # Формат даты: День-Месяц-Год


    # Параметры подключения к серверу IMAP
    imap_host = config['Mail']['imap_host']  # Замените на адрес вашего IMAP сервера
    imap_user = config['Mail']['imap_user']  # Замените на ваше имя пользователя
    imap_pass = config['Mail']['imap_pass']  # Замените на ваш пароль

    # Подключение к серверу без SSL
    mail = imaplib.IMAP4(imap_host)
    mail.login(imap_user, imap_pass)

    # Выбор почтового ящика (например, INBOX)
    mail.select('inbox')

    # Поиск писем с сегодняшней датой и определенной темой
    # date = datetime.now().strftime("%d-%b-%Y") - timedelta(1)  # Формат даты: День-Месяц-Год
    yesterday = datetime.now() - timedelta(1)
    date = yesterday.strftime("%d-%b-%Y")  # Формат даты: День-Месяц-Год


    subject_keyword = '[Support-ocs-spo] Check_SPO'
    typ, data = mail.search(None, '(SENTON "{}" SUBJECT "{}")'.format(date, subject_keyword))


    # Создание директории для сохранения писем
    directory = f"{base_path}/SPO_{datetime.now().strftime('%Y%m%d')}"
    if os.path.exists(directory):
        print("Директория уже существует. Скрипт будет остановлен.")
        sys.exit()
        return False
    else:
        os.makedirs(directory)

    # Извлечение и сохранение писем
    for num in data[0].split():
        typ, msg_data = mail.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        subject = decode_header(msg["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()

        # Формирование имени файла для сохранения письма
        filename = f"{directory}/{subject}.txt"

        # Сохранение письма в файл
        with open(filename, 'w', encoding='utf-8') as file:
            body = ''

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        body += part.get_payload(decode=True).decode(part.get_content_charset(), errors='ignore')
                    elif part.get_content_type() == 'text/html':
                        html_content = base64.b64decode(part.get_payload()).decode(part.get_content_charset(), errors='ignore')
                        body += strip_tags(html_content)
            else:
                content_transfer_encoding = msg.get('Content-Transfer-Encoding')
                if content_transfer_encoding == 'base64':
                    body = base64.b64decode(msg.get_payload()).decode(msg.get_content_charset(), errors='ignore')
                else:
                    body = msg.get_payload(decode=True).decode(msg.get_content_charset(), errors='ignore')

            file.write(body)

    # Закрытие соединения
    mail.close()
    mail.logout()

mail_grabber()
