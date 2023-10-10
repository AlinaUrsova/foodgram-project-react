# Продуктовый помощник FOODGRAM
### Описание:
«Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Проект состоит из следующих страниц: 
- главная,
- страница рецепта,
- страница пользователя,
- страница подписок,
- избранное,
- список покупок,
- создание и редактирование рецепта.

### Используемые технологии:
Python, Django, Django Rest Framework, Docker, PostgreSQL

### Как запустить проект:
#### API Foodgram локально:
1. Клонировать репозиторий и перейти в него в командной строке:
```
git@github.com:AlinaUrsova/foodgram-project-react.git
```
2. Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```
```
source venv/Scripts/activate
```
3. Установоить зависимости:
```
pip install -r requirements.txt
```
4. Перейти в дерикторию `foodgram/settings.py` заменить настройки базы данных на SQLite:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```
5. Перейти в дерикторию `backend` выполнить миграции и создать супер пользователя:
```
cd backend
```
```
python manage.py makemigrations
```
```
python manage.py migrate
```
```
python manage.py createsuperuser
```
6. Запустить сервер разработки:
```
python manage.py runserver
```
7. Наполнить базу данных ингредиентами через администратора, через кнопку 'import'

#### Запуск проекта на сервере:
1. Собрать образы:
```
docker build -t username/foodgram_frontend .
docker build -t username/foodgram_backend .
docker build -t username/foodgram_gateway . 
```
2. Загрузить образы на Docker Hub:
```
docker push username/foodgram_frontend
docker push username/foodgram_backend
docker push username/foodgram_gateway  
```
3. Загрузить образы на Docker Hub:
```
docker push username/foodgram_frontend
docker push username/foodgram_backend
docker push username/foodgram_gateway  
```
4. Поочерёдно выполните на сервере команды для установки Docker и Docker Compose на удаленном сервере:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin 
```
5. Скопируйте на сервер в директорию foodgram/ файл docker-compose.production.yml

6. Скопируйте на сервер в директорию foodgram/ файл .env

7. Запустите Docker Compose в режиме демона:
```
sudo docker compose -f docker-compose.production.yml up -d 
```
8. Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /backend_static/static/:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

**Проект будет досупен по адресу:**  
https://foodgramalina.hopto.org/

**Данные для администратора:**
Логин: admin
Email: a@a.ru  
Password: 123

### Автор:
Урсова Алина