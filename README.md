# yamdb_final ![YaMDb Status](https://github.com/rume73/yamdb_final/actions/workflows/yamdb_workflow.yaml/badge.svg)

## REST API for YaMDb service - site of reviews about films, books and music.

# Проект YaMDb

Проект YaMDb собирает отзывы (Review) пользователей на произведения (Title). Произведения делятся на категории: «Книги», «Фильмы», «Музыка». Список категорий (Category) может быть расширен (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»).

Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.

В каждой категории есть произведения: книги, фильмы или музыка. Например, в категории «Книги» могут быть произведения «Винни Пух и все-все-все» и «Марсианские хроники», а в категории «Музыка» — песня «Давеча» группы «Насекомые» и вторая сюита Баха. Произведению может быть присвоен жанр из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»). Новые жанры может создавать только администратор.

Благодарные или возмущённые читатели оставляют к произведениям текстовые отзывы (Review) и выставляют произведению рейтинг (оценку в диапазоне от одного до десяти). Из множества оценок автоматически высчитывается средняя оценка произведения.

### Установка на локальном компьютере

Эти инструкции помогут вам создать копию проекта и запустить ее на локальном компьютере для целей разработки и тестирования.

### Установка Docker

Установите Docker, используя инструкции с официального сайта:

- для Windows и MacOS
- для Linux. Отдельно потребуется установть Docker Compose

Запуск проекта (на примере Linux)

- Создайте на своем компютере папку проекта YamDb `mkdir yamdb` и перейдите в нее `cd yamdb`
- Склонируйте этот репозиторий в текущую папку git clone `https://github.com/rume73/yamdb_final/` .
- Создайте файл .env командой `touch .env` и добавьте в него переменные окружения для работы с базой данных:

```
    DB_NAME=postgres # имя базы данных
    POSTGRES_USER=postgres # логин для подключения к базе данных
    POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
    DB_HOST=db # название сервиса (контейнера)
    DB_PORT=5432 # порт для подключения к БД
```

- Запустите docker-compose командой `docker-compose up`
- Накатите миграции `docker-compose exec yamdb python manage.py migrate`
- Соберите статику командой `sudo docker-compose exec yamdb python manage.py collectstatic --no-input`
- Создайте суперпользователя Django `docker-compose exec yamdb python manage.py createsuperuser --username admin --email 'admin@yamdb.com'`
- Загрузите данные в базу данных при необходимости `docker-compose exec web python manage.py loaddata fixtures.json`

## Установка на удалённом сервере

Необходимо добавить Action secrets в репозитории на GitHub в разделе settings -> Secrets:
* DOCKER_PASSWORD - пароль от DockerHub;
* DOCKER_USERNAME - имя пользователя на DockerHub;
* HOST - ip-адрес сервера;
* SSH_KEY - приватный ssh ключ (публичный должен быть на сервере);
* TELEGRAM_TO - id своего телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
* TELEGRAM_TOKEN - токен бота (получить токен можно у @BotFather, /token, имя бота)

### Проверка работоспособности

Теперь если внести любые изменения в проект и выполнить:
```
git add .
git commit -m "..."
git push
```
Комманда git push является триггером workflow проекта.
При выполнении команды git push запустится набор блоков комманд jobs (см. файл yamdb_workflow.yaml).
Последовательно будут выполнены следующие блоки:
* tests - тестирование проекта на соответствие PEP8 и тестам pytest.
* build_and_push_to_docker_hub - при успешном прохождении тестов собирается образ (image) для docker контейнера 
и отправлятеся в DockerHub
* deploy - после отправки образа на DockerHub начинается деплой проекта на сервере.
Происходит копирование следующих файлов с репозитория на сервер:
  - docker-compose.yaml, необходимый для сборки трех контейнеров:
    + postgres - контейнер базы данных
    + web - контейнер Django приложения + wsgi-сервер gunicorn
    + nginx - веб-сервер
  - nginx/default.conf - файл кофигурации nginx сервера
  - static - папка со статическими файлами проекта
  
  После копировния происходит установка docker и docker-compose на сервере
  и начинается сборка и запуск контейнеров.
* send_message - после сборки и запуска контейнеров происходит отправка сообщения в 
  телеграм об успешном окончании workflow

После выполнения вышеуказанных процедур необходимо установить соединение с сервером:
```
ssh username@server_address
```
Отобразить список работающих контейнеров:
```
sudo docker container ls
```
В списке контейнеров копировать CONTAINER ID контейнера username/yamdb_final_web:latest (username - имя пользователя на DockerHub):
```
CONTAINER ID   IMAGE                            COMMAND                  CREATED          STATUS          PORTS                NAMES
0361a982109d   nginx:1.19.6                     "/docker-entrypoint.…"   50 minutes ago   Up 50 minutes   0.0.0.0:80->80/tcp   yamdb_final_nginx_1
a47ce31d4b7b   username/yamdb_final_web:latest  "/bin/sh -c 'gunicor…"   50 minutes ago   Up 50 minutes                        yamdb_final_web_1
aed19f6751f3   postgres:13.1                    "docker-entrypoint.s…"   50 minutes ago   Up 50 minutes   5432/tcp             yamdb_final_postgres_1
```
Выполнить вход в контейнер:
```
sudo docker exec -it a47ce31d4b7b bash
```
Внутри контейнера выполнить миграции:
```
python manage.py migrate
```
Также можно наполнить базу данных начальными тестовыми данными:
```
python3 manage.py shell
>>> from django.contrib.contenttypes.models import ContentType
>>> ContentType.objects.all().delete()
>>> quit()
python manage.py loaddata fixtures.json
```
Теперь проекту доступна статика. В админке Django (http://<server_address>/admin)
доступно управление данными. Если загрузить фикструры, то будет доступен superuser:
* email: admin5@admin5
* password: admin512345

Для создания нового суперпользователя можно выполнить команду:
```
$ python manage.py createsuperuser
```
и далее указать: 
```
Email:
Username:
Password:
Password (again):
```

## Техническое описание проекта YaMDb

Вам доступен репозиторий yamdb_final. К проекту по адресу /redoc подключена документация API YaMDb. В ней описаны шаблоны запросов к API и структура ожидаемых ответов. Для каждого запроса указаны уровни прав доступа: пользовательские роли, которым разрешён запрос.

*запросы к API начинаются с `/api/v1/`*

### Пользовательские роли

* **Аноним** — может просматривать описания произведений, читать отзывы и комментарии.
* **Аутентифицированный пользователь (user)**— может читать всё, как и Аноним, дополнительно может публиковать отзывы и ставить рейтинг произведениям (фильмам/книгам/песенкам), может комментировать чужие отзывы и ставить им оценки; может редактировать и удалять свои отзывы и комментарии.
* **Модератор (moderator)** — те же права, что и у Аутентифицированного пользователя плюс право удалять любые отзывы и комментарии.
* **Администратор (admin)** — полные права на управление проектом и всем его содержимым. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.
* **Администратор Django** — те же права, что и у роли Администратор.
    
### Алгоритм регистрации пользователей

1. Пользователь отправляет POST-запрос с параметром email на /api/v1/auth/email/.
2. YaMDB отправляет письмо с кодом подтверждения (confirmation_code) на адрес email .
3. Пользователь отправляет POST-запрос с параметрами email и confirmation_code на /api/v1/auth/token/, в ответе на запрос ему приходит token (JWT-токен).

Эти операции выполняются один раз, при регистрации пользователя. В результате пользователь получает токен и может работать с API, отправляя этот токен с каждым запросом.

После регистрации и получения токена пользователь может отправить PATCH-запрос на /api/v1/users/me/ и заполнить поля в своём профайле (описание полей — в документации).
Если пользователя создаёт администратор (например, через POST-запрос api/v1/users/...) — письмо с кодом отправлять не нужно. 

### Ресурсы API YaMDb

* Ресурс AUTH: аутентификация.
* Ресурс USERS: пользователи.
* Ресурс TITLES: произведения, к которым пишут отзывы (определённый фильм, книга или песенка).
* Ресурс CATEGORIES: категории (типы) произведений («Фильмы», «Книги», «Музыка»).
* Ресурс GENRES: жанры произведений. Одно произведение может быть привязано к нескольким жанрам.
* Ресурс REVIEWS: отзывы на произведения. Отзыв привязан к определённому произведению.
* Ресурс COMMENTS: комментарии к отзывам. Комментарий привязан к определённому отзыву.

Каждый ресурс описан в документации: указаны эндпойнты (адреса, по которым можно сделать запрос), разрешённые типы запросов, права доступа и дополнительные параметры, если это необходимо.

### Связанные данные и каскадное удаление

При удалении объекта пользователя User удаляться все отзывы и комментарии этого пользователя (вместе с оценками-рейтингами).  
При удалении объекта произведения Title удаляться все отзывы к этому произведению и комментарии к ним.  
При удалении объекта категории Category не удаляться связанные с этой категорией произведения (Title).  
При удалении объекта жанра Genre не удаляться связанные с этим жанром произведения (Title).  
При удалении объекта отзыва Review будут удалены все комментарии к этому отзыву.

## В разработке использованы

* [Python](https://www.python.org/)
* [Django](https://www.djangoproject.com/)
* [Django REST framework](https://www.django-rest-framework.org/)
* [DRF Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
* [PostgreSQL](https://www.postgresql.org/)
* [Docker](https://www.docker.com/)
* [Gunicorn](https://gunicorn.org/)
* [Nginx](https://nginx.org/)

## Авторы

* **Vladimir Loginov** - [rume73](https://github.com/rume73)
* **Olga Strizh** - [arswift ](https://github.com/arswift)
* **Ruslan Gamidov** - [Luchesse](https://github.com/Luchesse)

## Ссылки

Проект доступен по следующей ссылке <http://62.84.114.196/api/v1/>  
Подробная документация по API размещена по адресу <http://62.84.114.196/redoc/>
