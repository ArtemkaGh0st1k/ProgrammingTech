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
command_list = ['Узнать данные о студенте(ах)',
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
type_command = None 
type_delete_command = None
pick_object = None
NameSurnameList = []


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

    groupDB = random.randint(1,100)
    for rn in rus_names:
        nameDB = rn.split(" ")[0]
        surnameDB = rn.split(" ")[2]

        semmestrDB = 1
        for i in range(len(object_list)):
            
            object_listDB = object_list[semmestrDB-1]
            markDB = random.uniform(2.0, 5.0)

            sql.execute("""INSERT INTO student (name_first, semmestr, object, average_mark, name_group, name_last) VALUES (?, ?, ?, ?, ?, ?)""",
            (nameDB, semmestrDB, object_listDB, markDB, groupDB, surnameDB))

            semmestrDB+= 1
        
        db.commit()
     
    sql.execute("""SELECT * FROM student ORDER BY name_first""")
    db.commit()
    db.close()

    
# передаём токен боту
token = 'Ваш токен'
bot = telebot.TeleBot(token) 


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
        NameSurnameList.clear()

    markup = types.ReplyKeyboardMarkup(row_width=1)
    button1 = types.KeyboardButton(command_list[0])
    button2 = types.KeyboardButton(command_list[1])
    button3 = types.KeyboardButton(command_list[2])
    button4 = types.KeyboardButton(command_list[3])
    
    markup.add(button1,button2,button3,button4)

    bot.send_message(chat_id, 'Список команд', reply_markup=markup)

#ловит вводимые данные при /start
@bot.message_handler(regexp=(r'Узнать данные|Внести данные|Удалить данные|Посмотреть таблицу'))
def button_handler(message):
    chat_id = message.chat.id
    text = message.text
    global NameSurnameList
    global type_command

    # Проверка на работоспособность базы данных
    try:
        db = sqlite3.connect('server.db')
        sql = db.cursor()
    except Exception as e:
        bot.send_message(chat_id, e)
        return
    finally:
        if text == command_list[0]:
            type_command = 1

            sql.execute("""SELECT DISTINCT name_first, name_last FROM student ORDER BY name_first""")
            queryList = sql.fetchall()

            nameList = []
            surnameList = []
            for elem in queryList:
                nameList.append(elem[0])
                surnameList.append(elem[1])

            markup = types.ReplyKeyboardMarkup()

            #если не пустой список
            if NameSurnameList:
                NameSurnameList.clear()

            for i in range(len(queryList)):
                markup.add(types.KeyboardButton(nameList[i] + ' ' + surnameList[i]))
                NameSurnameList.append(nameList[i] + ' ' + surnameList[i])

            bot.send_message(chat_id, 'Список людей', reply_markup=markup)

            db.close()

        elif text == command_list[1]:
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
            
            
        elif text == command_list[2]:
            type_command = 3

            markup = types.ReplyKeyboardMarkup(row_width=1)

            button1 = types.KeyboardButton(pick_delete_comand[0])
            button2 = types.KeyboardButton(pick_delete_comand[1])
            button3 = types.KeyboardButton(pick_delete_comand[2])

            markup.add(button1,button2,button3)

            bot.send_message(chat_id, 'Вам прделагается удлаить данные о студенты в таком формате:' + '\n'
                             'По предмету -> удаляет студентов по выбранному предмету' + '\n'
                             'По семместру -> удаляет студента по выюранному семместру' + '\n'
                             'Полностью студента -> удаляет данные выбранного студента по всем семместрам', reply_markup=markup)

        elif text == command_list[3]:
            type_command = 4

            sql.execute("""SELECT * from student ORDER BY name_first, name_last""")
            
            columnsDB = [description[0] for description in sql.description]
            
            columnName = []
            columnSemmestr = []
            columnObject = []
            columnAVGMark = []
            columnGroup = []
            columnSurname = []
            for elem in sql.fetchall():
                columnName.append(elem[0])
                columnSemmestr.append(elem[1])                    
                columnObject.append(elem[2])
                columnAVGMark.append(elem[3])
                columnGroup.append(elem[4])
                columnSurname.append(elem[5])
            
            db.close()

            workbook = openpyxl.Workbook()
            sheet = workbook.active

            # Заполнение столбцов
            # В помощь таблица ASCII
            for i in range(len(columnsDB)):
                sheet[f"{chr(i+65)}{1}"] = columnsDB[i]
            
            for row in range(len(columnName)):
                sheet[row+2][0].value = columnName[row]
                sheet[row+2][1].value = columnSemmestr[row]
                sheet[row+2][2].value = columnObject[row]
                sheet[row+2][3].value = columnAVGMark[row]
                sheet[row+2][4].value = columnGroup[row]
                sheet[row+2][5].value = columnSurname[row]

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
              
        nameDB = substrings[1]
        surnameDB = substrings[2]
        groupDB = substrings[3]
        objectDB = substrings[4]
        semmestrDB = substrings[5]
        averege_markDB = substrings[6]
        
        try:
            db = sqlite3.connect('server.db')
            sql = db.cursor()
            
            sql.execute("""INSERT INTO student (name_first, semmestr, object, average_mark, name_group, name_last) VALUES (?, ?, ?, ?, ?, ?)""",
            (nameDB, semmestrDB, objectDB, averege_markDB, groupDB, surnameDB))
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
@bot.message_handler(func=lambda m: NameSurnameList.__contains__(m.text))
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

            objectList = []
            for elem in sql.fetchall():
                objectList.append(elem[0])
            
        markup = types.ReplyKeyboardMarkup(row_width=1)
        for object in objectList:
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
            sql.execute("""DELETE FROM student WHERE (name_first = ?) AND (name_last = ?)""", (pick_name_surname[0], pick_name_surname[1]))
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
    global NameSurnameList

    type_delete_command = 3

    try:
        db = sqlite3.connect('server.db')
        sql = db.cursor()
    except Exception as e: 
        bot.send_message(chat_id, e)
        return
    finally:
        sql.execute("""SELECT DISTINCT name_first, name_last FROM student ORDER BY name_first""")
        queryList = sql.fetchall()

        nameList = []
        surnameList = []
        for elem in queryList:
            nameList.append(elem[0])
            surnameList.append(elem[1])

    markup = types.ReplyKeyboardMarkup()

    #если не пустой список
    if NameSurnameList:
        NameSurnameList.clear()

    for i in range(len(queryList)):
        markup.add(types.KeyboardButton(nameList[i] + ' ' + surnameList[i]))
        NameSurnameList.append(nameList[i] + ' ' + surnameList[i])

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
                
    semmestrDB = message.text

    if type_delete_command == 2:
        try:
            db = sqlite3.connect('server.db')
            sql = db.cursor()
        except Exception as e:
            bot.send_message(chat_id, e)
            return
        finally:
            sql.execute("""DELETE FROM student WHERE semmestr = ?""", (semmestrDB))
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

    nameDB = pick_name_surname[0]
    surnameDB =  pick_name_surname[1]
    objectDB = pick_object

    #Выбранный студент -> его семместр и ср.бал
    sql.execute("""SELECT semmestr, average_mark FROM student WHERE (name_first = ?) AND (object = ?) AND (name_last = ?)""", (nameDB,objectDB, surnameDB))

    for elem in sql.fetchall():
        semmestrDB = elem[0]
        avg_markDB = elem[1]

    #sql - запрос -> ср значение по ср.баллу по определлёному предмету 
    try:
        sql.execute("""SELECT AVG(average_mark) FROM student WHERE (semmestr = ?) AND (object = ?)""", (semmestrDB, objectDB))
    except Exception as e:
        bot.send_message(chat_id, e)
        return
    finally:
        for elem in sql.fetchall():
            avgmark_groupDB = elem[0]

    db.close()

    #x-лист -> семместры
    #y-лист -> ср.бал 
    x1 = np.array([semmestrDB])
    y1 = np.array([avg_markDB])
    x2 = np.array([semmestrDB])
    y2 = np.array([avgmark_groupDB])

    plt.figure(figsize=(6,5))
    plt.axis([0,7,0,5])
    plt.text(semmestrDB, avg_markDB, f"{round(avg_markDB,2)}")
    plt.text(semmestrDB, avgmark_groupDB, f"{round(avgmark_groupDB,2)}")
    plt.title('Scatter')
    plt.xlabel('Семместр')
    plt.ylabel('Средний бал')
    plt.grid(True)
    plt.scatter(x1,y1)
    plt.scatter(x2,y2)
    plt.yticks(np.linspace(0, 5, 20))
    lgd = plt.legend([nameDB + ' ' + surnameDB, 'Ср.бал группы'],loc ='center left', bbox_to_anchor=(1,0.5))
    plt.savefig("scatter.png", bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close()
    bot.send_photo(chat_id, photo=open('scatter.png', 'rb'))
    
    os.remove('scatter.png')

# Команда выбора изображения
# Кнопка -> Гистограмма
@bot.message_handler(regexp=(r'Гистограмма'))
def plot_bar(message):
    chat_id = message.chat.id

    db = sqlite3.connect('server.db')
    sql = db.cursor()

    objectDB = pick_object

    #Вытащить Имя и Фамилию студентов по выбранному предмету и средний бал
    try:
        sql.execute("""SELECT DISTINCT name_first, average_mark, name_last FROM student WHERE object = ?""", (objectDB,))
    except Exception as e:
        bot.send_message(chat_id, e)
        return

        
    all_namesList = []
    avg_markList = []
    for elem in sql.fetchall():
        all_namesList.append(elem[0] + ' ' + elem[2])
        avg_markList.append(elem[1])

    index = 0
    for name in all_namesList:
        if name == pick_name_surname[0] + ' ' + pick_name_surname[1]:
            break
        else:
            index+=1
    
    db.close()

    plt.title('bar')
    plt.yticks(np.linspace(0,5,20))
    plt.text(index, avg_markList[index],f"{round(avg_markList[index],2)}")

    plt.bar(np.arange(len(avg_markList)), avg_markList, color = 'blue')
    plt.bar(np.array(index), avg_markList[index], color = 'red')
    lgd = plt.legend(['Балы других студентов', all_namesList[index]],loc ='center left', bbox_to_anchor=(1,0.5))

    plt.savefig('bar.png', bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close()
    bot.send_photo(chat_id,  photo=open('bar.png', 'rb'))
    
    os.remove('bar.png')

# Команда выбора изображения
# Кнопка -> Диаграмма
@bot.message_handler(regexp=(r'Диаграмма'))
def plot_pie(message):
    chat_id = message.chat.id

    db = sqlite3.connect('server.db')
    sql = db.cursor()

    objectDB = pick_object

    #Вытащить Имя и Фамиля студентов по выбранному предмету и средний бал
    sql.execute("""SELECT DISTINCT name_first, average_mark, name_last FROM student WHERE object = ?""", (objectDB,))

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
    plt.close() 

    bot.send_photo(chat_id, photo=open('pie.png', 'rb'))

    os.remove('pie.png')

# лямбда-функция, которая ловит все сообщения,
# которые не соответсвтуют функционалу бота 
@bot.message_handler(func=lambda lmd: True)
def catch_anybad_text(message):
    chat_id = message.chat.id

    bot.send_message(chat_id, 'Извините, невозможно обработать текст!')

bot.polling()
