# praktikum_new_diplom
MyFoodgram - Ваш помощник в кулинарии
MyFoodgram_workflow

Описание
MyFoodgram - это кулинарный сервис, где пользователи могут публиковать рецепты, подписываться на публикации других авторов и добавлять понравившиеся рецепты в список «Избранное». Сервис также предлагает функцию «Список покупок», которая поможет пользователям сгенерировать список продуктов для приготовления выбранных блюд.

-- -
### Технологии:
- Python
- Django Rest Framework
- Docker
- Nginx
- Postgres
-- -

## Настройка и запуск проекта

1. Установите [Docker](https://docs.docker.com/get-docker/) на вашем компьютере или сервере.
2. Клонируйте репозиторий и перейдите в корневую директорию проекта.
3. Создайте и заполните `.env` файл, используя следующий шаблон:

```.env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_secret_key
```

5. В терминали запустить **docker-compose**. Выполнить миграции, сборку статических файлов, заполнение базы исходными ингредиентами, создание супер пользователя:
```bash
docker-compose up -d --build
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py importcsv
docker-compose exec backend python manage.py createsuperuser
```
Доступ к админ-панели

```bash
Для доступа к админ-панели перейдите по адресу http://84.201.162.233:81/admin и используйте учетные данные суперпользователя.
```

Автор
Вilol A.
