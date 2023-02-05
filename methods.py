import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from datetime import date
from my_database import *

vk = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk)
URL = 'https://api.vk.com/method/'
offset = 0


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7)})


def user_info():
    url = f'{URL}account.getProfileInfo'
    params = {'access_token': user_token,
              'v': '5.131'}
    return requests.get(url, params=params).json()['response']


def user_age():
    if user_info()['bdate']:
        bdate = user_info()['bdate'].split('.')
        today = date.today()
        users_age = today.year - int(bdate[2]) - ((today.month, today.day) < (int(bdate[1]), int(bdate[0])))
        return users_age
    else:
        for events in longpoll.listen():
            if events.type == VkEventType.MESSAGE_NEW and events.to_me:
                write_msg(events.user_id, 'Введите Ваш возраст')
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        users_age = int(event.text)
                        print(f'[INFO] Задан возраст пользователя - {users_age}')
                        return users_age


def user_sex():
    users_sex = user_info()['sex']
    if users_sex == 0:
        print('[INFO] Пол пользователя не определён')
        for event in longpoll.listen():
            write_msg(event.user_id, 'Введите Ваш пол цифрой:'
                                     '1 - женский'
                                     '2 - мужской')
            for events in longpoll.listen():
                if events.type == VkEventType.MESSAGE_NEW and events.to_me:
                    users_sex = events.text
                    if users_sex == 1:
                        print(f'[INFO] Задан пол пользователя - женский')
                    elif users_sex == 2:
                        print(f'[INFO] Задан пол пользователя - мужской')
                    else:
                        write_msg(event.user_id, 'Ваш ответ не понятен')
                        print(f'[ERROR] Пол пользователя не задан/задан некорректно')
    return users_sex


def user_city():
    print("USER CITY START")
    url = f'{URL}users.get'
    params = {'access_token': user_token,
              'user_ids': user_info()['id'],
              'fields': 'city',
              'v': '5.131'}
    if 'city' in requests.get(url, params=params).json()['response']:
        users_city = requests.get(url, params=params).json()['response'][0]['city']
        print(f'[INFO] Определён город пользователя - {users_city}')
        print("USER CITY OVER TRUE")
        return users_city
    else:
        print("USER CITY OVER FALSE")
        users_city = input_user_city()
        return users_city


def input_user_city():
    print("INPUT USER CITY START")
    print('[INFO] Город пользователя не найден')
    for events in longpoll.listen():
        write_msg(events.user_id, 'Введите Ваш город')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                users_city = event.text.capitalize()
                if users_city.isalpha():
                    print(f'[INFO] Задан город пользователя - {users_city}')
                    print("INPUT USER CITY OVER TRUE")
                    return users_city
                else:
                    try:
                        print("INPUT USER CITY OVER FALSE")
                        input_user_city()
                    except TypeError:
                        print('[TypeError]: Ошибка получения названия города')
                        break


def get_user_city_id():
    print("GET USER CITY ID START")
    users_city = user_city()
    if users_city is not False:
        url = f'{URL}database.getCities'
        params = {'access_token': user_token,
                  'country_id': '1',
                  'q': users_city,
                  'count': 1,
                  'v': '5.131'}
        try:
            city_id = requests.get(url, params=params).json()['response']['items'][0]['id']
            print("GET USER CITY ID OVER TRY")
            return city_id
        except IndexError:
            print('[IndexError]: ошибка получения ID города пользователя. Город указан неверно')
            input_user_city()
            return False


def user_relations():
    user_relation = int(user_info()['relation'])
    if 0 < user_relation < 9:
        print(f'[INFO] Определено семейное положение пользователя')
        return user_relation
    else:
        print(f'[INFO] Семейное положение пользователя не определено')
        for event in longpoll.listen():
            print('USER RELATION CYCLE START')
            write_msg(event.user_id, f'Укажите цифрой Ваше семейное положение: \n'
                                     '1 - не женат/не замужем \n'
                                     '2 - есть друг/есть подруга \n'
                                     '3 - помолвлен/помолвлена \n'
                                     '4 - женат/замужем \n'
                                     '5 - всё сложно \n'
                                     '6 - в активном поиске \n'
                                     '7 - влюблён/влюблена \n'
                                     '8 - в гражданском браке \n')
            for events in longpoll.listen():
                if events.type == VkEventType.MESSAGE_NEW and events.to_me:
                    user_relation = events.text
                    if user_relation.isdigit() is True and 0 < int(user_relation) < 9:
                        print(f'[INFO] Задано семейное положение пользователя')
                        return str(user_relation)
                    else:
                        write_msg(event.user_id, 'Ваше сообщение не распознано')
                        user_relations()


def age_from():
    age_min = user_age() - 5
    print(f'[INFO] Определён возраст пользователя - {age_min+5}')
    if age_min < 18:
        age_min = 18
    return age_min


def age_to():
    return user_age() + 5


def sex_found_person():
    if user_sex() == 1:
        print('[INFO] Определён пол пользователя - женский')
        return 2
    elif user_sex() == 2:
        print('[INFO] Определён пол пользователя - мужской')
        return 1


def find_person(city_id, sex, status, min_age, max_age):
    url = f'{URL}users.search'
    params = {'access_token': user_token,
              'offset': 1,
              'count': count,
              'fields': 'is_closed, id, first_name, last_name',
              'city_id': city_id,
              'sex': sex,
              'status': status,
              'age_from': min_age,
              'age_to': max_age,
              'has_photo': 1,
              'v': '5.131'}
    people_data = []
    for i in range(count):
        response = requests.get(url, params=params).json()['response']['items'][i]
        if response['is_closed'] is False:
            person_id = response['id']
            person_link = f'https://vk.com/id{person_id}'
            person_name = response['first_name']
            person_surname = response['last_name']
            insert_users_data_to_users_table(person_id, person_name, person_surname)
            # see_table_users()
            if user_already_seen(person_id) is True:
                continue
            url_get_photos = f'{URL}photos.getAll'
            params_get_photos = {'access_token': user_token,
                                 'owner_id': person_id,
                                 'extended': 1,
                                 'count': 3,
                                 'v': '5.131'}
            photos = requests.get(url_get_photos, params=params_get_photos).json()['response']['items']
            photos_list = []
            for k in range(len(photos)):
                photos_list.append({'id': photos[k]['id'], 'likes': photos[k]['likes']['count']})
            sorted_photos_list = sorted(photos_list, key=lambda d: d['likes'], reverse=True)
            the_most_liked_photos_data = sorted_photos_list[0:3]
            photos_ids = []
            if len(the_most_liked_photos_data) >= 3:
                for k in range(len(the_most_liked_photos_data)):
                    photos_ids.append(the_most_liked_photos_data[k].get('id'))
                first_photo = f'photo{person_id}_{photos_ids[0]}'
                second_photo = f'photo{person_id}_{photos_ids[1]}'
                third_photo = f'photo{person_id}_{photos_ids[2]}'
                data = {'id': f'{person_id}',
                        'link': f'{person_link}',
                        'name': f'{person_name} {person_surname}',
                        'first_photo': f'{first_photo}',
                        'second_photo': f'{second_photo}',
                        'third_photo': f'{third_photo}'}
                people_data.append(data)
            else:
                continue
    return people_data


def send_people_cards(city_id, sex, status, min_age, max_age):
    i = 0
    people_data = find_person(city_id, sex, status, min_age, max_age)
    print(people_data)
    for events in longpoll.listen():
        if i < len(people_data):
            write_msg(events.user_id, f'{people_data[i]["link"]} {people_data[i]["name"]}')
            send_photos(people_data, i)
            insert_users_data_to_seen_users_table(people_data[i]['id'])
            # see_table_seen_users()
            write_msg(events.user_id, 'Нажмите "1", чтобы продолжить поиск\n'
                                      'Нажмите "0", чтобы прекратить поиск')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    if event.text == '1':
                        i += 1
                        break
                    elif event.text == '0':
                        write_msg(event.user_id, 'Поиск завершён')
                        print('[INFO] Работа бота завершена')
                        return
                    else:
                        write_msg(event.user_id, 'Некорректный ответ\n'
                                                 'Нажмите "1", чтобы продолжить поиск\n'
                                                 'Нажмите "0", чтобы прекратить поиск')
                        continue
        else:
            for event in longpoll.listen():
                write_msg(event.user_id, 'Поиск завершён')
                return


def send_photos(people_data, i):
    vk.method('messages.send',
              {'access_token': user_token,
               'user_id': user_info()['id'],
               'random_id': randrange(10 ** 7),
               'attachment': f'{people_data[i]["first_photo"]},'
                             f'{people_data[i]["second_photo"]},'
                             f'{people_data[i]["third_photo"]},',
               'v': '5.131'})


