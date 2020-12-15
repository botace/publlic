# Запрос/сохранение/навигация информации о валютах
# Используем инфу ЦБР

import re
import xml.etree.ElementTree as Xml
import os
import requests
import pickle
import utils


class CurrenciesDB:

    # храним словарь по валютам
    # Общий для всех экзепляров
    # он может быть дефолтным, либо
    # подгружен из сохранёнки по данным из ЦБР
    __db = {
        'R01235': {'ISO': 'USD', },
        'R01239': {'ISO': 'EUR', },
        'R01820': {'ISO': 'JPY', },
    }
    __db_loaded = False

    def __init__(self, trace=False):
        self.trace = trace
        self.__load_db()

    def __gen_public(self):
        for item in self.__db.items():
            yield item

    def __iter__(self):
        return self.__gen_public()

    def __create_file_cbr_val(self, filename: str):
        url = r'http://www.cbr.ru/scripts/XML_valFull.asp'
        if self.trace:
            print('CurrenciesDB: Запрашиваем список валют у сервера ЦБ')

        try:
            resp = requests.get(url)
        except:
            if self.trace:
                print('CurrenciesDB: Ошибка обращения к серверу ЦБ')
            return

        if self.trace:
            print(f'CurrenciesDB: {resp.status_code}')
        if resp.status_code == 200 and len(resp.text):
            with open(filename, 'w') as xmlfile:
                xmlfile.write(resp.text)

    def __convert_xmlfile_to_dict(self, filename: str):
        db = {}
        data = Xml.parse(filename)
        if self.trace:
            print('CurrenciesDB: Конвертируем xml файл с данными о валютах в словарь')
        converted = 0
        for item in data.getroot():
            db[item.get('ID')] = {
                'ISO': item.find('ISO_Char_Code').text,
                'NUM': utils.str2int(item.find('ISO_Num_Code').text, None),
                'ENGNAME': item.find('EngName').text,
                'RUSNAME': item.find('Name').text,
                'NOMINAL': utils.str2int(item.find('Nominal').text, None),
                }
            converted += 1
        if self.trace:
            print(f'CurrenciesDB: Валют в словаре - {converted}')
        return db

    def __load_db(self):
        """ Метод подгружает данные из файла со словарём
            Если файла нет, то идёт запрос к серверу ЦБ и
            сохранение этих данных в словарь + на диск
        """
        if CurrenciesDB.__db_loaded is True:
            return

        db = {}
        module_dir = os.path.dirname(os.path.abspath(__file__))
        module_dir += r'\currencies'
        if not os.path.isdir(module_dir):
            os.mkdir(module_dir)
        db_filename = module_dir + r'\currencies.dict'
        if not os.path.isfile(db_filename):
            xml_filename = module_dir + r'\cbr_valFull.xml'
            if not os.path.isfile(xml_filename):
                self.__create_file_cbr_val(xml_filename)
            if os.path.isfile(xml_filename):  # если удалось загрузить данные с ЦБ
                db = self.__convert_xmlfile_to_dict(xml_filename)
                with open(db_filename, 'wb') as db_file:
                    pickle.dump(db, db_file)
        else:
            with open(db_filename, 'rb') as db_file:
                db = pickle.load(db_file)

        db_size = len(db)
        if db_size > 0:
            CurrenciesDB.__db = db
            CurrenciesDB.__db_loaded = True
        else:
            db_size = len(CurrenciesDB.__db)
        if self.trace:
            print(f'CurrenciesDB: Размер словаря - {db_size}')

    def find(self, some=None):
        """ Метод из some строит список с разделителем ' '
            и ищет для каждого элемента из этого списка
            вхождения в словаре по валютам.
            Для полей ENGNAME,RUSNAME можно использовать regex
            
            На выходе словарь всех найденных вхождений при поиске:
                {
                    'Rxxxxx': {'ISO': '...', 'NUM':xxx, ... },
                    'Rxxxxx': {'ISO': '...', 'NUM':xxx, ... },
                    ...
                }
        """
        if some is None:
            return self.__db
        elif type(some) == str:
            some = some.split(' ')
        elif type(some) == int:
            some = [some]
        if not hasattr(some, '__iter__'):
            raise TypeError('Недопустимый запрос для поиска', type(some))

        def check_dict(mask, items):
            for item in items:
                if re.match(mask, item):
                    return True
            return False

        def check_dict2(mask, items):
            for item in items:
                if mask in item:
                    return True
            return False

        ret = {}
        if self.trace:
            print(f'CurrenciesDB: обрабатываем запрос поиска:\'{some}\'')
        for value in some:
            # Отдельный случай, когда у нас инт - мы ищем у всех валют только среди 'NUM'
            if type(value) == int:
                if self.trace:
                    print(f'CurrenciesDB: Ищем по базе валюту с NUM == {value}')
                for item_k, item_v in self.__db.items():
                    v_num = item_v['NUM']
                    # print(f'item_k={item_k}, value={value}, v_num={v_num}')
                    if v_num == value and item_k not in ret:
                        ret[item_k] = item_v
                        break
            else:
                if type(value) != str:
                    raise TypeError('Допустим только тип str')
                for item_k, item_v in self.__db.items():
                    if value == item_k and item_k not in ret:
                        ret[item_k] = item_v
                        break
                    else:
                        v = value.split(':')
                        if len(v) == 1:
                            v0 = v[0]
                            # ищем среди ISO,ENGNAME,RUSNAME
                            if self.trace:
                                print(f'CurrenciesDB: Ищем среди ISO,ENGNAME,RUSNAME')
                            iso_c = item_v['ISO'] if item_v['ISO'] is not None else ''
                            check_list = list(filter(lambda o: o is not None, [item_v['ENGNAME'], item_v['RUSNAME']]))

                            if v0.upper() == iso_c or check_dict(v0, check_list) or check_dict2(v0, check_list):
                                if item_k not in ret:
                                    ret[item_k] = item_v
                        else:
                            # ищем по сочетанию key:value
                            k = v[0].upper()
                            v1 = v[1]
                            if k == 'ISO':
                                v1 = v1.upper()

                            if self.trace:
                                print(f'CurrenciesDB: Ищем по сочетанию {k}:{v1}')

                            if k in item_v and item_v[k] is not None and (re.match(v1, item_v[k]) or v1 in item_v[k]):
                                if item_k not in ret:
                                    ret[item_k] = item_v
        return ret


if __name__ == '__main__':

    import pprint

    info = CurrenciesDB(trace=True)
    test_st = r'R01820 iso:usd eur EngName:[\w\W]+Dollar юань'
    print(f'Тестовая строка поиска:\'{test_st}\'')
    pprint.pp(info.find(test_st))
