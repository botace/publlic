# Запрос/сохранение/навигация информации о валютах
# Используем инфу ЦБР

import datetime 
from dateutil import parser
import os
import sys
import requests
import pickle
import xml.etree.ElementTree as Xml
from currencies import CurrenciesDB as CurrDB
import utils


class Currency:

    class CurrencyHistory:
        """ Данный классик будет отвечать за работу с базой истории
            выбранной валюты
        """

        def __init__(self, currid: str, arch_dir: str, trace: bool):
            """ Инитимся по умолчанию и отправляемся поднимать историю
                из базы на диске, либо создавать её
                
                curr_id     - str, ЦБшный код валюты
                arch_dir    - str, Каталог хранения базы истории
                trace       - bool, Флаг логирования работы методов в консоль
            """
            self.trace = trace
            self.arch_dir = arch_dir
            self.curr_id = currid
            self.date_ask = None
            self.date_s = None
            self.date_e = None
            self.db = dict()
            self.load_db()

        def __get_dbfilename(self):
            return self.arch_dir + f'\\{self.curr_id}.dat'

        def load_db(self):
            if not os.path.isdir(self.arch_dir):
                os.mkdir(self.arch_dir)
            db_filename = self.__get_dbfilename()
            if not os.path.isfile(db_filename):
                self.update_db()
            else:
                with open(db_filename, 'rb') as dbfile:
                    self.date_ask = pickle.load(dbfile)
                    self.date_s = pickle.load(dbfile)
                    self.date_e = pickle.load(dbfile)
                    self.db = pickle.load(dbfile)
                    if self.trace:
                        print(f'History: Файл с историей от {self.date_ask} для периода {self.date_s}:{self.date_e}')

                if self.date_ask < datetime.date.today():
                    if self.trace:
                        print(f'History: Файл с историей устарел - пытаемся обновить историю')
                    self.update_db()
                else:
                    if self.trace:
                        print(f'History: Файл с историей актуален')

        def update_db(self, date_s=None, date_e=None):
            if date_s is None:
                date_s = self.date_e + datetime.timedelta(days=1) if self.date_e is not None else datetime.date(1900, 1, 1)
            if date_e is None:
                date_e = datetime.date.today()
            if date_s > date_e:
                date_s = date_e

            date_start = date_s.strftime('%d/%m/%Y')
            date_end = date_e.strftime('%d/%m/%Y')

            db_filename = self.__get_dbfilename()
            url = r'http://www.cbr.ru/scripts/XML_dynamic.asp'

            if self.trace:
                print(f'History: Запрашиваем историю для {self.curr_id} {date_start}:{date_end} у сервера ЦБ')

            params = {'VAL_NM_RQ': self.curr_id, 'date_req1': date_start, 'date_req2': date_end}

            try:
                resp = requests.get(url, params)
            except:
                if self.trace:
                    print('History: Ошибка обращения к серверу ЦБ')
                return

            if self.trace:
                print(f'History: responce code is {resp.status_code}')

            if resp.status_code == 200 and len(resp.text):

                # with open(db_filename + '.xml', 'w') as xmlfile:
                #    xmlfile.write(resp.text)

                converted = 0
                xml_tree = Xml.fromstring(resp.text)
                xml_tree_len = len(xml_tree)
                for record in xml_tree:
                    nominal = record.find('Value').text
                    nominal = int(nominal) if len(nominal) and nominal.isdigit() else 1
                    value = record.find('Value').text
                    self.db[self.cnv_date(record.attrib['Date'])] = utils.str2float(value) / nominal
                    converted += 1

                    if self.trace:
                        percent = int(converted / xml_tree_len * 100)
                        utils.pbprint('History:', percent, f'записей {converted}')

                if converted == 0:  # нет новых данных
                    if self.trace:
                        print('History: Обновления истории нет')
                    self.date_ask = datetime.date.today()  # когда запрашивали
                    with open(db_filename, 'wb') as db_file:  # но необходимо обновить дату опроса ЦБ
                        pickle.dump(self.date_ask, db_file)
                        pickle.dump(self.date_s, db_file)
                        pickle.dump(self.date_e, db_file)
                        pickle.dump(self.db, db_file)
                    return resp.status_code

                date_sorted = sorted(self.db.keys())
                if len(date_sorted):
                    if self.trace:
                        print('History: from', date_sorted[0], 'to', date_sorted[-1])
                    self.date_ask = datetime.date.today()  # когда запрашивали
                    self.date_s = date_sorted[0]  # первая дата истории
                    self.date_e = date_sorted[-1]  # последняя дата истории
                    with open(db_filename, 'wb') as db_file:
                        pickle.dump(self.date_ask, db_file)
                        pickle.dump(self.date_s, db_file)
                        pickle.dump(self.date_e, db_file)
                        pickle.dump(self.db, db_file)

                        if self.trace:
                            print(f'History: сохранили историю в файл \'{self.curr_id}.dat\'')

            return resp.status_code

        @staticmethod
        def cnv_date(date_str: str):
            return parser.parse(date_str, dayfirst=True).date()

    def __init__(self, for_currency: str, **kwargs):
        self.trace = False

        for kw_key, kw_value in kwargs.items():
            if kw_key == 'trace' and type(kw_value) == bool:
                self.trace = kw_value

        if self.trace:
            print(f'Currency: ищем информацию о валюте по запросу:\'{for_currency}\'')

        _curr_dict = CurrDB().find(for_currency)
        if len(_curr_dict) != 1:
            raise ValueError('Недопустимая строка выбора валюты для работы', _curr_dict)
        item = _curr_dict.popitem()
        self.__curr_info = item[1]
        self.__curr_info['ID'] = item[0]
        arch_dir = os.path.dirname(os.path.abspath(sys.argv[0])) + r'\currencies'
        self.__rates = Currency.CurrencyHistory(self.__curr_info['ID'], arch_dir, self.trace)

    def __repr__(self):
        return f'Currency({self.__curr_info.__repr__()})'

    @property
    def date_min(self):
        if self.__rates.date_ask is None:
            self.__rates.update_db()
        return self.__rates.date_s

    @property
    def date_max(self):
        if self.__rates.date_ask < datetime.date.today():
            self.__rates.update_db()  # автообновление!
        return self.__rates.date_e

    @property
    def info(self): return self.__curr_info

    @property
    def id(self): return self.__curr_info['ID']

    @property
    def iso_code(self): return self.__curr_info['ISO']

    @property
    def iso_num(self): return self.__curr_info['NUM']

    @property
    def rus_name(self): return self.__curr_info['RUSNAME']

    @property
    def eng_name(self): return self.__curr_info['ENGNAME']

    @property
    def nominal(self): return self.__curr_info['NOMINAL']

    @staticmethod
    def __convert_date(date_str):
        return parser.parse(date_str, dayfirst=True).date()

    def get_period(self, date_s='', date_e=''):
        """ Выдаём словарь за период
            date_s/date_e - datetime.date or str
        """
        if isinstance(date_s, datetime.date):
            _date_s = date_s
        elif isinstance(date_s, str):
            _date_s = self.__convert_date(date_s) if len(date_s) else self.date_min
        else:
            raise TypeError('Работаем только с str и datetime.date')
        if isinstance(date_e, datetime.date):
            _date_e = date_e
        elif isinstance(date_e, str):
            _date_e = self.__convert_date(date_e) if len(date_e) else self.date_max
        else:
            raise TypeError('Работаем только с str и datetime.date')

        # автообновление, если хотят дату за пределами нашей текущей истории
        if _date_e > self.__rates.date_e and self.__rates.date_ask < datetime.date.today():
            self.__rates.update_db()

        dates = list(filter(lambda key: _date_s <= key <= _date_e, self.__rates.db.keys()))
        return {_date: self.__rates.db[_date] for _date in dates}

    def __getitem__(self, some):
        if isinstance(some, datetime.date):  # умеем выдавать значение по datetime.data
            _date = some
        elif isinstance(some, str):
            dates_range = some.split(':')
            if len(dates_range) == 2:  # умеем выдавать словарь за период из строки '1 dec:' or '01.01:31.01'
                return self.get_period(dates_range[0], dates_range[1])
            else:
                _date = self.__convert_date(some)  # умеем выдавать значение по дате в строке '2 feb 2019'
        elif isinstance(some, slice):  # умеем выдавать словарь дата:курс по срезу
            if self.__rates.date_ask < datetime.date.today():
                self.__rates.update_db()
            slice_dates = list(self.__rates.db.keys()).__getitem__(some)
            return {_date: self.__rates.db[_date] for _date in slice_dates}
        else:
            raise TypeError('Работаем только с str,str(\':\'),datetime.date,slice')

        # автообновление, если хотят дату за пределами нашей текущей истории
        if _date > self.__rates.date_e and self.__rates.date_ask < datetime.date.today():
            self.__rates.update_db()

        if _date < self.__rates.date_s or _date > self.__rates.date_e:
            return None

        ret = None
        try:
            ret = self.__rates.db.__getitem__(_date)
        except KeyError:
            # нам нужна самая поздняя дата, среди дат, меньших чем искомая
            dates_prev = list(filter(lambda d: d < _date, sorted(self.__rates.db)))
            if len(dates_prev):
                date_closest = dates_prev[-1]  # самая поздняя из этих дат
                ret = self.__rates.db.__getitem__(date_closest)
        return ret

    def __gen_public(self):
        for item in self.__rates.db.items():
            yield item

    def __iter__(self):
        return self.__gen_public()

    def __len__(self):
        return len(self.__rates.db)


if __name__ == '__main__':

    import pandas as pd
    
    currencies = []
    curr_dict = CurrDB(trace=True).find()  # все валюты
    for curr_id, curr_info in curr_dict.items():
        iso_code = curr_info['ISO']
        rus_name = curr_info['RUSNAME']
        curr_num = curr_info['NUM']
        print(f'\nОбрабатываем запрос для: Currency(\'{curr_id}\') \'{iso_code}\':{curr_num}:\'{rus_name}\'')
        currencies.append(Currency(curr_id, trace=True))

    xls_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    need_save = ['USD', 'EUR']
    print(f'\nСоздаём файлы .xlsx для:{need_save} за последние полгода...')

    for currency in currencies:
        if currency.iso_code in need_save:
            delta = None
            col_rate = f'Курс {currency.iso_code}'
            db = {'Дата': [], col_rate: [], 'Дельта': []}
            rates = currency.get_period(datetime.date.today() - datetime.timedelta(days=180))
            for k, v in rates.items():
                delta = v - delta if delta is not None else 0
                db['Дата'].append(k)
                db[col_rate].append(v)
                db['Дельта'].append(float(delta))
                delta = v
            df = pd.DataFrame(db)
            df.to_excel(xls_dir + f'\\{currency.iso_code}.xlsx', sheet_name='Rates', index=False)
