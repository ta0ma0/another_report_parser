import re
import os
from datetime import datetime
import write_to_db
from write_to_db import create_connection, write
import spo_mails

if spo_mails.mail_grabber() == False:
    exit()

mysql_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
server_data = {}
server_data_list = []

def conventer(value):
    if re.match(r'.*M$', value):
        line = value.split('M')
        try:
            line_mb = float(line[0]) / 1024
        except ValueError:
            line_correct = line[0].split(',')
            line_correct = line_correct[0]+'.'+line_correct[1]
            line_mb = float(line_correct) / 1024
            return round(line_mb, 3)

        return round(line_mb, 3)
        
    elif re.match(r'.*T$', value):
        line = value.split('T')

        try:
            line_tb = float(line[0]) * 1024
        except ValueError:
            line_correct = line[0].split(',')
            line_correct = line_correct[0]+'.'+line_correct[1]
            line_tb = float(line_correct) * 1024
            return round(line_tb, 3)

        return round(line_tb, 3)
        
    elif re.match(r'.*%$', value):
        line = value.split('%')
        try:
            line_perscent = float(line[0])
        except ValueError:
            try:
                line_correct = line[0].split(',')
            except ValueError:
                line_correct = line_correct[0]+'.'+line_correct[1]
                line_perscent = float(line_correct)
                return round(line_perscent, 3)
        return round(line_perscent, 3)

    elif re.match(r'.*K$', value):
        line = value.split('K')
        try:
            line_kb = float(line[0]) / 1024 / 1024
        except ValueError:
            line_correct = line[0].split(',')
            line_correct = line_correct[0]+'.'+line_correct[1]
            line_kb = float(line_correct) / 1024 / 1024
            return round(line_kb, 5)
        return round(line_kb, 5)

    else:
        line = value.split('G')
        try:
            line_gb = float(line[0])
        except ValueError:
            line_correct = line[0].split(',')
            line_correct = line_correct[0]+'.'+line_correct[1]
            line_gb = float(line_correct)
            return round(line_gb, 3)
        return round(line_gb, 3)


def get_file_list(last_directory):
    """
    Retrieves list of files in the current directory.

    Returns:
    List of files in the current directory.
    """
    return [f for f in os.listdir(last_directory) if os.path.isfile(os.path.join(last_directory, f))]
    

def get_latest_spo_directory():
    """
    Retrieves the latest SPO_ directory based on the modification time.

    Returns:
    The name of the latest SPO_ directory.
    """
    # Список директорий, начинающихся на SPO_, с их путями и временем последней модификации
    spo_directories = [(d, os.path.getmtime(d)) for d in os.listdir('.') if os.path.isdir(d) and d.startswith('SPO_')]
    
    # Находим директорию с самым поздним временем модификации
    if spo_directories:
        latest_directory = max(spo_directories, key=lambda x: x[1])[0]
        return latest_directory
    else:
        return None  # Возвращаем None, если подходящих директорий не найдено

def extract_project_name(filename):
    """
    Извлекает имя проекта из имени файла.

    Args:
    filename: Имя файла.

    Returns:
    Имя проекта.
    """
    match = re.search(r'SPO\s+([\w-]+)\.', filename)
    if match:
        return match.group(1)
    else:
        return None


# filename = '[Support-ocs-spo] Check_SPO omg-kv.txt'
# project_name = extract_project_name(filename)

# if project_name:
#     print(f"Имя проекта: {project_name}")
# else:
#     print(f"Не удалось извлечь имя проекта из имени файла: {filename}")


def parse_disk_space_info(text):
    """
    Parses disk space information from the given text.

    Args:
        text: Text containing disk space information.

    Returns:
        Dictionary containing server name and disk space information.
    """
    try:
        server_name = re.search(r'Сервер:\s+(.*)', text).group(1)
    except AttributeError:
        server_name = None
        pass
    disk_space_info = [line for line in text.splitlines() if (line.startswith('/') or line.endswith('/')) and re.match(r'^.*%.*$', line)]
    return {
        'server_name': server_name,
        'disk_space_info': disk_space_info,
    }


def get_servers_info(filename):
    """
    Retrieves server information from the given file.

    Args:
      filename: Name of the file containing server information.

    Returns:
      List of dictionaries with server information.
    """
    with open(last_directory + '/' + filename, 'r') as file:
        file_content = file.read()
    servers_info = [parse_disk_space_info(text_block) for text_block in file_content.split('Отчёт SPO по проекту') if text_block.strip()]
    return servers_info


# Пример использования
last_directory = get_latest_spo_directory()
print(f"Последний SPO_ директорий: {last_directory}")
filenames = get_file_list(last_directory)
print(filenames)




def parser(filenames):
    server_data_list = []  # Убедись, что этот список инициализирован в начале функции
    for el in filenames:
        servers_info = get_servers_info(el)
        for server_info in servers_info:
            project_name = extract_project_name(el)
            if server_info['disk_space_info'] and project_name is not None:
                print(f"{project_name}: {server_info['server_name']}")
                for line in server_info['disk_space_info']:
                    split_line = line.split()
                    if (project_name == 'll7' or project_name == 'blg' or project_name == 'sg') and split_line[4] == '/':
                        split_line = ['N/A'] + split_line
                    
                    server_data = {}  # Создание нового словаря для каждого набора данных
                    server_data['proj'] = project_name
                    server_data['server'] = server_info['server_name']
                    server_data['file_system'] = split_line[0]
                    server_data['whole_size'] = conventer(split_line[1])
                    server_data['used'] = conventer(split_line[2])
                    server_data['avalible'] = conventer(split_line[3])
                    try:
                        server_data['used_percent'] = conventer(split_line[4])
                    except IndexError:
                        server_data['used_percent'] = conventer(split_line[3])
                    server_data['mounted'] = split_line[5]
                    server_data['datetime'] = mysql_datetime  # Убедись, что переменная mysql_datetime инициализирована до этого места
                    server_data_list.append(server_data)
                    # print(server_data)
    return server_data_list  # Перемести возвращение списка за пределы всех циклов

        # return server_data_list

# for el in parser(filenames):
#     print(el)
# print(conventer('86%'))
parser(filenames)
server_data = parser(filenames)
conncetion = write_to_db.create_connection()
for el in server_data:
    # print(el)
    query = """INSERT INTO space_monitoring (project, server, file_system, whole_size, used, avalible, used_percent, mount_point, date_check) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    values = (el['proj'], el['server'], el['file_system'], el['whole_size'], el['used'], el['avalible'], el['used_percent'], el['mounted'], el['datetime'])
    write_to_db.write(conncetion, query, values)
    # print(conncetion, query, values)