"""
Simple English trainer with 5 dictionaries(800 words, 3000 words, 5000 words, py_docs)
and another one custom dictionary. You can add any word that is contained in
dictionary to your custom one. There is 2 modes(english words first or russian words first).
ver. 0.4b
"""

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

lbl = Label(window, text="", font=("Arial Bold", 40), pady=80)
lbl.pack()
lblAnswer = Label(window, text="", font=("Arial", 20))
lblAnswer.pack()


def get_current_dict_size() -> int:
    """Returns current dictionary's size"""
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
    """Get new string from DataBase and change labels"""
    global flipflop
    global key
    global value
    global mode
    if flipflop:
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
        # вывод значения или ключа
        if mode == 0:
            lblAnswer.configure(text=value)
        elif mode == 1:
            lblAnswer.configure(text=key)
        flipflop = True


def btn_add_remove_clicked():
    global flipflop
    """Button Add/Remove word from custom dictionary"""
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
    """Create new window with description of owner"""
    top = Toplevel(window)

    top.title("About")
    top.geometry('500x200+700+400')
    top.resizable(False, False)

    top.iconphoto(False, photo)
    lbbg = Label(top, text="", bg='gray')
    lbbg.place(width=500, height=200)
    lb = Label(top, text="English Trainer by UFODriver. 2023", font=("Arial Bold", 16), bg='gray')
    lb.place(x=250, y=80, anchor='center')

    top.transient(window)
    # мы передаем поток данному виджету т.е. делаем его модальным
    top.grab_set()
    # фокусируем наше приложение на окне top
    top.focus_set()
    # мы задаем приложению команду, что пока не будет закрыто окно top пользоваться другим окном будет нельзя
    top.wait_window()


def verb():
    """Create new window with pictures(irregular verbs)"""
    global tables
    global tables_iterator
    top = Toplevel(window)

    top.title("Irregular verbs")
    top.geometry('500x800+700+100')
    top.resizable(False, False)

    ph_tab = PhotoImage(file='1.png')
    top.iconphoto(False, photo)

    # first create the canvas
    canvas = Canvas(top, height=760, width=450)
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
    """Create new window with to_be_table"""
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
    """Create new window with simple_times"""
    top = Toplevel(window)

    top.title("Be")
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
    """Create new window with all_times"""
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

about = Menu(menubar, tearoff=0)
menubar.add_cascade(label='О программе', menu=about)
about.add_command(label='О программе', command=abouta)

window.config(menu=menubar)


def change_dictionary():
    """Change global dictionary and show it size"""
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

window.mainloop()
db.close()
