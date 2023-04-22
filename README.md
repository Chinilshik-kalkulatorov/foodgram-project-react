# praktikum_new_diplom
MyFoodgram - Ваш помощник в кулинарии
MyFoodgram_workflow

Описание
MyFoodgram - это кулинарный сервис, где пользователи могут публиковать рецепты, подписываться на публикации других авторов и добавлять понравившиеся рецепты в список «Избранное». Сервис также предлагает функцию «Список покупок», которая поможет пользователям сгенерировать список продуктов для приготовления выбранных блюд.

Технологии
Python
Django
Django Rest Framework
PostgreSQL
Gunicorn
Nginx
Docker
Настройка и запуск проекта
Установите Docker на вашем компьютере или сервере.
Клонируйте репозиторий и перейдите в корневую директорию проекта.
Создайте и заполните .env файл, используя следующий шаблон:
bash
Copy code
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_secret_key
Запустите Docker контейнеры, выполните миграции, сборку статических файлов и создание суперпользователя:
bash
Copy code
sudo docker-compose up -d
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py collectstatic --no-input
sudo docker-compose exec backend python manage.py createsuperuser
Загрузите ингредиенты и тестовые данные:
bash
Copy code
sudo docker-compose exec backend python manage.py load_data
Доступ к админ-панели
Для доступа к админ-панели перейдите по адресу http://84.201.162.233:81/admin и используйте учетные данные суперпользователя.

Автор
Вilol A.
