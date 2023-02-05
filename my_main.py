from methods import *

vk = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk)
URL = 'https://api.vk.com/method/'

# delete_seen_users_table()
delete_users_table()
create_users_table()
create_seen_users_table()

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()

        if request == 'привет':
            write_msg(event.user_id, f"Здравствуйте, {user_info()['first_name']}!")
            city_id = get_user_city_id()
            sex = sex_found_person()
            status = user_relations()
            min_age = age_from()
            max_age = age_to()
            find_person(city_id, sex, status, min_age, max_age)
            send_people_cards(city_id, sex, status, min_age, max_age)
        elif request == "пока":
            write_msg(event.user_id, "Буду ждать Вас снова!")
            print('[INFO] Работа бота завершена')

conn.close()
