"""
Данные получены с помощью Interpol Notices API https://interpol.api.bund.dev.
Перебор по фамилиям A-Z + перебор по именам A-Z, если запрос включает более 160 элементов,
то добавляется фильтр по возрасту: 18-30, 30-40, 40-50, 50-70, 70-90, 90-110.
Метод parse_notices сохраняет данные со страницы View-Red-Notices в текущей рабочей директории, метод
parse_details помимо данных со страницы сохраняет подробные данные об объекте, метод parse_details_with_thumbnails
помимо перечисленного выше сохраняет миниатюры в папке images, остальные методы вспомогательные.
"""

from string import ascii_uppercase
import requests
import json
import os


class NoticeParser:

    age_max_list = [30, 40, 50, 70, 90, 110]
    age_min_list = [18, 30, 40, 50, 70, 90]

    def __init__(self, link: str):
        self.link = link
        self.data_list = []             # информация об объектах
        self.data_list_detail = []      # подробная информация об объектах
        self.num_of_res = 0             # кол-во результатов

    @staticmethod
    def json_write(data_list, filename):
        with open(f'{filename}.json', 'a') as f:
            f.write('[\n')
            for el in data_list[:-1]:
                json.dump(el, f)
                f.write(',\n')
            json.dump(data_list[-1], f)
            f.write('\n')
            f.write(']\n')
            f.close()

    def query(self, char_name: str, char_forename: str, age_max=None, age_min=None):
        params = dict(resultPerPage=200, name=f'^{char_name}', forename=f'^{char_forename}', ageMax=age_max,
                      ageMin=age_min)
        request = requests.get(self.link, params)
        query = request.json()
        total = int(query['total'])                 # кол-во результатов
        data = query['_embedded']['notices']        # словарь, в котором лежит информация об объекте
        return data, total

    def save_images(self, data):
        for el in data:
            try:
                image_request = requests.get(el['_links']['thumbnail']['href']) # тут лежит миниатюра, но она есть
                if not os.path.exists('images'):                                # не в каждой записи
                    os.mkdir('images')
                entity_id = el['entity_id'].replace('/', '-')                   # id объекта
                out = open(f"images/{entity_id}.jpg", "wb")
                out.write(image_request.content)
                out.close()
            except KeyError:
                pass
            detail_request = requests.get(el['_links']['self']['href'])         # тут лежит подробная информация
            self.data_list_detail.append(detail_request.json())                 # об объекте

    def parse_notices(self, filename):
        for char_name in ascii_uppercase:
            for char_forename in ascii_uppercase:
                data, total = self.query(char_name, char_forename)
                if total == 0:
                    continue
                if total > 160:
                    for age_min, age_max in zip(self.age_min_list, self.age_max_list):
                        data, total = self.query(char_name, char_forename, age_max=age_max, age_min=age_min)
                        if total == 0:
                            continue
                        self.num_of_res += total
                        self.data_list.append(data)
                    continue
                self.num_of_res += total
                print(f'Found {self.num_of_res} notices')
                self.data_list.append(data)
        self.json_write(self.data_list, f'{filename}')

    def parse_details(self, filename_notices: str, filename_notices_details: str):
        for char_name in ascii_uppercase:
            for char_forename in ascii_uppercase:
                data, total = self.query(char_name, char_forename)
                if total == 0:
                    continue
                if total > 160:
                    for age_min, age_max in zip(self.age_min_list, self.age_max_list):
                        data, total = self.query(char_name, char_forename, age_max=age_max, age_min=age_min)
                        if total == 0:
                            continue
                        self.num_of_res += total
                        for el in data:
                            detail_request = requests.get(el['_links']['self']['href'])
                            self.data_list_detail.append(detail_request.json())
                        self.data_list.append(data)
                    continue
                self.num_of_res += total
                print(f'Found {self.num_of_res} notices')
                for el in data:
                    detail_request = requests.get(el['_links']['self']['href'])
                    self.data_list_detail.append(detail_request.json())
                self.data_list.append(data)
        self.json_write(self.data_list, f'{filename_notices}')
        self.json_write(self.data_list_detail, f'{filename_notices_details}')

    def parse_details_with_thumbnails(self, filename_notices: str, filename_notices_details: str):
        for char_name in ascii_uppercase:
            for char_forename in ascii_uppercase:
                data, total = self.query(char_name, char_forename)
                if total == 0:
                    continue
                if total > 160:
                    for age_min, age_max in zip(self.age_min_list, self.age_max_list):
                        data, total = self.query(char_name, char_forename, age_max=age_max, age_min=age_min)
                        if total == 0:
                            continue
                        self.num_of_res += total
                        self.save_images(data)
                        self.data_list.append(data)
                    continue
                self.num_of_res += total
                print(f'Found {self.num_of_res} notices')
                self.save_images(data)
                self.data_list.append(data)
        self.json_write(self.data_list, f'{filename_notices}')
        self.json_write(self.data_list_detail, f'{filename_notices_details}')


red_notices = NoticeParser('https://ws-public.interpol.int/notices/v1/red')
# red_notices.parse_notices('results')
# red_notices.parse_details('results', 'results_details')
red_notices.parse_details_with_thumbnails('results', 'results_details')