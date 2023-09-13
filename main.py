import requests
import json
from abc import ABC, abstractmethod


class Parameters:
    def __init__(self, text='', area='Москва', page=0, per_page=10):
        self.text = text
        self.area = area
        self.page = page
        self.per_page = per_page

    def get_params(self):
        return {
            'text': self.text,
            'area': self.area,
            'page': self.page,
            'per_page': self.per_page
        }


class Vacancy:
    def __init__(self, vacancy):
        self.__name = vacancy.get('name')
        self.__url = vacancy.get('url')
        self.__salary = vacancy.get('salary')
        self.__experience = vacancy.get('experience')
        self.__requirement_and_responsibility = vacancy.get('requirement_and_responsibility')

    def name(self):
        return self.__name

    def url(self):
        return self.__url

    def salary(self):
        return self.__salary

    def experience(self):
        return self.__experience

    def requirement_and_responsibility(self):
        return self.__requirement_and_responsibility


class JobSeeker(ABC):
    def __init__(self, params):
        self.params = params
        self.town_id = self.get_region_id()
        self.vacancy_data = self.get_vacancies()

    @abstractmethod
    def get_vacancies(self):
        pass

    @abstractmethod
    def get_region_id(self):
        pass

    @abstractmethod
    def vacancy_filtering(self):
        pass


class HeadHunterAPI(JobSeeker):

    def get_region_id(self):
        user_area = params.get('area')
        regions_dict = json.loads(requests.get('https://api.hh.ru/areas').content.decode())[0].get('areas')
        for region in regions_dict:
            for town in region.get('areas'):
                if user_area == town.get('name'):
                    return town.get('id')
                elif user_area == 'Москва':
                    return '1'

    def get_vacancies(self):
        params['area'] = self.town_id
        data = json.loads(requests.get('https://api.hh.ru/vacancies', params).content.decode())['items']
        return data

    def vacancy_filtering(self):
        filtered_vacancies = []
        for vac in self.vacancy_data:
            name_vacancy = vac.get('name')
            url_vacancy = vac.get('apply_alternate_url')
            if vac.get('salary') is None:
                salary_vacancy = 'По договоренности'
            else:
                salary_vacancy = f'от {vac.get("salary").get("from")} до {vac.get("salary").get("to")}'
            experience_vacancy = vac.get('experience').get('name')
            requirement = f"Требования: {vac.get('snippet').get('requirement')}\nОбязаности: {vac.get('snippet').get('responsibility')}"
            requirement_and_responsibility = requirement.replace('\n', '')
            filtered_vacancy = {'name': name_vacancy,
                                'url': url_vacancy,
                                'salary': salary_vacancy,
                                'experience': experience_vacancy,
                                'requirement_and_responsibility': requirement_and_responsibility}
            filtered_vacancies.append(filtered_vacancy)
        return filtered_vacancies


class SuperJobAPI(JobSeeker):

    def get_region_id(self):
        user_area = params.get('area')
        regions_list = json.loads(requests.get('https://api.superjob.ru/2.0/towns/?all=1').content.decode()).get(
            'objects')
        for town in regions_list:
            if user_area == town.get('title'):
                return town.get('id')

    def get_vacancies(self):
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
            requirement_and_responsibility = requirement.replace('\n', '')
            filtered_vacancy = {'name': name_vacancy,
                                'url': url_vacancy,
                                'salary': salary_vacancy,
                                'requirements': experience_vacancy,
                                'requirement_and_responsibility': requirement_and_responsibility}
            filtered_vacancies.append(filtered_vacancy)
        return filtered_vacancies


class JSONSaver:
    def __init__(self):
        pass

    def add_vacancy(self, vacancy):
        pass

    def get_vacancies_by_salary(self, salary):
        pass

    def delete_vacancy(self, vacancy):
        pass


def user_interaction():
    filter_word = input('Введите строку для поиска вакансий по названию\n')
    user_area = input('Введите нужный вам регион \n(По умолчанию Москва)\n')
    if user_area == '':
        user_area = 'Москва'
    user_per_page = input('Введите желаемое число вакансий\n(По умолчанию 10)\n')
    if user_per_page == '':
        user_per_page = 10
    inquiry = Parameters(filter_word, user_area, 0, int(user_per_page))
    return inquiry


inquiry = user_interaction()
params = inquiry.get_params()

# Создание экземпляра класса для работы с API сайтов с вакансиями
hh_api = HeadHunterAPI(params)
superjob_api = SuperJobAPI(params)

# Получение вакансий с разных платформ
hh_vacancies = hh_api.vacancy_filtering()
superjob_vacancies = superjob_api.vacancy_filtering()

# Обьединение списков вакансий с разных платформ
vacancies_full_list = hh_vacancies + superjob_vacancies

#print(vacancies_full_list)

# Создание экземпляра класса для работы с вакансиями
names_vac = []
for i in range(len(vacancies_full_list)):
    names_vac.append(f'vacancy{i}')
    names_vac[i] = Vacancy(vacancies_full_list[i])


print(names_vac[0].__dict__)
print(names_vac[1].__dict__)
print(names_vac[2].__dict__)
print(names_vac[3].__dict__)
print(names_vac[4].__dict__)
print(names_vac[5].__dict__)
print(names_vac[6].__dict__)

# Сохранение информации о вакансиях в файл
# json_saver = JSONSaver()
# json_saver.add_vacancy(vacancy)
# json_saver.get_vacancies_by_salary("100 000-150 000 руб.")
# json_saver.delete_vacancy(vacancy)
