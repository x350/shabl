import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog

from docxtpl import DocxTemplate
from num2words import num2words
from pathlib import Path
import datetime


# font = 'TimesNewRoman 10'
# font = 'CourierNew

class Window:
    def __init__(self, width=860, height=860, title='ВВК', icon=None):
        self.root = tk.Tk()
        self.root.title(title)
        self.width = width
        self.height = height
        self.root.geometry(f"{self.width}x{self.height}+50+10")
        if icon:
            self.root.iconbitmap(icon)
        self.root.bind("<Control-KeyPress>", self.keypress)

        self.tabs_control = ttk.Notebook(self.root, width=self.width - 20, padding=(10,))
        self.tabs_control.enable_traversal()
        self.tab_1 = tk.Frame(self.tabs_control)
        self.tab_2 = tk.Frame(self.tabs_control)
        self.tab_3 = tk.Frame(self.tabs_control)

        self.tabs_control.add(self.tab_1, text="Данные больного")
        self.tabs_control.add(self.tab_2, text='Объективный статус')
        self.tabs_control.add(self.tab_3, text='Прочие данные')

        self.menu = tk.Menu(tearoff=0)
        self.menu.add_command(label="Вырезать", accelerator="Ctrl+X",
                              command=lambda: self.w.focus_force() or self.w.event_generate("<<Cut>>"))
        self.menu.add_command(label="Копировать", accelerator="Ctrl+С",
                              command=lambda: self.w.focus_force() or self.w.event_generate("<<Copy>>"))
        self.menu.add_command(label="Вставить", accelerator="Ctrl+V",
                              command=lambda: self.w.focus_force() or self.w.event_generate("<<Paste>>"))
        self.menu.add_command(label="Удалить", accelerator="Delete",
                              command=lambda: self.w.focus_force() or self.w.event_generate("<<Clear>>"))
        self.menu.add_separator()
        self.menu.add_command(label="Выделить все", accelerator="Ctrl+A",
                              command=lambda: self.w.focus_force() or self.w.event_generate("<<SelectAll>>"))

        self.menu.bind_class("Entry", "<Button-3><ButtonRelease-3>", self.func)
        self.menu.bind_class("Text", "<Button-3><ButtonRelease-3>", self.func)

        self._who_is = {
            1: "По контракту",
            2: "Мобилизован",
            3: "По призыву"
        }

        self._damages = {
            1: 'Легкое увечье',
            2: 'Тяжелое увечье',
            3: 'Не входит в перечень'}
        self._rest_var = tk.IntVar()
        self._rest_var.set(3)

        self.context = {'data_vvk': tk.StringVar(),
                        'data_damage': tk.StringVar(),
                        'fio': tk.StringVar(),
                        'birthday': tk.StringVar(),
                        'rang': tk.StringVar(),
                        'vch': tk.StringVar(),
                        'priziv': tk.StringVar(),
                        'dembel': tk.StringVar(),
                        'voenkomat': tk.StringVar(),
                        'mobil': tk.StringVar(),
                        'mobil_voenkomat': tk.StringVar(),
                        'contract_start': tk.StringVar(),
                        'contract_end': tk.StringVar(),
                        'contract_with': tk.StringVar(),
                        'nomber_l': tk.StringVar(),
                        'complaints': tk.StringVar(),  # None,
                        'anamnes': tk.StringVar(),
                        'diagnosis': tk.StringVar(),
                        # 'damages': self._damages[['damage_var']],
                        'damage_var': tk.IntVar(),
                        'who_is': tk.IntVar(),
                        'hospitals': [],
                        # 'rests': rests[rest_var.get()],
                        # 'rest_var': rest_var.get(),
                        'status': tk.StringVar(),
                        'analis': tk.StringVar(),
                        # 'rest_var': tk.IntVar(),
                        'srok': tk.IntVar(),
                        'statia': tk.IntVar(),
                        'oper': [],
                        'f_100': tk.StringVar(),
                        'f_100_data': tk.StringVar(),
                        'adres': tk.StringVar(),
                        'otdel': tk.StringVar(),
                        'slave': tk.StringVar(),
                        'boss': tk.StringVar(),
                        }
        self.context['srok'].set(60)
        self.context['statia'].set(0)
        # self.context['rest_var'].set(3)

        self._hosp = tk.StringVar()
        self._hosp_start = tk.StringVar()
        self._hosp_end = tk.StringVar()
        self._added = tk.StringVar()
        self._oper = tk.StringVar()
        self._oper_name = tk.StringVar()
        self._oper_date = tk.StringVar()

    dnevnik = '''Состояние удовлетворительное. Дыхание везикулярное, проводится во все отделы, хрипов нет. 
Пульс 72 в 1 мин. ритмичный. АД 123/76 мм рт. ст.. Язык влажный. Живот не вздут, мягкий, безболезненный во всех отделах.Поколачивание по поясничной области безболезненно. Стул и мочеиспускание в норме. Диурез достаточный.
Местный статус: '''

    analizi = '''Общий анализ крови от :гемоглобин г/л, эритроциты х10/12, лейкоциты х10/9, тромбоциты х10/9;
Общий анализ мочи от : в пределах нормы;
Биохимический анализ крови от :Общий белок г/л, общий билирубин мкмоль/л, мочевина ммоль/л., креатинин мкмоль/л, АлАТ ед/л, АсАТ ед/л.
Флюорография от : Очаговых и инфильтративных теней не выявлено.'''

    def func(self, event):
        self.menu.post(event.x_root, event.y_root)
        self.w = event.widget

    def run(self):
        self.draw_widgets()
        self.root.mainloop()

    @staticmethod
    def keypress(event):
        # print(event.keycode)
        if event.keycode == 86:
            event.widget.event_generate('<<Paste>>')
        elif event.keycode == 67:
            event.widget.event_generate('<<Copy>>')
        elif event.keycode == 88:
            event.widget.event_generate('<<Cut>>')
        elif event.keycode == 65:
            event.widget.event_generate('<<SelectAll>>')

    def add_hosp(self):
        var = [self._hosp.get(), self._hosp_start.get(), self._hosp_end.get()]
        for item in var:
            if not item:
                return
        self.context['hospitals'].append(var)
        var = ''
        for item in self.context['hospitals']:
            var += item[0][:70] + ' с ' + item[1] + ' по ' + item[2] + '... ' + '.\n'

        self._added.set(var)
        self._hosp.set('')
        self._hosp_start.set('')
        self._hosp_end.set('')

    def del_hosp(self):
        if self.context['hospitals']:
            self.context['hospitals'].pop()
        var = ''
        for item in self.context['hospitals']:
            var += item[0][:70] + ' с ' + item[1] + ' по ' + item[2] + '... ' + '.\n'
        self._added.set(var)

    def add_oper(self):
        var = [self._oper_date.get(), self._oper_name.get()]
        for item in var:
            if not item:
                return
        self.context['oper'].append(var)
        var = ''
        for item in self.context['oper']:
            var += 'Операция от ' + item[0] + 'г.: ' + item[1][:70] + '... ;' + '\n'

        self._oper.set(var)
        self._oper_name.set('')
        self._oper_date.set('')

    def del_oper(self):
        if self.context['oper']:
            self.context['oper'].pop()
        var = ''
        var = ''
        for item in self.context['oper']:
            var += 'Операция от ' + item[0] + ': ' + item[1][:70] + '... '  '.\n'
        self._oper.set(var)

    def get_zakluchenie(self):
        if self._rest_var.get() == 1:
            return f"На основании статьи «{self.context['statia'].get()}» графы III Расписания болезней* «Г» –  временно не годен к \
военной службе, необходимо предоставить бесплатную медицинскую реабилитацию в военном санатории \
на срок 21 сутки."
        elif self._rest_var.get() == 2:
            return ''
        elif self._rest_var.get() == 3:
            return f"На основании статьи «{self.context['statia'].get()}» графы III Расписания болезней* «Г» – временно \
не годен к военной службе, необходимо предоставить отпуск по болезни сроком \
на {self.context['srok'].get()} ({num2words(self.context['srok'].get(), lang='ru')}) суток."

    def get_context(self):
        rend = {'data_vvk': self.context['data_vvk'].get(),
                'data_damage': (self.context['data_damage'].get()),
                'fio': self.context['fio'].get(),
                'birthday': self.context['birthday'].get(),
                'rang': self.context['rang'].get(),
                'vch': self.context['vch'].get(),
                'who_is': self._who_is[self.context['who_is'].get()],
                'priziv': self.context['priziv'].get(),
                'dembel': self.context['dembel'].get(),
                'mobil': self.context['mobil'].get(),
                'voenkomat': self.context['voenkomat'].get(),
                'mobil_voenkomat': self.context['mobil_voenkomat'].get(),
                'contract_start': self.context['contract_start'].get(),
                'contract_end': self.context['contract_end'].get(),
                'contract_with': self.context['contract_with'].get(),
                'nomber_l': self.context['nomber_l'].get(),
                'complaints': self.context['complaints'].get("1.0", tk.END).strip(),  # get("1.0",'end-1c'),
                'anamnes': self.context['anamnes'].get("1.0", tk.END).strip(),
                'diagnosis': self.context['diagnosis'].get("1.0", tk.END).strip(),
                'damage': self._damages[self.context['damage_var'].get()],
                'hospitals_predst': ', '.join(
                    [f'{item[0]} с {item[1]} по {item[2]}' for item in self.context['hospitals']]),
                'hospitals_spravka': ', '.join(
                    [f'c {item[1]} по {item[2]} в {item[0]}' for item in self.context['hospitals']]),
                'status': self.context['status'].get("1.0", tk.END).strip(),
                'analis': self.context['analis'].get("1.0", tk.END).strip(),
                'srok': self.context['srok'].get(),
                'statia': self.context['statia'].get(),
                'oper': ', '.join([
                    f'Операция от {item[0]}: {item[1]}.' for item in self.context['oper']
                ]), #   .capitalize(),
                'f_100': self.context['f_100'].get(),
                'f_100_data': self.context['f_100_data'].get(),
                'adres': self.context['adres'].get(),
                'otdel': self.context['otdel'].get(),
                'zakluchenie': self.get_zakluchenie(),
                'boss': self.context['boss'].get(),
                'slave': self.context['slave'].get(),
                }
        return rend

    def make_rest(self):
        if self._rest_var.get() == 3:
            self.tab_3.children['!entry6'].grid(row=11, column=4, stick='w', padx=5, pady=5)
            self.tab_3.children['!label8'].grid(row=12, columnspan=2, column=2, stick='e', padx=5, pady=5)
            self.tab_3.children['!entry7'].grid(row=12, column=4, stick='w', padx=5, pady=5)
        else:
            # self.context['srok'].set(0)
            self.tab_3.children['!entry6'].grid_remove()
            self.tab_3.children['!label8'].grid_remove()
            self.tab_3.children['!entry7'].grid_remove()

    def make_view_vk(self):
        if self.context['who_is'].get() == 1:  # контракт
            self.tab_1.children['!label11'].grid(row=7, column=0, stick='we', padx=5, pady=5)
            self.tab_1.children['!label12'].grid(row=7, column=2, stick='w', padx=5, pady=5)
            self.tab_1.children['!label13'].grid(row=8, column=0, stick='we', padx=5, pady=5)

            self.tab_1.children['!entry10'].grid(row=7, column=1, stick='we', padx=5, pady=5)
            self.tab_1.children['!entry11'].grid(row=7, column=3, stick='we', padx=5, pady=5)
            self.tab_1.children['!entry12'].grid(row=8, column=1, columnspan=2, stick='we', padx=5, pady=5)


            self.tab_1.children['!label14'].grid_remove()
            self.tab_1.children['!label15'].grid_remove()
            self.tab_1.children['!entry13'].grid_remove()
            self.tab_1.children['!entry14'].grid_remove()
        elif self.context['who_is'].get() == 2: # мобилизован

            self.tab_1.children['!label14'].grid(row=9, column=0, stick='we', padx=5, pady=5)
            self.tab_1.children['!label15'].grid(row=10, column=0, stick='w', padx=5, pady=5)
            self.tab_1.children['!entry13'].grid(row=9, column=1, stick='we', padx=5, pady=5)
            self.tab_1.children['!entry14'].grid(row=10, column=1, columnspan=2, stick='we', padx=5, pady=5)

            self.tab_1.children['!label11'].grid_remove()
            self.tab_1.children['!label12'].grid_remove()
            self.tab_1.children['!label13'].grid_remove()
            self.tab_1.children['!entry10'].grid_remove()
            self.tab_1.children['!entry11'].grid_remove()
            self.tab_1.children['!entry12'].grid_remove()


        elif self.context['who_is'].get() == 3: # призыв
            self.tab_1.children['!label11'].grid_remove()
            self.tab_1.children['!label12'].grid_remove()
            self.tab_1.children['!label13'].grid_remove()
            self.tab_1.children['!label14'].grid_remove()
            self.tab_1.children['!label15'].grid_remove()
            self.tab_1.children['!entry10'].grid_remove()
            self.tab_1.children['!entry11'].grid_remove()
            self.tab_1.children['!entry12'].grid_remove()
            self.tab_1.children['!entry13'].grid_remove()
            self.tab_1.children['!entry14'].grid_remove()


    def write_file(self, path_dir, file_name, context):
        document = DocxTemplate(Path('doc') / file_name)
        document.render(context)
        document.save(Path(path_dir) / file_name)

    def make_all(self):
        path_dir = filedialog.askdirectory()
        context = self.get_context()
        if not context['priziv']:
            context['priziv'] = 'не служил'
        if self.context['who_is'].get() == 1: # по контракту
            self.write_file(path_dir, 'protokol_kont.docx', context)
            self.write_file(path_dir, 'predstavl.docx', context)
            self.write_file(path_dir, 'raport.docx', context)
            self.write_file(path_dir, 'spravka_o_tajest.docx', context)
            if self.context['statia'].get():
                self.write_file(path_dir, 'zakl_hist_bol.docx', context)
                self.write_file(path_dir, 'zakl_f12.docx', context)
            else:
                self.write_file(path_dir, 'zakl_hist_bol_bez_stati.docx', context)

        if self.context['who_is'].get() == 2: # мобилизован
            self.write_file(path_dir, 'protokol_mobil.docx', context)
            self.write_file(path_dir, 'predstavl_mob.docx', context)
            self.write_file(path_dir, 'raport.docx', context)
            self.write_file(path_dir, 'spravka_o_tajest.docx', context)
            if self.context['statia'].get():
                self.write_file(path_dir, 'zakl_hist_bol.docx', context)
                self.write_file(path_dir, 'zakl_f12_mobil.docx', context)
            else:
                self.write_file(path_dir, 'zakl_hist_bol_bez_stati.docx', context)

        if self.context['who_is'].get() == 3: # по призыву
            self.write_file(path_dir, 'protokol_priziv.docx', context)
            self.write_file(path_dir, 'predstavl_sroch.docx', context)
            self.write_file(path_dir, 'raport_priziv.docx', context)
            self.write_file(path_dir, 'spravka_o_tajest_priziv.docx', context)
            if self.context['statia'].get():
                self.write_file(path_dir, 'zakl_hist_bol.docx', context)
                self.write_file(path_dir, 'zakl_f12_priziv.docx', context)
            else:
                self.write_file(path_dir, 'zakl_hist_bol_bez_stati.docx', context)





    def draw_widgets(self):
        self.tabs_control.grid(sticky='WE')
        # row 0
        tk.Label(self.tab_1, text='Дата представления на ВВК:').grid(row=0, column=0, stick='we', padx=5, pady=5)
        data_vvk = tk.Entry(self.tab_1, width=10, textvariable=self.context['data_vvk'])
        data_vvk.grid(row=0, column=1, stick='w', padx=5, pady=5)
        #
        tk.Label(self.tab_1, text='Дата травмы:').grid(row=0, column=2, stick='we', padx=5, pady=5)
        data_damage = tk.Entry(self.tab_1, width=10, textvariable=self.context['data_damage'])
        data_damage.grid(row=0, column=3, stick='w', padx=5, pady=5)
        #
        btn_1 = tk.Button(self.tab_1, text='Сброс', bg='#ff6666', command=self.sbros)
        btn_1.grid(row=0, column=4, stick='we', padx=5, pady=5)

        tk.Label(self.tab_1, text='ФИО:').grid(row=1, column=0, stick='we', padx=5, pady=5)
        fio = tk.Entry(self.tab_1, width=40, textvariable=self.context['fio'])
        fio.grid(row=1, column=1, columnspan=2, stick='we', padx=5, pady=5)

        tk.Label(self.tab_1, text='Дата рождения:').grid(row=1, column=3, stick='we', padx=5, pady=5)
        birthday = tk.Entry(self.tab_1, width=10, textvariable=self.context['birthday'])
        birthday.grid(row=1, column=4, stick='w', padx=5, pady=5)
        #
        tk.Label(self.tab_1, text='Звание:').grid(row=2, column=0, stick='we', padx=5, pady=5)
        rang = tk.Entry(self.tab_1, width=42, textvariable=self.context['rang'])
        rang.grid(row=2, column=1, columnspan=2, stick='we', padx=5, pady=5)

        tk.Label(self.tab_1, text='Воинская часть:').grid(row=2, column=3, stick='we', padx=5, pady=5)
        vch = tk.Entry(self.tab_1, width=10, textvariable=self.context['vch'])
        vch.grid(row=2, column=4, stick='we', padx=5, pady=5)
        #
        tk.Label(self.tab_1, text='Категория:').grid(row=3, column=0, stick='we', padx=5, pady=5)
        for ind, who in enumerate(sorted(self._who_is)):
            tk.Radiobutton(self.tab_1, text=self._who_is[who], variable=self.context['who_is'], value=who,
                           command=self.make_view_vk).grid(row=3, column=1 + ind, stick='we', padx=5, pady=5)
        self.context['who_is'].set(1)

        #
        tk.Label(self.tab_1, text='Дата призыва, с:').grid(row=5, column=0, stick='we', padx=5, pady=5)
        priziv = tk.Entry(self.tab_1, width=10, textvariable=self.context['priziv'])
        priziv.grid(row=5, column=1, stick='w', padx=5, pady=5)
        #
        tk.Label(self.tab_1, text='по:').grid(row=5, column=2, stick='we', padx=5, pady=5)
        dembel = tk.Entry(self.tab_1, width=10, textvariable=self.context['dembel'])
        dembel.grid(row=5, column=3, stick='w', padx=5, pady=5)

        tk.Label(self.tab_1, text='Военкомат (призыв):').grid(row=6, column=0, stick='we', padx=5, pady=5)
        voenkomat = tk.Entry(self.tab_1, width=50, textvariable=self.context['voenkomat'])
        voenkomat.grid(row=6, column=1, columnspan=2, stick='we', padx=5, pady=5)
        #


        #

        tk.Label(self.tab_1, text='Начало последнего контракта:').grid(row=7, column=0, stick='we', padx=5, pady=5)
        contract_start = tk.Entry(self.tab_1, width=10, textvariable=self.context['contract_start'])
        contract_start.grid(row=7, column=1, stick='w', padx=5, pady=5)
        #
        tk.Label(self.tab_1, text='Окончание последнего контракта:').grid(row=7, column=2, stick='w', padx=5, pady=5)
        contract_end = tk.Entry(self.tab_1, width=10, textvariable=self.context['contract_end'])
        contract_end.grid(row=7, column=3, stick='w', padx=5, pady=5)
        #
        tk.Label(self.tab_1, text='Контракт заключен с:').grid(row=8, column=0, stick='we', padx=5, pady=5)
        contract_with = tk.Entry(self.tab_1, width=25, textvariable=self.context['contract_with'])
        contract_with.grid(row=8, column=1, columnspan=2, stick='we', padx=5, pady=5)

        #
        tk.Label(self.tab_1, text='Дата мобилизации:').grid(row=9, column=0, stick='w', padx=5, pady=5)
        mobil = tk.Entry(self.tab_1, width=10, textvariable=self.context['mobil'])
        mobil.grid(row=9, column=1, stick='w', padx=5, pady=5)
        #

        tk.Label(self.tab_1, text='Военкомат (мобилизация):').grid(row=10, column=0, stick='we', padx=5, pady=5)
        mobil_voenkomat = tk.Entry(self.tab_1, width=50, textvariable=self.context['mobil_voenkomat'])
        mobil_voenkomat.grid(row=10, column=1, columnspan=2, stick='w', padx=5, pady=5)
        #

        self.tab_1.children['!entry13'].grid_remove()
        self.tab_1.children['!entry14'].grid_remove()
        self.tab_1.children['!label14'].grid_remove()
        self.tab_1.children['!label15'].grid_remove()
        #

        tk.Label(self.tab_1, text='Личный номер:').grid(row=11, column=0, stick='we', padx=5, pady=5)
        nomber_l = tk.Entry(self.tab_1, width=10, textvariable=self.context['nomber_l'])
        nomber_l.grid(row=11, column=1, stick='we', padx=5, pady=5)

        tk.Label(self.tab_1, text='Данные о травме подтверждены:').grid(row=12, column=0, stick='we', padx=5, pady=5)
        f_100 = tk.Entry(self.tab_1, textvariable=self.context['f_100'])
        f_100.grid(row=12, column=1, stick='we', columnspan=2, padx=5, pady=5)

        tk.Label(self.tab_1, text='Дата подтверждения:').grid(row=12, column=3, stick='we', padx=5, pady=5)
        f_100_data = tk.Entry(self.tab_1, width=10, textvariable=self.context['f_100_data'])
        f_100_data.grid(row=12, column=4, stick='w', padx=5, pady=5)

        # tk.Label(self.tab_1, text='Адрес для отправки заключения:').grid(row=9, column=0, stick='we', padx=5, pady=5)
        # f_100_data = tk.Entry(self.tab_1, textvariable=self.context['adres'])
        # f_100_data.grid(row=10, column=1, columnspan=3, stick='we', padx=5, pady=5)

        # Место для реализации радиобатон с выбором типа ВВК: тяжесть, годность, тяжесть с годностью
        # адрес выше, только диагноз на годность и добавить соответствующие шаблоны файлы в doc

        btn_2 = tk.Button(self.tab_1, text='Следующая вкладка', bg='#72aee6',
                          command=(lambda: self.tabs_control.select(self.tab_2)))
        btn_2.grid(row=13, column=4, stick='we', padx=5, pady=5)
        #
        # # row 6-7
        tk.Label(self.tab_2, text='Жалобы:').grid(row=0, columnspan=4, column=0, stick='we', padx=5, pady=5)
        self.context['complaints'] = ScrolledText(self.tab_2, height=2, wrap=tk.WORD, width=97)

        self.context['complaints'].grid(row=1, column=0, columnspan=5, stick='we', padx=5, pady=5)
        #
        tk.Label(self.tab_2, text='Анамнез:').grid(row=2, columnspan=4, column=0, stick='we', padx=5, pady=5)
        self.context['anamnes'] = ScrolledText(self.tab_2, height=12, wrap=tk.WORD, width=97)
        self.context['anamnes'].grid(row=3, column=0, columnspan=5, stick='we', padx=5, pady=5)

        tk.Label(self.tab_2, text='Объективный статус:').grid(row=4, columnspan=4, column=0, stick='we', padx=5, pady=5)
        self.context['status'] = ScrolledText(self.tab_2, height=8, wrap=tk.WORD, width=97)
        self.context['status'].grid(row=5, column=0, columnspan=5, stick='we', padx=5, pady=5)
        self.context['status'].insert("0.0", self.dnevnik)

        tk.Label(self.tab_2, text='Анализы и исследования:').grid(row=6, columnspan=4, column=0, stick='we', padx=5,
                                                                  pady=5)
        self.context['analis'] = ScrolledText(self.tab_2, height=8, wrap=tk.WORD, width=97)
        self.context['analis'].grid(row=7, column=0, columnspan=5, stick='we', padx=5, pady=5)
        self.context['analis'].insert("0.0", self.analizi)

        btn_3 = tk.Button(self.tab_2, text='Предыдущаяя вкладка', bg='#72aee6',
                          command=(lambda: self.tabs_control.select(self.tab_1)))
        btn_3.grid(row=8, column=0, stick='we', padx=5, pady=5)

        btn_4 = tk.Button(self.tab_2, text='Следующая вкладка', bg='#72aee6',
                          command=(lambda: self.tabs_control.select(self.tab_3)))
        btn_4.grid(row=8, column=4, stick='we', padx=5, pady=5)

        tk.Label(self.tab_3, text='Диагноз:').grid(row=0, columnspan=4, column=0, stick='we', padx=5, pady=5)
        self.context['diagnosis'] = ScrolledText(self.tab_3, height=4, wrap=tk.WORD, width=97)
        self.context['diagnosis'].grid(row=1, column=0, columnspan=5, stick='we', padx=5, pady=5)

        #

        tk.Label(self.tab_3, text='Операции: ').grid(row=2, columnspan=3, column=0, stick='we', padx=5, pady=5)
        #
        oper = tk.Label(self.tab_3, textvariable=self._oper, font='CourierNew 10')
        oper.grid(row=3, column=0, stick='w', columnspan=3)
        #

        oper_name = tk.Entry(self.tab_3, width=20, textvariable=self._oper_name)
        oper_name.grid(row=4, column=0, columnspan=4, stick='we', padx=5, pady=5)
        #
        oper_date = tk.Entry(self.tab_3, width=10, textvariable=self._oper_date)
        oper_date.grid(row=4, column=4, stick='w', padx=5, pady=5)
        #

        #
        btn_add_oper = tk.Button(self.tab_3, text='Добавить', bg='#00cccc', command=self.add_oper)
        btn_add_oper.grid(row=5, column=3, stick='we', padx=5, pady=5)

        btn_del_oper = tk.Button(self.tab_3, text='Удалить', bg='#00cccc', command=self.del_oper)
        btn_del_oper.grid(row=5, column=1, stick='we', padx=5, pady=5)

        # damages = {
        #     1: 'Легкое',
        #     2: 'Тяжелое',
        #     3: 'Не входит'
        # }

        self.context['damage_var'].set(1)
        #
        tk.Label(self.tab_3, text='Тяжесть увечья: ').grid(row=6, column=0, stick='we', padx=5, pady=5)
        for ind, damage in enumerate(sorted(self._damages)):
            tk.Radiobutton(self.tab_3, text=self._damages[damage], variable=self.context['damage_var'],
                           value=damage).grid(
                row=6, column=1 + ind, stick='we', padx=5, pady=5
            )

        tk.Label(self.tab_3, text='Находился на лечении, где и с какого числа по какое число:').grid(
            row=7, columnspan=3, stick='we', padx=5,  pady=5)
        #
        added = tk.Label(self.tab_3, textvariable=self._added, font='CourierNew 10')
        added.grid(row=8, column=0, stick='w', columnspan=3)
        #

        hosp = tk.Entry(self.tab_3, width=20, textvariable=self._hosp)
        hosp.grid(row=9, column=0, columnspan=2, stick='we', padx=5, pady=5)
        #
        hosp_start = tk.Entry(self.tab_3, width=10, textvariable=self._hosp_start)
        hosp_start.grid(row=9, column=2, stick='w', padx=5, pady=5)
        #
        hosp_end = tk.Entry(self.tab_3, width=10, textvariable=self._hosp_end)
        hosp_end.grid(row=9, column=3, stick='w', padx=5, pady=5)
        #
        btn_add = tk.Button(self.tab_3, text='Добавить', bg='#00cccc', command=self.add_hosp)
        btn_add.grid(row=10, column=3, stick='we', padx=5, pady=5)

        btn_del = tk.Button(self.tab_3, text='Удалить', bg='#00cccc', command=self.del_hosp)
        btn_del.grid(row=10, column=1, stick='we', padx=5, pady=5)

        rests = {
            1: 'Санаторий',
            2: 'Без освобождения',
            3: 'Освобождение(суток):'
        }
        tk.Label(self.tab_3, text='Выписан в: ').grid(row=11, column=0, stick='we', padx=5, pady=5)
        for ind, rest in enumerate(sorted(rests)):
            tk.Radiobutton(self.tab_3, text=rests[rest], indicatoron=0, variable=self._rest_var, value=rest,
                           command=self.make_rest).grid(row=11, column=1 + ind, stick='we', padx=5, pady=5)


        srok = tk.Entry(self.tab_3, width=3, textvariable=self.context['srok'])
        srok.grid(row=11, column=4, stick='w', padx=5, pady=5)
        # tk.Label(self.tab_3, text='суток').grid(row=11, column=5, stick='w', padx=5, pady=5)

        tk.Label(self.tab_3, text='На основании сатьи:').grid(row=12, columnspan=2, column=2, stick='e', padx=5, pady=5)
        statia = tk.Entry(self.tab_3, width=3, textvariable=self.context['statia'])
        statia.grid(row=12, column=4, stick='w', padx=5, pady=5)

        tk.Label(self.tab_3, text='Отделение:').grid(row=13, columnspan=1, column=0, stick='we', padx=5, pady=5)
        otdel = tk.Entry(self.tab_3, width=3, textvariable=self.context['otdel'])
        otdel.grid(row=13, columnspan=2, column=1, stick='we', padx=5, pady=5)

        tk.Label(self.tab_3, text='Лечащий врач:').grid(row=14, columnspan=1, column=0, stick='we', padx=5, pady=5)
        slave = tk.Entry(self.tab_3, width=3, textvariable=self.context['slave'])
        slave.grid(row=14, columnspan=1, column=1, stick='we', padx=5, pady=5)

        tk.Label(self.tab_3, text='Начальник отделения:').grid(row=14, columnspan=1, column=2, stick='we', padx=5, pady=5)
        boss = tk.Entry(self.tab_3, width=3, textvariable=self.context['boss'])
        boss.grid(row=14, columnspan=1, column=3, stick='we', padx=5, pady=5)

        btn_5 = tk.Button(self.tab_3, text='Предыдущаяя вкладка', bg='#72aee6',
                          command=(lambda: self.tabs_control.select(self.tab_2)))
        btn_5.grid(row=15, column=0, stick='we', padx=5, pady=5)

        btn_send = tk.Button(self.tab_3, text='Готово!', bg='#ff6666', command=self.make_all)
        btn_send.grid(row=16, column=0, columnspan=5, stick='we', padx=5, pady=5)


    def sbros(self):
        for _, item in self.tab_1.children.items():
            if item.widgetName == 'entry':
                item.delete(0, tk.END)
        for _, item in self.tab_3.children.items():
            if item.widgetName == 'entry':
                item.delete(0, tk.END)

        self._oper.set('')
        self._added.set('')

        self.context['complaints'].delete('1.0', tk.END)
        self.context['anamnes'].delete('1.0', tk.END)
        self.context['status'].delete('1.0', tk.END)
        self.context['status'].insert("1.0", self.dnevnik)
        self.context['analis'].delete('1.0', tk.END)
        self.context['analis'].insert("1.0", self.analizi)
        self.context['diagnosis'].delete('1.0', tk.END)


if __name__ == '__main__':
    win = Window()
    win.run()
