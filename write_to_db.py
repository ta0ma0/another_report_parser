import configparser
import mysql.connector
from mysql.connector import Error


config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

host = config['MySQL']['host']
user = config['MySQL']['user']
password = config['MySQL']['password']
database = config['MySQL']['database']


def create_connection():
    """Создает соединение с базой данных."""
    try:
        connection = mysql.connector.connect(
            host=host, # Замените на ваш хост
            database=database, # Замените на вашу базу данных
            user=user, # Ваш MySQL пользователь
            password=password # Ваш MySQL пароль
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)


def write(connection, query, values):
    """Записывает данные в базу данных."""
    cursor = connection.cursor()
    print(query, values)
    cursor.execute(query, (values))
    connection.commit()
    print("Данные успешно записаны в базу данных.")
