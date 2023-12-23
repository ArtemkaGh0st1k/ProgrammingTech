import sqlite3
import telebot
from telebot import types
import matplotlib.pyplot as plt
import numpy as np
from russian_names import RussianNames
import random
import os.path
import openpyxl

# статические массивы кнопок
list_command = ['Узнать данные о студенте(ах)',
                'Внести данные о новом студенте',
                'Удалить данные о студенте',
                'Посмотреть таблицу']

object_list = [ "Математический анализ",
                "Физика.Механика",
                "Физика.Термодинамика",
                "Физика.Оптика",
                "Линейная алгебра", 
                "Технологии программирования", 
                "Дифференциальные уравнения"]

pick_delete_comand = ['По предмету',
                      'По семместру',
                      'Полностью студента']

# /переменные, который нужны в дальнейшем в алгоритме
pick_name_surname = None
type_command = None #костыль, чтобы вызвать определённую функцию
type_delete_command = None
pick_object = None
list_name_surname = []


#проверка на создание файла базы данных
if (not os.path.exists('server.db')):

    #создание локальной базы данных
    db = sqlite3.connect('server.db')
    sql = db.cursor()

    sql.execute( """CREATE TABLE IF NOT EXISTS student (
                name_first TEXT,
                semmestr INTEGER,
                object TEXT,
                average_mark INTEGER,
                name_group INTEGER,
                name_last TEXT
    )""" )
    db.commit()

    rus_names = RussianNames(count = 15).get_batch()

    local_group = random.randint(1,100)
    for rn in rus_names:
        local_name = rn.split(" ")[0]
        local_surname = rn.split(" ")[2]

        local_semmestr = 1
        for i in range(len(object_list)):
            
            local_object_list = object_list[local_semmestr-1]
            local_mark = random.uniform(2.0, 5.0)

            sql.execute("""INSERT INTO student (name_first, semmestr, object, average_mark, name_group, name_last) VALUES (?, ?, ?, ?, ?, ?)""",
            (local_name,local_semmestr, local_object_list, local_mark, local_group, local_surname))

            local_semmestr+= 1
        
        db.commit()
     
    sql.execute("""SELECT * FROM student ORDER BY name_first""")
    db.commit()
    db.close()

    
# передаём токен боту
token = '6469443130:AAHydTKZZSaXEp-CUxusQBiGgxO0k7CNGVc'
bot = telebot.TeleBot('6469443130:AAHydTKZZSaXEp-CUxusQBiGgxO0k7CNGVc') 


# вспомагательная функция
# /help -> в чат
@bot.message_handler(commands=['help'])
def help_handler(message):
    chat_id = message.chat.id

    if message.from_user.last_name != None:
        bot.send_message(chat_id, "Привет" + " " + f"{message.from_user.first_name}" + " " 
                        + f"{message.from_user.last_name} " + "(" 
                        + f"{message.from_user.username}" + ")" + ".\n" 
                        + "Моя основная цель это предоставление информации о студентах\n" 
                        + "Чтобы подробнее ознакомится с моими возможностями, воспользуйся" + " " 
                        + "командой /start")
    else:
       bot.send_message(chat_id, "Привет" + " " + f"{message.from_user.first_name}" + " " + "(" 
                        + f"{message.from_user.username}" + ")" + ".\n" 
                        + "Моя основная цель это предоставление информации о студентах\n" 
                        + "Чтобы подробнее ознакомится с моими возможностями, воспользуйся" + " " 
                        + "командой /start")

# основная функция
# /start -> в чат
count_start = 0
@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id

    global count_start
    count_start+=1
    if count_start!=1:
        list_name_surname.clear()

    markup = types.ReplyKeyboardMarkup(row_width=1)
    button1 = types.KeyboardButton(list_command[0])
    button2 = types.KeyboardButton(list_command[1])
    button3 = types.KeyboardButton(list_command[2])
    button4 = types.KeyboardButton(list_command[3])
    
    markup.add(button1,button2,button3,button4)

    bot.send_message(chat_id, 'Список команд', reply_markup=markup)

#ловит вводимые данные при /start
@bot.message_handler(regexp=(r'Узнать данные|Внести данные|Удалить данные|Посмотреть таблицу'))
def button_handler(message):
    chat_id = message.chat.id
    text = message.text
    global list_name_surname
    global type_command

    # Проверка на работоспособность базы данных
    try:
        db = sqlite3.connect('server.db')
        sql = db.cursor()
    except Exception as e:
        bot.send_message(chat_id, e)
        return
    finally:
        if text == list_command[0]:
            type_command = 1

            sql.execute("""SELECT DISTINCT name_first, name_last FROM student ORDER BY name_first""")
            local_listQuery = sql.fetchall()

            local_name = []
            local_surname = []
            for elem in local_listQuery:
                local_name.append(elem[0])
                local_surname.append(elem[1])

            markup = types.ReplyKeyboardMarkup()

            #если не пустой список
            if list_name_surname:
                list_name_surname.clear()

            for i in range(len(local_listQuery)):
                markup.add(types.KeyboardButton(local_name[i] + ' ' + local_surname[i]))
                list_name_surname.append(local_name[i] + ' ' + local_surname[i])

            bot.send_message(chat_id, 'Список людей', reply_markup=markup)

            db.close()

        elif text == list_command[1]:
            type_command = 2

            bot.send_message(chat_id, 'Пожалуйста внесети данные согласно данному' + ' '
                             + 'шаблону: Имя_Фамилия_группа_Предмет_семместр(1-7)_ср.бал' + ' '
                             + 'где _ это ПРОБЕЛ')
            
            bot.send_message(chat_id, 'После того, как запишете данные в определёноом порядке' + ' '
                            + 'в начале пропишите Добавить:')

            
            bot.send_message(chat_id, 'Подсказка для заполнения:' + '\n'
                             +'Математический анализ -> 1 семмесетр' + '\n'
                             +'Физика.Механика -> 2 семместр' + '\n'
                             +'Физика.Термодинамика -> 3 семместр' + '\n'
                             +'Физика.Оптика -> 4 семместр' + '\n' 
                             +'Линейная алгебра -> 5 семместр' + '\n'
                             +'Технологии программирования -> 6 семместр' + '\n'
                             +'Дифференциальные уравнения -> 7 семместр' + '\n')
            
            
        elif text == list_command[2]:
            type_command = 3

            #добавить выбор типа удаления:
            #вводится имя студента, после предлагается тип удаления
            #1 -> по предмету
            #2 -> по семестру
            #3 -> полноостью по имени удаляются все данные по всем семместрам

            markup = types.ReplyKeyboardMarkup(row_width=1)

            button1 = types.KeyboardButton(pick_delete_comand[0])
            button2 = types.KeyboardButton(pick_delete_comand[1])
            button3 = types.KeyboardButton(pick_delete_comand[2])

            markup.add(button1,button2,button3)

            bot.send_message(chat_id, 'Вам прделагается удлаить данные о студенты в таком формате:' + '\n'
                             'По предмету -> удаляет студентов по выбранному предмету' + '\n'
                             'По семместру -> удаляет студента по выюранному семместру' + '\n'
                             'Полностью студента -> удаляет данные выбранного студента по всем семместрам', reply_markup=markup)

        elif text == list_command[3]:
            type_command = 4

            sql.execute("""SELECT * from student ORDER BY name_first, name_last""")
            
            columnsDB = [description[0] for description in sql.description]
            
            column1 = []
            column2 = []
            column3 = []
            column4 = []
            column5 = []
            column6 = []
            for elem in sql.fetchall():
                column1.append(elem[0])
                column2.append(elem[1])                    
                column3.append(elem[2])
                column4.append(elem[3])
                column5.append(elem[4])
                column6.append(elem[5])
            
            db.close()

            workbook = openpyxl.Workbook()
            sheet = workbook.active

            # Заполнение столбцов
            # В помощь таблица ASCII
            for i in range(len(columnsDB)):
                sheet[f"{chr(i+65)}{1}"] = columnsDB[i]
            
            for row in range(len(column1)):
                sheet[row+2][0].value = column1[row]
                sheet[row+2][1].value = column2[row]
                sheet[row+2][2].value = column3[row]
                sheet[row+2][3].value = column4[row]
                sheet[row+2][4].value = column5[row]
                sheet[row+2][5].value = column6[row]

            workbook.save(filename="DataBaseExcel.xlsx")
            workbook.close()

            bot.send_document(chat_id, document=open("DataBaseExcel.xlsx", 'rb'))

            os.remove("DataBaseExcel.xlsx")

# добавление данных в БД
# Написать в чат -> Добавить: ....
@bot.message_handler(regexp=(r'Добавить:'))
def insert_value(message):
    chat_id = message.chat.id

    #вычисляем количество подстрок (должно быть равно 7)
    countSubstrings = len(message.text.split(' '))
    if countSubstrings != 7: 
        bot.send_message(chat_id, 'Не до конца введены данные! Просьба проверить корректность')
        return

    substrings = message.text.split(' ')

    if type_command == 2:
              
        local_name = substrings[1]
        local_surname = substrings[2]
        local_group = substrings[3]
        local_object = substrings[4]
        local_semmestr = substrings[5]
        local_averege_mark = substrings[6]
        
        try:
            db = sqlite3.connect('server.db')
            sql = db.cursor()
            
            sql.execute("""INSERT INTO student (name_first, semmestr, object, average_mark, name_group, name_last) VALUES (?, ?, ?, ?, ?, ?)""",
            (local_name,local_semmestr, local_object, local_averege_mark, local_group, local_surname))
        except Exception as e:
            bot.send_message(chat_id, e)
            return
        finally:
            sql.execute("""SELECT * FROM student ORDER BY name_first ASC""")
            db.commit()
            db.close()
            bot.send_message(chat_id, 'Запись успешна добавлена в базу данных!')

# ламба-функция, которая ловит имя и фамилию,
# которые были выбраны   
@bot.message_handler(func=lambda m: list_name_surname.__contains__(m.text))
def name_surname_handler(message):
    chat_id = message.chat.id

    global pick_name_surname

    #ловим Имя и Фамилию из базы данных глобально
    pick_name_surname = message.text.split(' ')

    if type_command == 1:
        try: 
            db = sqlite3.connect('server.db')
            sql = db.cursor()
        except Exception as e:
            bot.send_message(chat_id, e)
            return
        finally:
            sql.execute("""SELECT object FROM student WHERE (name_first = ?) AND (name_last = ?)""", (pick_name_surname[0], pick_name_surname[1]))

            local_list_object = []
            for elem in sql.fetchall():
                local_list_object.append(elem[0])
            
        markup = types.ReplyKeyboardMarkup(row_width=1)
        for object in local_list_object:
            markup.add(object)

        bot.send_message(chat_id, 'Список предметов', reply_markup=markup)
        
    if type_delete_command == 3:

        try:
            db = sqlite3.connect('server.db')
            sql = db.cursor()
        except Exception as e: 
            bot.send_message(chat_id, e)
            return
        finally:
            sql.execute("""DELETE FROM student WHERE (name_first = ?) AND (name_last = ?)""", (pick_name_surname[0],pick_name_surname[1]))
            sql.execute("""SELECT * FROM student ORDER BY name_first ASC""")
            bot.send_message(chat_id, 'Данные успешны удалены!')
            db.commit()
            db.close()

# Команда удаления
# Кнопка -> Полностью студента
@bot.message_handler(regexp=(r'Полностью студента'))
def delete_surname_name(message):
    chat_id = message.chat.id

    global type_delete_command
    global list_name_surname

    type_delete_command = 3

    try:
        db = sqlite3.connect('server.db')
        sql = db.cursor()
    except Exception as e: 
        bot.send_message(chat_id, e)
        return
    finally:
        sql.execute("""SELECT DISTINCT name_first, name_last FROM student ORDER BY name_first""")
        local_listQuery = sql.fetchall()

        local_name = []
        local_surname = []
        for elem in local_listQuery:
            local_name.append(elem[0])
            local_surname.append(elem[1])

    markup = types.ReplyKeyboardMarkup()

    #если не пустой список
    if list_name_surname:
        list_name_surname.clear()

    for i in range(len(local_listQuery)):
        markup.add(types.KeyboardButton(local_name[i] + ' ' + local_surname[i]))
        list_name_surname.append(local_name[i] + ' ' + local_surname[i])

    bot.send_message(chat_id, 'Удаление по критерию "Полностью студента"', reply_markup=markup)

    db.close()

# Команда удаления
# Кнопка -> По предмету
@bot.message_handler(regexp=(r'По предмету'))
def delete_object(message):
    chat_id = message.chat.id

    global type_delete_command
    type_delete_command = 1

    try: 
        db = sqlite3.connect('server.db')
        sql = db.cursor()
    except Exception as e:
        bot.send_message(chat_id, e)
        return
    finally:
        sql.execute("""SELECT DISTINCT object FROM student""")

        markup = types.ReplyKeyboardMarkup(row_width=1)
        for object in sql.fetchall():
            markup.add(object[0])

    bot.send_message(chat_id, 'Удаление по критерию "По предмету"', reply_markup=markup)

# Команда удаления
# Кнопка -> По семместру
@bot.message_handler(regexp=(r'По семместру'))
def delete_semmestr(message):
    chat_id = message.chat.id

    global type_delete_command

    type_delete_command = 2

    markup = types.ReplyKeyboardMarkup(row_width=7)
    button1 = types.KeyboardButton('1')
    button2 = types.KeyboardButton('2')
    button3 = types.KeyboardButton('3')
    button4 = types.KeyboardButton('4')
    button5 = types.KeyboardButton('5')
    button6 = types.KeyboardButton('6')
    button7 = types.KeyboardButton('7')

    markup.add(button1,button2,button3,button4,button5,button6,button7)

    bot.send_message(chat_id, 'Список семместров', reply_markup=markup)

# лямба-функция, которая ловит семместры,
# которые были выбраны
@bot.message_handler(regexp=(r'1|2|3|4|5|6|7'))
def delete_object_handler(message):
    chat_id = message.chat.id
                
    local_semmestr = message.text

    if type_delete_command == 2:
        try:
            db = sqlite3.connect('server.db')
            sql = db.cursor()
        except Exception as e:
            bot.send_message(chat_id, e)
            return
        finally:
            sql.execute("""DELETE FROM student WHERE semmestr = ?""", (local_semmestr))
            sql.execute("""SELECT * FROM student ORDER BY name_first ASC""")
            bot.send_message(chat_id, 'Удаление по критерию "По семестру"')
            db.commit()
            db.close()

# лямба-функция, которая ловит список предметов,
# которые были выбраны
@bot.message_handler(func=lambda m:object_list.__contains__(m.text)) 
def object_handler_(message):
    global pick_object

    chat_id = message.chat.id
    pick_object = message.text
    
    if type_delete_command == 1:

        try:
            db = sqlite3.connect('server.db')
            sql = db.cursor()
        except Exception as e: 
            bot.send_message(chat_id, e)
            return
        finally:
            sql.execute("""DELETE FROM student WHERE object = ?""", (pick_object,))
            sql.execute("""SELECT * FROM student ORDER BY name_first""")
            bot.send_message(chat_id, 'Данные успешны удалены!')
            db.commit()
            db.close()
        
    else:
        markup = types.ReplyKeyboardMarkup(row_width=1)
        button1 = types.KeyboardButton('График')
        button2 = types.KeyboardButton('Гистограмма')
        button3 = types.KeyboardButton('Диаграмма')
        markup.add(button1,button2,button3)

        bot.send_message(chat_id, 'Выбор графика', reply_markup=markup)

# Команда выбора изображения
# Кнопка -> График
@bot.message_handler(regexp=(r'График'))
def plot_scatter(message):
    chat_id = message.chat.id

    db = sqlite3.connect('server.db')
    sql = db.cursor()

    local_name = pick_name_surname[0]
    local_surname =  pick_name_surname[1]
    local_object = pick_object

    #Выбранный студент -> его семместр и ср.бал
    sql.execute("""SELECT semmestr, average_mark FROM student WHERE (name_first = ?) AND (object = ?) AND (name_last = ?)""", (local_name,local_object,local_surname))

    for elem in sql.fetchall():
        local_semmestr = elem[0]
        local_avg_mark = elem[1]

    #sql - запрос -> ср значение по ср.баллу по определлёному предмету 
    try:
        sql.execute("""SELECT AVG(average_mark) FROM student WHERE (semmestr = ?) AND (object = ?)""", (local_semmestr,local_object))
    except Exception as e:
        bot.send_message(chat_id, e)
        return
    finally:
        for elem in sql.fetchall():
            local_avgmark_group = elem[0]

    db.close()

    #x-лист -> семместры
    #y-лист -> ср.бал 
    x1 = np.array([local_semmestr])
    y1 = np.array([local_avg_mark])
    x2 = np.array([local_semmestr])
    y2 = np.array([local_avgmark_group])

    plt.figure(figsize=(6,5))
    plt.axis([0,7,0,5])
    plt.text(local_semmestr, local_avg_mark, f"{round(local_avg_mark,2)}")
    plt.text(local_semmestr, local_avgmark_group, f"{round(local_avgmark_group,2)}")
    plt.title('Scatter')
    plt.xlabel('Семместр')
    plt.ylabel('Средний бал')
    plt.grid(True)
    plt.scatter(x1,y1)
    plt.scatter(x2,y2)
    plt.yticks(np.linspace(0, 5, 20))
    lgd = plt.legend([local_name + ' ' + local_surname, 'Ср.бал группы'],loc ='center left', bbox_to_anchor=(1,0.5))
    plt.savefig("scatter.png", bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close() #-> необходимо закрыть поток, чтобы не было наложение графиокв(потокобезопасность)

    bot.send_photo(chat_id, photo=open('scatter.png', 'rb'))
    
    os.remove('scatter.png')

# Команда выбора изображения
# Кнопка -> Гистограмма
@bot.message_handler(regexp=(r'Гистограмма'))
def plot_bar(message):
    chat_id = message.chat.id

    db = sqlite3.connect('server.db')
    sql = db.cursor()

    local_object = pick_object

    #Вытащить Имя и Фамилию студентов по выбранному предмету и средний бал
    try:
        sql.execute("""SELECT DISTINCT name_first, average_mark, name_last FROM student WHERE object = ?""", (local_object,))
    except Exception as e:
        bot.send_message(chat_id, e)
        return

        
    list_all_names = []
    list_avg_mark = []
    for elem in sql.fetchall():
        list_all_names.append(elem[0] + ' ' + elem[2])
        list_avg_mark.append(elem[1])

    index = 0
    for name in list_all_names:
        if name == pick_name_surname[0] + ' ' + pick_name_surname[1]:
            break
        else:
            index+=1
    
    db.close()

    plt.title('bar')
    plt.yticks(np.linspace(0,5,20))
    plt.text(index, list_avg_mark[index],f"{round(list_avg_mark[index],2)}")

    plt.bar(np.arange(len(list_avg_mark)),list_avg_mark, color = 'blue')
    plt.bar(np.array(index),list_avg_mark[index], color = 'red')
    lgd = plt.legend(['Балы других студентов', list_all_names[index]],loc ='center left', bbox_to_anchor=(1,0.5))

    plt.savefig('bar.png', bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close() #-> необходимо закрыть поток, чтобы не было наложение графиокв(потокобезопасность)

    bot.send_photo(chat_id,  photo=open('bar.png', 'rb'))
    
    os.remove('bar.png')

# Команда выбора изображения
# Кнопка -> Диаграмма
@bot.message_handler(regexp=(r'Диаграмма'))
def plot_pie(message):
    chat_id = message.chat.id

    db = sqlite3.connect('server.db')
    sql = db.cursor()

    local_object = pick_object

    #Вытащить Имя и Фамиля студентов по выбранному предмету и средний бал
    sql.execute("""SELECT DISTINCT name_first, average_mark, name_last FROM student WHERE object = ?""", (local_object,))

    labels = []
    values = []
    for elem in sql.fetchall():
        labels.append(elem[0] + ' ' + elem[2])
        values.append(elem[1])

    #узнали где находится наш выбранный студент
    index = 0
    for label in labels:
        if label == pick_name_surname[0] + ' ' + pick_name_surname[1]:
            break
        else:
            index+= 1

    #для выбора кусочка диаграммы
    explode = []
    for i in range(len(labels)):
        if i==index:
            explode.append(0.3)
        else:
            explode.append(0)

    db.close()

    plt.title('Pie')
    plt.pie(values, labels = labels, explode=explode,shadow=True,autopct='%1.1f%%',startangle=180)
    plt.savefig('pie.png')
    plt.close() #-> необходимо закрыть поток, чтобы не было наложение графиокв(потокобезопасность)

    bot.send_photo(chat_id, photo=open('pie.png', 'rb'))

    os.remove('pie.png')

# лямбда-функция, которая ловит все сообщения,
# которые не соответсвтуют функционалу бота 
@bot.message_handler(func=lambda lmd: True)
def catch_anybad_text(message):
    chat_id = message.chat.id

    bot.send_message(chat_id, 'Извините, невозможно обработать текст!')

bot.polling()
