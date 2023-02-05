import psycopg2
from my_config import *
from pprint import pprint

conn = psycopg2.connect(database='vkinderdb', user=user_db, password=password_db)


def create_users_table():
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id serial PRIMARY KEY,
            vk varchar(50) NOT NULL,
            vk_name varchar(50) NOT NULL,
            vk_surname varchar(50) NOT NULL);""")
    print('[INFO_DB] Создана таблица пользователей')
    conn.commit()


def insert_users_data_to_users_table(vk_id, name, surname):
    with conn.cursor() as cur:
        cur.execute(f"""
            INSERT INTO users (vk, vk_name, vk_surname) 
            VALUES ('{vk_id}', '{name}', '{surname}');""")
    print('[INFO_DB] В таблицу USERS добавлены данные')
    conn.commit()


# def see_table_users():
#     with conn.cursor() as cur:
#         cur.execute("""
#             SELECT * FROM users;""")
#         pprint(cur.fetchall())

# def see_table_seen_users():
#     with conn.cursor() as cur:
#         cur.execute("""
#             SELECT * FROM seen_users;""")
#         pprint(cur.fetchall())


def create_seen_users_table():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS seen_users(
                id serial PRIMARY KEY,
                vk varchar(50) NOT NULL);""")
    print('[INFO_DB] Создана таблица просмотренных пользователей')
    conn.commit()


def insert_users_data_to_seen_users_table(vk_id):
    with conn.cursor() as cur:
        cur.execute(f"""
            INSERT INTO seen_users (vk) 
            VALUES ('{vk_id}');""")
    print('[INFO_DB] В таблицу SEEN_USERS добавлены данные')
    conn.commit()


def delete_users_table():
    with conn.cursor() as cur:
        cur.execute("""
        DROP TABLE IF EXISTS users CASCADE;""")
    print('[INFO_DB] Таблица USERS была удалена')
    conn.commit()


def delete_seen_users_table():
    with conn.cursor() as cur:
        cur.execute("""
        DROP TABLE IF EXISTS seen_users CASCADE;""")
    print('[INFO_DB] Таблица SEEN_USERS была удалена')
    conn.commit()


def user_already_seen(vk_id):
    with conn.cursor() as cur:
        cur.execute(f"""
        SELECT vk FROM seen_users WHERE vk = '{vk_id}';""")
        return cur.fetchone() is not None
