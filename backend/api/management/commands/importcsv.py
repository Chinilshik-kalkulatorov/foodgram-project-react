import csv
import sqlite3

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Импорт в базу тестовых данных из файлов'

    def handle(self, *args, **options):
        path = "static/data"
        config_files = {
            'category': {
                'tb_name': 'reviews_category',
                'fields': ['id', 'name', 'slug']
            },
            'genre': {
                'tb_name': 'reviews_genre',
                'fields': ['id', 'name', 'slug']
            },
            'titles': {
                'tb_name': 'reviews_title',
                'fields': ['id', 'name', 'year', 'category_id']
            },
            'genre_title': {
                'tb_name': 'reviews_genretitle',
                'fields': ['id', 'title_id', 'genre_id']
            },
            'review': {
                'tb_name': 'reviews_review',
                'fields': ['id', 'title_id', 'text',
                           'author_id', 'score', 'pub_date']
            },
            'comments': {
                'tb_name': 'reviews_comment',
                'fields': ['id', 'review_id', 'text', 'author_id', 'pub_date']
            },
            'users': {
                'tb_name': 'users_user',
                'fields': ['id', 'username', 'email', 'role', 'bio',
                           'first_name', 'last_name']
            },
        }
        add_fields = {
            'password': '',
            'is_superuser': '0',
            'is_staff': '0',
            'is_active': '1',
            'date_joined': '',
            'confirmation_code': ''
        }
        sql_query_form = 'INSERT INTO {} ({}) VALUES ({});'

        sqlite_connection = sqlite3.connect('db.sqlite3')
        cursor = sqlite_connection.cursor()
        for file in config_files:
            with open(f'{path}/{file}.csv', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row_data = []
                    for value in row.values():
                        row_data.append(value)
                    table_name = config_files[file]['tb_name']
                    columns_list = config_files[file]['fields'].copy()
                    if table_name == 'users_user':
                        for key, value in add_fields.items():
                            columns_list.append(key)
                            row_data.append(value)

                    columns = ', '.join(columns_list)
                    values = ', '.join(['?' for i in columns_list])
                    sql_query = (
                        sql_query_form.format(
                            table_name,
                            columns,
                            values
                        )
                    )
                    try:
                        cursor.execute(
                            sql_query,
                            tuple(row_data)
                        )
                    except Exception as error:
                        self.stdout.write(
                            f'Ошибка в строке файла {file}: {row_data}\n'
                            f'Запрос: {sql_query}\n'
                            f'Исключение: {error}'
                        )
            self.stdout.write(f'Файл {file}.csv импортирован!')
        sqlite_connection.commit()
        cursor.close()
