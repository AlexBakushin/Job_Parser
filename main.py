# Импорт необходимых библиотек
import requests
import json
from abc import ABC, abstractmethod


class Parameters:
    """
    Класс для работы с параметрами поиска вакансий на сайтах
    """

    def __init__(self, text='', area='москва', page=0, per_page=10):
        """
        Инициализация основных параметров поиска
        :param text: Ключегое слово для поиска вакансий
        :param area: Регион поиска (город, область, край или вся Россия)
        :param page: Колличество страниц со списками вакансий - не изменяется
        :param per_page: Колличество вакансий проверенных на каждом из сайтов
        """
        self.text = text
        self.area = area
        self.page = page
        self.per_page = per_page

    def get_params(self):
        """
        Вывод всех параметров в виде словаря
        :return: словарь с параметрами поиска
        """
        return {
            'text': self.text,
            'area': self.area,
            'page': self.page,
            'per_page': self.per_page
        }


class Vacancy:
    """
    Класс для работы с вакансиями
    """

    def __init__(self, vacancy):
        """
        Инициализация каждой вакансии
        :param vacancy: список с
        """
        self.__name = vacancy.get('name')
        self.__url = vacancy.get('url')
        self.__salary_full = vacancy.get('salary')

        if self.__salary_full == 'По договоренности':
            self.__salary_min = 0
            self.__salary_max = 0
        else:
            self.__salary_min = vacancy.get('salary').rsplit(None, 3)[1]
            self.__salary_max = vacancy.get('salary').rsplit(None, 3)[3]

        self.salary = max(int(self.__salary_min), int(self.__salary_max))
        self.__experience = vacancy.get('experience')
        self.__requirement_and_responsibility = vacancy.get('requirement_and_responsibility')

    def __str__(self):
        return f"{self.__name} " \
               f"({self.__salary_full}, " \
               f"{self.__url}, " \
               f"{self.__experience}, " \
               f"{self.__requirement_and_responsibility})"

    def __dict__(self):
        vacancy_dict = {'name': self.__name,
                        'url': self.__url,
                        'salary': self.__salary_full,
                        'experience': self.__experience,
                        'requirement_and_responsibility': self.__requirement_and_responsibility}
        return vacancy_dict

    def __add__(self, other):
        """
        Суммирование подпищиков каналов
        :param other: количество подпищиков другого канала
        :return: общее количество подпищиков или ошибка
        """
        if type(other) == Vacancy:
            return self.salary + other.salary
        else:
            raise TypeError

    def __sub__(self, other):
        """
        Вычитание подпищиков каналов
        :param other: количество подпищиков другого канала
        :return: разница количества подпищиков или ошибка
        """
        if type(other) == Vacancy:
            return self.salary - other.salary
        else:
            raise TypeError

    def __lt__(self, other):
        """
        Если количество подпищиков первого канала меньше количества подпищиков второго
        :param other: количество подпищиков другого канала
        :return: True или False или ошибка
        """
        if type(other) == Vacancy:
            return self.salary < other.salary
        else:
            raise TypeError

    def __le__(self, other):
        """
        Если количество подпищиков первого канала меньше или равно количеству подпищиков второго
        :param other: количество подпищиков другого канала
        :return: True или False или ошибка
        """
        if type(other) == Vacancy:
            return self.salary <= other.salary
        else:
            raise TypeError

    def __gt__(self, other):
        """
        Если количество подпищиков первого канала больше количества подпищиков второго
        :param other: количество подпищиков другого канала
        :return: True или False или ошибка
        """
        if type(other) == Vacancy:
            return self.salary > other.salary
        else:
            raise TypeError

    def __ge__(self, other):
        """
        Если количество подпищиков первого канала больше или равно количеству подпищиков второго
        :param other: количество подпищиков другого канала
        :return: True или False или ошибка
        """
        if type(other) == Vacancy:
            return self.salary >= other.salary
        else:
            raise TypeError

    def name(self):
        return self.__name

    def url(self):
        return self.__url

    def salary_full(self):
        return self.__salary_full

    def experience(self):
        return self.__experience

    def requirement_and_responsibility(self):
        return self.__requirement_and_responsibility


class JobSeeker(ABC):
    """
    Абстрактный класс для работы с сайтами для поиска вакансий по API
    """

    def __init__(self, params):
        """
        Инициализация параметров поиска вакансий пользователя
        :param params: параметры поиска
        """
        self.params = params
        # Создание self-переменной для хранения id города или области из функции
        self.town_id = self.get_region_id()
        # Создание self-переменной для хранения полученных данных
        self.vacancy_data = self.get_vacancies()

    @abstractmethod
    def get_vacancies(self):
        """
        Абстрактный метод, который получает информацию через API сайта
        :return: Массив с вакансиями
        """
        pass

    @abstractmethod
    def get_region_id(self):
        """
        Абстракный метод для получения id региона поиска вакансий (у своего сайта все id разные)
        :return: id региона
        """
        pass

    @abstractmethod
    def vacancy_filtering(self):
        """
        Абстракный метод для фильтрации массива данных о вакансиях
        :return: Отфильтрованный и приведенный к общему шаблону массив с необходимой информацией об вакансиях
        """
        pass


class HeadHunterAPI(JobSeeker):
    """
    Дочерний класс для работы с API HeadHunter.ru
    """

    def get_region_id(self):
        """
        Метод для получения id региона
        :return: id региона
        """
        user_area_hh = self.params.get('area').lower()
        regions_dict = json.loads(requests.get('https://api.hh.ru/areas').content.decode())[0].get('areas')
        for region in regions_dict:
            for town in region.get('areas'):
                if user_area_hh == town.get('name').lower():
                    return town.get('id')
                elif user_area_hh == 'москва':
                    return '1'

    def get_vacancies(self):
        """
        Метод для получения информации об вакансиях с HH.ru
        :return: Массив с вакансиями
        """
        parametrs = {'text': self.params.get('text'), 'area': self.town_id, 'page': 0,
                     'per_page': self.params.get('per_page')}
        try:
            data = json.loads(requests.get('https://api.hh.ru/vacancies', parametrs).content.decode())['items']
            return data
        except KeyError:
            exit('Слишком большое число вакансий!')

    def vacancy_filtering(self):
        """
        Метод для фильтрации массива данных о вакансиях с hh.ru
        :return: Отфильтрованный и приведенный к общему шаблону массив с необходимой информацией об вакансиях
        """
        filtered_vacancies = []
        for vac in self.vacancy_data:
            name_vacancy = vac.get('name')
            url_vacancy = vac.get('alternate_url')
            if vac.get('salary') is None:
                salary_vacancy = 'По договоренности'
            else:
                if vac.get("salary").get("from") is None:
                    salary_vacancy = f'от {0} до {vac.get("salary").get("to")}'
                elif vac.get("salary").get("to") is None:
                    salary_vacancy = f'от {vac.get("salary").get("from")} до {0}'
                else:
                    salary_vacancy = f'от {vac.get("salary").get("from")} до {vac.get("salary").get("to")}'
            experience_vacancy = vac.get('experience').get('name')
            requirement = f"Требования: {vac.get('snippet').get('requirement')}\n" \
                          f"Обязаности: {vac.get('snippet').get('responsibility')}"
            requirement_and_responsibility = requirement.replace('\n', '').replace('<highlighttext>', '').replace(
                '</highlighttext>', '')
            filtered_vacancy = {'name': name_vacancy,
                                'url': url_vacancy,
                                'salary': salary_vacancy,
                                'experience': experience_vacancy,
                                'requirement_and_responsibility': requirement_and_responsibility}
            filtered_vacancies.append(filtered_vacancy)
        return filtered_vacancies


class SuperJobAPI(JobSeeker):
    """
    Класс для работы с API Super Job
    """

    def get_region_id(self):
        """
        Метод для получения id региона
        :return: id региона
        """
        user_area_sj = self.params.get('area').lower()
        regions_list = json.loads(requests.get('https://api.superjob.ru/2.0/towns/?all=1').content.decode()).get(
            'objects')
        for town in regions_list:
            if user_area_sj == town.get('title').lower():
                return town.get('id')

    def get_vacancies(self):
        """
        Метод для получения информации об вакансиях с Super Job
        :return: Массив с вакансиями
        """
        params['area'] = self.town_id
        parametrs = {'town': params.get('area'), 'catalogues': None, 'count': params.get('per_page'),
                     'keyword': params.get('text')}
        headers = {
            'X-Api-App-Id': 'v3.r.137811180.37c57501a5961531559fcd1e5a184b116afd2325.'
                            'fd437c755d2c9fbea649de57242247526224f0af'}
        data = (requests.get('https://api.superjob.ru/2.0/vacancies/', params=parametrs, headers=headers)).json()[
            'objects']
        return data

    def vacancy_filtering(self):
        """
        Метод для фильтрации массива данных о вакансиях с Super Job
        :return: Отфильтрованный и приведенный к общему шаблону массив с необходимой информацией об вакансиях
        """
        filtered_vacancies = []
        for vac in self.vacancy_data:
            name_vacancy = vac.get('profession')
            url_vacancy = vac.get('link')
            if int(vac.get('payment_from')) == 0:
                salary_vacancy = 'По договоренности'
            else:
                salary_vacancy = f'от {vac.get("payment_from")} до {vac.get("payment_to")}'
            experience_vacancy = vac.get('experience').get('title')
            requirement = vac.get('candidat')
            if requirement is None:
                requirement_and_responsibility = 'Нет'
            else:
                requirement_and_responsibility = requirement.replace('\n', '').replace('<highlighttext>', '').replace(
                    '</highlighttext>', '')
            filtered_vacancy = {'name': name_vacancy,
                                'url': url_vacancy,
                                'salary': salary_vacancy,
                                'experience': experience_vacancy,
                                'requirement_and_responsibility': requirement_and_responsibility}
            filtered_vacancies.append(filtered_vacancy)
        return filtered_vacancies


class JSONSaver:
    """
    Класс для сохранения и записи списка вакансий
    """
    # Пустой список для словарей вакансий
    json_vacancy_dict = []

    def __init__(self, vacancy):
        """
        Инициализация словарей вакансий
        :param vacancy: словарь с информацией по вакансии
        """
        self.vacancy = vacancy
        # Добавление словаря в список
        self.json_vacancy_dict.append(self.vacancy)

    def json_file(self):
        """
        Функция для записи списка в json-файл
        :return:
        """
        with open('json-vacancies.json', 'w', encoding='utf-8') as file:
            json.dump(self.json_vacancy_dict, file, ensure_ascii=False)


def user_interaction():
    """
    Функция для работы с пользователем
    :return: Параметры поиска вакансий
    """
    # Запрос ключевого слова поиска
    filter_word = input('Введите строку для поиска вакансий по названию:\n')
    # Запрос региона поиска
    user_area = input('Введите нужный вам регион: \n(По умолчанию Москва)\n')
    # Выставление региона по умолчанию
    if user_area == '':
        user_area = 'москва'
    # Запрос количества желаемых вакансий
    user_per_page = input('Введите желаемое число вакансий:\n(Не более 100)\n(По умолчанию 10)\n')
    # Выставление количества по умолчанию
    if user_per_page == '':
        user_per_page = 10
    # Создание экземпляра класса из параметров пользователя
    inquiry = Parameters(filter_word, user_area, 0, int(user_per_page))
    return inquiry


# Начало программы
# Сбор параметров поиска
inquiry = user_interaction()
# Перевод параметров в словарь
params = inquiry.get_params()

# Создание экземпляра класса для работы с API сайтов с вакансиями
hh_api = HeadHunterAPI(params)
superjob_api = SuperJobAPI(params)

# Получение вакансий с разных платформ
hh_vacancies = hh_api.vacancy_filtering()
superjob_vacancies = superjob_api.vacancy_filtering()

# Обьединение списков вакансий с разных платформ
vacancies_full_list = superjob_vacancies + hh_vacancies

# Создание экземпляров класса для работы с вакансиями
# Пустой словарь для экземпляров класса вакансий
names_vac = []
# Иттерация по всем собранным вакансиям
for i in range(len(vacancies_full_list)):
    # Создание и добавление переменных по количество найденных вакансий
    names_vac.append(f'vacancy{i}')
    # Создание экзкмпляров класса по количеству вакансий
    names_vac[i] = Vacancy(vacancies_full_list[i])

# Сортировка всех найденных экземпляров класса по зарплате ("По договоренности" в конце)
names_vac.sort(key=lambda x: x.salary, reverse=True)

# Иттерация по 'топ - N' экземпляров класса ваканций
for i in range(int(len(names_vac) / 2)):
    # Вывод 'топ - N' вакансий в консоль
    print(f'{i + 1}: {names_vac[i]}')
    # Инициализация __dict__-функции класса вакансии в класс для сохранения в json
    json_saver = JSONSaver(names_vac[i].__dict__())

# Запуск записи массива с информацией об вакансиях в json-файл
json_saver.json_file()
# Вывод пользователя по окончанию записи вакансий в файл
print('Данные сохранены в "json-vacancies.json"')
