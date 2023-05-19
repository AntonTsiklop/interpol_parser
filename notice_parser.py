"""
Данные получены с помощью Interpol Notices API https://interpol.api.bund.dev.
Перебор по фамилиям A-Z + перебор по именам A-Z, если запрос включает более 160 элементов,
то добавляется фильтр по возрасту: 18-30, 30-40, 40-50, 50-70, 70-90, 90-110.
Метод parse_notices возвращает список с информацией со страниц, метод parse details
возвращает список с подробной информацией об объектах, метод parse_thumbnails сохраняет
миниатюры в указанную папку, остальные методы спомогательные, функционал понятен из названия.
"""

from string import ascii_uppercase
import requests
import json
import os


class NoticesParser:

    age_max_list = [30, 40, 50, 70, 90, 110]
    age_min_list = [18, 30, 40, 50, 70, 90]

    def __init__(self, link: str):
        self.link = link
        self.data_list = []             # информация об объектах
        self.data_list_detail = []      # подробная информация об объектах
        self.num_of_res = 0             # кол-во результатов

    @staticmethod
    def json_write(data_list: list, filename: str):
        with open(f'{filename}.json', 'a') as f:
            f.write('[\n')
            for el in data_list[:-1]:
                json.dump(el, f)
                f.write(',\n')
            json.dump(data_list[-1], f)
            f.write('\n')
            f.write(']\n')
            f.close()

    @staticmethod
    def save_images(data: list, image_dir: str):
        for el in data:
            try:
                image_request = requests.get(el['_links']['thumbnail']['href']) # тут лежит миниатюра, но она есть
                if not os.path.exists(f'{image_dir}'):                                # не в каждой записи
                    os.mkdir(f'{image_dir}')
                entity_id = el['entity_id'].replace('/', '-')                   # id объекта
                out = open(f"{image_dir}/{entity_id}.jpg", "wb")
                out.write(image_request.content)
                out.close()
            except KeyError:
                pass

    def query(self, char_name: str, char_forename: str, age_max=None, age_min=None):
        params = dict(resultPerPage=200, name=f'^{char_name}', forename=f'^{char_forename}', ageMax=age_max,
                      ageMin=age_min)
        request = requests.get(self.link, params)
        query = request.json()
        total = int(query['total'])                 # кол-во результатов
        data = query['_embedded']['notices']        # словарь, в котором лежит информация об объекте
        return data, total

    def parse_notices(self):
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
                if self.num_of_res > 100:
                    break
            break
        return self.data_list

    def parse_details(self):
        if not self.data_list:
            self.data_list = self.parse_notices()
        for data in self.data_list:
            for el in data:
                detail_request = requests.get(el['_links']['self']['href'])
                self.data_list_detail.append(detail_request.json())
        return self.data_list_detail

    def parse_thumbnails(self, image_dir: str, data_list: list):
        if not data_list:
            self.data_list = self.parse_notices()
        for data in self.data_list:
            self.save_images(data, image_dir)


red_notices = NoticesParser('https://ws-public.interpol.int/notices/v1/red')
red_notices_list = red_notices.parse_notices()
red_notices.json_write(red_notices_list, 'red_notices')
red_notices_details_list = red_notices.parse_details()
red_notices.json_write(red_notices_details_list, 'red_notices_details')
red_notices.parse_thumbnails('images_red', red_notices_list)