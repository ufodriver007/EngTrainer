"""
Simple English trainer with 4 dictionaries(800 words, 3000 words, 5000 words, py_docs)
and another one custom dictionary. You can add any word that contained in
a dictionary to your custom one. There are 2 modes(english words first or russian words first).
ver. 0.5b
"""
import threading
import time
import tkinter.messagebox
from tkinter import *
import sqlite3


db = sqlite3.connect('dictionary_bd.sqlite')
cursor = db.cursor()

window = Tk()
window.title("English Trainer")
window.geometry('600x500+650+300')
window.resizable(False, False)

photo = PhotoImage(file='icon.png')       # переменная с иконкой
window.iconphoto(False, photo)

currentDictionary = 'dict800'             # текущий словарь
radSelected = IntVar()                    # радиокнопка словаря
radEngRus = IntVar()                      # радиокнопка английские/русские слова сначала
flipflop = True                           # значение, указывающее что показывать, слово или ответ
key = ''                                  # ключ словаря, он же - английское слово
value = ''                                # значение словаря, оно же - русское слово
mode = 0                                  # режим английское или русское слоаво сначала
tables = ['1.png', '2.png', '3.png', '4.png', '5.png', '6.png', '7.png']
tables_iterator = 0                       # paginator окна неправильных глаголов
is_exam = False                           # флаг состояния экзамена
timerOff = False                          # флаг выхода из бесконченого цикла таймера
seconds = 0                               # количество секунд прошедших с начала экзамена
known_words = 0                           # количество слов, которые вы знаете
unknown_words = 0                         # количество слов, которые вы НЕ знаете

lbl = Label(window, text="", font=("Arial Bold", 40), pady=80)
lbl.pack()
lblAnswer = Label(window, text="", font=("Arial", 20))
lblAnswer.pack()
lblTimer = Label(window, text="", font=("Arial", 12), fg='red')
lblTimer.place(x=20, y=50)


def get_current_dict_size() -> int:
    """Returns a current dictionary size"""
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {currentDictionary}")
        dict_res = cursor.fetchone()  # лист кортежей, в каждом - строка из БД
        if dict_res[0] is None:
            return 0
        else:
            return dict_res[0]
    except sqlite3.OperationalError:
        tkinter.messagebox.showerror(title='Ошибка', message='База данных отсутствует!')


lblCurrentDictionarySize = Label(window, text=f"Размер текущего словаря: {get_current_dict_size()}", font=("Arial", 10))
lblCurrentDictionarySize.place(x=390, y=470)


def btn_next_clicked():
    """Get a new string from DataBase and change labels"""
    global flipflop
    global key
    global value
    global mode
    global is_exam

    if flipflop:
        if is_exam:
            # убираем кнопку Далее
            btnNext.place(x=1000, y=300)

            # добавляем кнопки знаю, не знаю
            btnKnow.place(x=330, y=350)
            btnDontKnow.place(x=170, y=350)

        lbl.configure(font=("Arial Bold", 50))
        # определяем режим
        mode = radEngRus.get()
        # получаем ключ-значение
        try:
            cursor.execute(f"SELECT * FROM {currentDictionary} ORDER BY RANDOM() LIMIT 1")
            dict_res = cursor.fetchone()  # кортеж - строка из БД
            key = dict_res[1]
            value = dict_res[2]
        except TypeError:
            return
        except ValueError:
            return

        # вывод ключа или значения
        if mode == 0:
            lbl.configure(text=key)
        elif mode == 1:
            lbl.configure(text=value)

        # прячем нижнюю надпись
        lblAnswer.configure(text='')
        flipflop = False
    else:
        if is_exam:
            # убираем кнопки знаю, не знаю
            btnKnow.place(x=330, y=1000)
            btnDontKnow.place(x=170, y=1000)

            # возвращаем кнопку Далее
            btnNext.place(x=180, y=300)

        # вывод значения или ключа
        if mode == 0:
            lblAnswer.configure(text=value)
        elif mode == 1:
            lblAnswer.configure(text=key)
        flipflop = True


def btn_add_remove_clicked():
    """Button Add/Remove word from custom dictionary"""
    global flipflop
    if currentDictionary == 'my_words':
        # подготовить запрос
        cursor.execute(f"DELETE FROM my_words WHERE eng = ?", (key, ))
        # выполнить запросы(только для меняющих базу)
        db.commit()
        lblCurrentDictionarySize.configure(text=f"Размер текущего словаря: {get_current_dict_size()}")
        if get_current_dict_size() == 0:
            lbl.configure(text='--//--')
    else:
        if key and value:
            # подготовить запрос
            cursor.execute(f"INSERT INTO my_words (eng, rus) VALUES (?, ?)", (key, value))
            # выполнить запросы(только для меняющих базу)
            db.commit()
    flipflop = True
    btn_next_clicked()


def abouta():
    """Create a new window with description of owner"""
    top = Toplevel(window)

    top.title("About")
    top.geometry('500x200+700+400')
    top.resizable(False, False)

    top.iconphoto(False, photo)
    lbbg = Label(top, text="", bg='gray')
    lbbg.place(width=500, height=200)
    lb = Label(top, text="English Trainer 0.5b\n\n by UFODriver. 2023", font=("Arial Bold", 16), bg='gray')
    lb.place(x=250, y=80, anchor='center')

    top.transient(window)
    # мы передаем поток данному виджету т.е. делаем его модальным
    top.grab_set()
    # фокусируем наше приложение на окне top
    top.focus_set()
    # мы задаем приложению команду, что пока не будет закрыто окно top пользоваться другим окном будет нельзя
    top.wait_window()


def i_know_word():
    """Exam button 'I know this word'"""
    global known_words
    known_words += 1
    btn_next_clicked()


def i_dont_know_word():
    """Exam button 'I dont know this word'"""
    global unknown_words
    unknown_words += 1
    btn_next_clicked()


def timer():
    """Exam function for other thread"""
    global timerOff
    global seconds
    timerOff = False

    while not timerOff:
        lblTimer.configure(text=f'{time.strftime("%H:%M:%S", time.gmtime(seconds))}')
        time.sleep(1)
        seconds += 1


def btn_end_exam():
    """Button 'End exam'"""
    global timerOff
    global seconds
    global known_words
    global unknown_words
    global flipflop
    global is_exam
    timerOff = True
    lblTimer.configure(text='')

    lbl.configure(text=f'''            СТАТИСТИКА
    
    общее время: {time.strftime("%H:%M:%S", time.gmtime(seconds))}
    слов пройдено: {known_words + unknown_words}
    правильных ответов: {known_words}
    неправильных ответов: {unknown_words}
    РЕЗУЛЬТАТ: {0 if known_words == 0 else (known_words / ((known_words + unknown_words) / 100)):.1f}%
    ''', font=("Arial Bold", 12), justify=LEFT)
    lblAnswer.configure(text='')

    seconds = 0
    known_words = 0
    unknown_words = 0
    flipflop = True
    is_exam = False

    # убираем кнопки знаю, не знаю, закончить экзамен
    btnKnow.place(x=330, y=1000)
    btnDontKnow.place(x=170, y=1000)
    btnEndExam.place(x=170, y=1000)

    # возвращаем кнопки Далее и Добавить в мой словарь
    btnNext.place(x=180, y=300)
    btnIKnow.place(x=185, y=420)

    # включаем обратно меню и радиокнопки
    radBasic.configure(state='normal')
    radmy.configure(state='normal')
    rad3000.configure(state='normal')
    rad5000.configure(state='normal')
    radEng.configure(state='normal')
    radRus.configure(state='normal')
    pydoc.configure(state='normal')
    menubar.entryconfig('Таблицы', state='normal')
    menubar.entryconfig('Неправильные глаголы', state='normal')
    menubar.entryconfig('Экзамен', state='normal')
    menubar.entryconfig('О программе', state='normal')


def examine():
    """Menu button 'Exam'"""
    global flipflop
    global known_words
    global unknown_words
    global is_exam
    is_exam = True
    known_words = 0
    unknown_words = 0

    # запускаем функцию таймера в отдельном потоке
    p = threading.Thread(target=timer)
    p.start()

    lbl.configure(text='')
    lblAnswer.configure(text='')
    flipflop = True
    btn_next_clicked()

    # убираем кнопки Далее и Добавить в мой словарь
    btnNext.place(x=1000, y=300)
    btnIKnow.place(x=1000, y=300)

    # добавляем кнопки знаю, не знаю, закончить экзамен
    btnKnow.place(x=330, y=350)
    btnDontKnow.place(x=170, y=350)
    btnEndExam.place(x=207, y=430)

    # выключаем меню и радиокнопки
    radBasic.configure(state='disabled')
    radmy.configure(state='disabled')
    rad3000.configure(state='disabled')
    rad5000.configure(state='disabled')
    radEng.configure(state='disabled')
    radRus.configure(state='disabled')
    pydoc.configure(state='disabled')
    menubar.entryconfig('Таблицы', state="disabled")
    menubar.entryconfig('Неправильные глаголы', state="disabled")
    menubar.entryconfig('Экзамен', state="disabled")
    menubar.entryconfig('О программе', state="disabled")


def verb():
    """Create a new window with pictures(irregular verbs)"""
    global tables
    global tables_iterator
    top = Toplevel(window)

    top.title("Irregular verbs")
    top.geometry('500x800+700+100')
    top.resizable(False, False)

    ph_tab = PhotoImage(file='1.png')
    top.iconphoto(False, photo)

    # first create the canvas
    canvas = Canvas(top, height=780, width=470)
    canvas.pack()

    canvas.delete("all")
    canvas.create_image(0, 0, anchor='nw', image=ph_tab)
    canvas.image = ph_tab

    def btn_n_clicked():
        """Button Next"""
        global tables
        global tables_iterator
        if tables_iterator < 6:
            tables_iterator += 1
            f = PhotoImage(file=tables[tables_iterator])
            canvas.delete("all")
            canvas.create_image(0, 0, anchor='nw', image=f)
            canvas.image = f

    def btn_p_clicked():
        """Button previous"""
        global tables
        global tables_iterator
        if tables_iterator > 0:
            tables_iterator -= 1
            f = PhotoImage(file=tables[tables_iterator])
            canvas.delete("all")
            canvas.create_image(0, 0, anchor='nw', image=f)
            canvas.image = f

    btn_n = Button(top, text="След.", font=("Arial", 12), command=btn_n_clicked)
    btn_n.pack(side=RIGHT)

    btn_p = Button(top, text="Пред.", font=("Arial", 12), command=btn_p_clicked)
    btn_p.pack(side=LEFT)

    top.transient(window)
    # мы передаем поток данному виджету т.е. делаем его модальным
    top.grab_set()
    # фокусируем наше приложение на окне top
    top.focus_set()
    # мы задаем приложению команду, что пока не будет закрыто окно top пользоваться другим окном будет нельзя
    top.wait_window()


def tobe():
    """Create a new window with to_be_table"""
    top = Toplevel(window)

    top.title("Be")
    top.geometry('800x600+550+250')
    top.resizable(False, False)

    ph_tab = PhotoImage(file='be.gif')
    top.iconphoto(False, photo)

    lb = Label(top, text="", image=ph_tab)
    lb.pack(expand=True, fill=BOTH)

    top.transient(window)
    # мы передаем поток данному виджету т.е. делаем его модальным
    top.grab_set()
    # фокусируем наше приложение на окне top
    top.focus_set()
    # мы задаем приложению команду, что пока не будет закрыто окно top пользоваться другим окном будет нельзя
    top.wait_window()


def simple():
    """Create a new window with simple times"""
    top = Toplevel(window)

    top.title("Simple times")
    top.geometry('800x600+550+250')
    top.resizable(False, False)

    ph_tab = PhotoImage(file='simple.gif')
    top.iconphoto(False, photo)

    lb = Label(top, text="", image=ph_tab)
    lb.pack(expand=True, fill=BOTH)

    top.transient(window)
    # мы передаем поток данному виджету т.е. делаем его модальным
    top.grab_set()
    # фокусируем наше приложение на окне top
    top.focus_set()
    # мы задаем приложению команду, что пока не будет закрыто окно top пользоваться другим окном будет нельзя
    top.wait_window()


def all_times():
    """Create a new window with all_times"""
    top = Toplevel(window)

    top.title("Verb tenses")
    top.geometry('900x600+550+250')
    top.resizable(False, False)

    ph_tab = PhotoImage(file='grammar_table.png')
    top.iconphoto(False, photo)

    lb = Label(top, text="", image=ph_tab)
    lb.pack(expand=True, fill=BOTH)

    top.transient(window)
    # мы передаем поток данному виджету т.е. делаем его модальным
    top.grab_set()
    # фокусируем наше приложение на окне top
    top.focus_set()
    # мы задаем приложению команду, что пока не будет закрыто окно top пользоваться другим окном будет нельзя
    top.wait_window()


# Creating Menubar
menubar = Menu(window)
# Adding File Menu and commands
file = Menu(menubar, tearoff=0)
menubar.add_cascade(label='Таблицы', menu=file)
file.add_command(label='to be', command=tobe)
file.add_command(label='Простое время', command=simple)
file.add_command(label='Все времена', command=all_times)
file.add_separator()
file.add_command(label='Exit', command=window.destroy)

verbs = Menu(menubar, tearoff=0)
menubar.add_cascade(label='Неправильные глаголы', menu=verbs)
verbs.add_command(label="Неправильные глаголы", command=verb)

exam = Menu(menubar, tearoff=0)
menubar.add_cascade(label='Экзамен', menu=exam)
exam.add_command(label='Экзамен', command=examine)

about = Menu(menubar, tearoff=0)
menubar.add_cascade(label='О программе', menu=about)
about.add_command(label='О программе', command=abouta)

window.config(menu=menubar)


def change_dictionary():
    """Change the global dictionary and show it size"""
    global currentDictionary
    if radSelected.get() == 0:
        currentDictionary = 'dict800'
        btnIKnow.configure(text="Добавить в мой словарь")
    elif radSelected.get() == 3000:
        currentDictionary = 'dict3000'
        btnIKnow.configure(text="Добавить в мой словарь")
    elif radSelected.get() == 5000:
        currentDictionary = 'dict5000'
        btnIKnow.configure(text="Добавить в мой словарь")
    elif radSelected.get() == 1:
        currentDictionary = 'my_words'
        btnIKnow.configure(text='Убрать из моего словаря')
    elif radSelected.get() == 2:
        currentDictionary = 'py_docs'
        btnIKnow.configure(text="Добавить в мой словарь")
    lblCurrentDictionarySize.configure(text=f"Размер текущего словаря: {get_current_dict_size()}")


radBasic = Radiobutton(window, text='800 words', value=0, variable=radSelected, command=change_dictionary)
radBasic.place(x=3, y=3)
rad3000 = Radiobutton(window, text='3000 words', value=3000, variable=radSelected, command=change_dictionary)
rad3000.place(x=130, y=3)
rad5000 = Radiobutton(window, text='5000 words', value=5000, variable=radSelected, command=change_dictionary)
rad5000.place(x=260, y=3)
radmy = Radiobutton(window, text='My dictionary', value=1, variable=radSelected, command=change_dictionary)
radmy.place(x=390, y=3)
pydoc = Radiobutton(window, text='PyDoc', value=2, variable=radSelected, command=change_dictionary)
pydoc.place(x=520, y=3)

radEng = Radiobutton(window, text='Английские слова', value=0, variable=radEngRus)
radEng.place(x=3, y=25)
radRus = Radiobutton(window, text='Русские слова', value=1, variable=radEngRus)
radRus.place(x=130, y=25)

btnNext = Button(window, text="Далее", font=("Arial Bold", 50), bg='#567', command=btn_next_clicked)
btnNext.place(x=180, y=300)

btnIKnow = Button(window, text="Добавить в мой словарь", font=("Arial", 14), bg='#567', command=btn_add_remove_clicked)
btnIKnow.place(x=185, y=420)

btnKnow = Button(window, text="   Знаю   ", font=("Arial", 14), bg='#567', command=i_know_word)
btnKnow.place(x=330, y=1000)
btnDontKnow = Button(window, text="Не знаю", font=("Arial", 14), bg='#567', command=i_dont_know_word)
btnDontKnow.place(x=170, y=1000)
btnEndExam = Button(window, text="Закончить экзамен", font=("Arial", 14), bg='#567', command=btn_end_exam)
btnEndExam .place(x=170, y=1000)

window.mainloop()
db.close()
