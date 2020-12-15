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
            self.date_s = datetime.date(1900, 1, 1)
            self.date_e = datetime.date.today()
            self.db = dict()
            self.load_db()

        def load_db(self):
            if not os.path.isdir(self.arch_dir):
                os.mkdir(self.arch_dir)
            db_filename = self.arch_dir + f'\\{self.curr_id}.dat'
            if not os.path.isfile(db_filename):
                self.update_db(db_filename, datetime.date(1900, 1, 1), datetime.date.today())
            else:
                with open(db_filename, 'rb') as dbfile:
                    self.date_s = pickle.load(dbfile)
                    self.date_e = pickle.load(dbfile)
                    self.db = pickle.load(dbfile)
                if self.date_e < datetime.date.today():
                    self.update_db(db_filename, self.date_e, datetime.date.today())
                else:
                    if self.trace:
                        print(f'History: Файл с историей \'{self.curr_id}\' уже есть - подгрузили в память')

        def update_db(self, db_filename: str, date_s, date_e):
            url = r'http://www.cbr.ru/scripts/XML_dynamic.asp'
            date_start = date_s.strftime('%d/%m/%Y')
            date_end = date_e.strftime('%d/%m/%Y')

            if self.trace:
                print(f'History: Запрашиваем историю для {self.curr_id} {date_start}:{date_end} у сервера ЦБ')

            params = {'VAL_NM_RQ': self.curr_id, 'date_req1': date_start, 'date_req2': date_end}
            resp = requests.get(url, params)
            if self.trace:
                print(f'History: {resp.status_code}')

            if resp.status_code == 200 and len(resp.text):
                converted = 0
                xml_tree = Xml.fromstring(resp.text)
                xml_tree_len = len(xml_tree)
                for record in xml_tree:
                    nominal = record.find('Value').text
                    nominal = int(nominal) if len(nominal) and nominal.isdigit() else 1
                    value = record.find('Value').text
                    self.db[self.cnv_date(record.attrib['Date'])] = self.cnv_to_float(value) / nominal
                    converted += 1

                    if self.trace:
                        percent = int(converted / xml_tree_len * 100)
                        utils.pbprint('History', percent, f'записей {converted}')
                    
                date_e = self.cnv_date(xml_tree.attrib['DateRange2'])
                if date_e > self.date_e:
                    self.date_e = date_end
                with open(db_filename, 'wb') as db_file:
                    pickle.dump(self.date_s, db_file)
                    pickle.dump(self.date_e, db_file)
                    pickle.dump(self.db, db_file)

                    if self.trace:
                        print(f'History: сохранили историю в файл \'{self.curr_id}.dat\'')

            return resp.status_code

        @staticmethod
        def cnv_date(date_str: str):
            return parser.parse(date_str, dayfirst=True).date()

        @staticmethod
        def cnv_to_float(value: str):
            return float(value.replace(',', '.'))

    def __init__(self, for_currency: str, **kwargs):
        self.trace = False
        self.precision = None

        for kw_key, kw_value in kwargs.items():
            if kw_key == 'precision' and type(kw_value) == int and 0 <= kw_value < 21:
                self.precision = kw_value
            elif kw_key == 'trace' and type(kw_value) == bool:
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

    def __getitem__(self, some):
        if isinstance(some, datetime.date):
            _date = some
        elif isinstance(some, str):
            _date = self.__convert_date(some)
        elif isinstance(some, slice):
            return self.__rates.db.__getitem__(some)
        else:
            raise TypeError('Работаем только со строками или datetime.date')

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


if __name__ == '__main__':

    import pandas as pd
    
    currencies = []
    curr_dict = CurrDB().find()  # все валюты
    for curr_id, curr_info in curr_dict.items():
        iso_code = curr_info['ISO']
        rus_name = curr_info['RUSNAME']
        curr_num = curr_info['NUM']
        print(f'Обрабатываем запрос для: Currency(\'{curr_id}\') \'{iso_code}\':{curr_num}:\'{rus_name}\'')
        currencies.append(Currency(curr_id, precision=2, trace=True))

    xls_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    need_save = ['USD', 'EUR']
    date = datetime.date.today() - datetime.timedelta(days=180)
    print(f'Создаём файлы .xlsx для:{need_save} за последние полгода...')
    for currency in currencies:
        if currency.iso_code in need_save:
            delta = float(0)
            col_rate = f'Курс {currency.iso_code}'
            db = {'Дата': [], col_rate: [], 'Дельта': []}
            for k, v in currency:
                delta = v - delta
                if k > date:
                    db['Дата'].append(k)
                    db[col_rate].append(v)
                    db['Дельта'].append(delta)
                delta = v
            df = pd.DataFrame(db)
            df.to_excel(xls_dir + f'\\{currency.iso_code}.xlsx', sheet_name='Rates', index=False)
