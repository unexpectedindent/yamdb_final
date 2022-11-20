# Проект YaMDb
![yamdb_workflow.yml](https://github.com/unexpectedindent/yamdb_final/actions/workflows/yamdb_workflow/badge.svg)

* [Описание проекта](#Описание-проекта)
* [Технологии](#Используемые-технологии)
* [Запуск](#Запуск-проекта)
* [Функциональность](#Функциональность)
  * [Пользовательские роли](#Пользовательские-роли)
  * [Ресурсы](#Ресурсы)
  * [Регистрация и авторизация](#Регистрация-и-авторизация)
  * [Документация](Полная-документация-к-API)


### Описание проекта

Проект YaMDb собирает отзывы пользователей на произведения. Произведения делятся на категории, например, «Книги», «Фильмы», «Музыка». Список категорий может быть меняться администратором.
Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
В каждой категории есть произведения. Например, в категории «Книги» могут быть произведения «Винни-Пух и все-все-все» и «Марсианские хроники», а в категории «Музыка» — песня «Давеча» группы «Насекомые» и вторая сюита Баха.
Произведению может быть присвоен жанр из списка предустановленных. Новые жанры может создавать только администратор.
Пользователи могут оставлять к произведениям текстовые отзывы и ставить произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — рейтинг (целое число). На одно произведение пользователь может оставить только один отзыв.


### Используемые технологии

* python
* django
* drf
* jwt
* nginx
* gunicorn
* docker

### Запуск проекта

1. Скопируйте репозитарий на свой компьютер:
```bash
git clone https://github.com/unexpectedindent/yamdb_final.git
```
2. Подготовьте сервер - скопируйте со своей локальной машины файл docker-compose.yaml и директорию nginx. Для этого в терминале выполните команду:
```bash
scp infra/docker-compose.yaml <username on server>@<IP-address of your server>:/<directory on the server> && scp -r infra/nginx <username on server>@<IP-address of your server>:/<directory on the server>
```
3. Создайте в удаленном репозитарии на github переменные окружения: <Your repository> -> Settings -> Secrets -> Actions: New repository secret:
* `DOCKER_USERNAME` - Ваш логин на hub.docker.com
* `DOCKER_PASSWORD` - Ваш пароль на hub.docker.com
* `DOCKER_REPOS` - имя репозитария на hub.docker.com
* `HOST` - ip-адрес вашего сервера
* `USER` - имя пользователя на сервере
* `SSH_KEY` - приватный ssh-ключ (`cat ~/.ssh/id_rsa` начиная с `-----BEGIN OPENSSH PRIVATE KEY-----` до `-----END OPENSSH PRIVATE KEY-----`)
* `PASSPHRASE` - пароль, защищающий ssh-ключ

А также переменные, которые будут скопированы в `.env`
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password (задайте свой пароль)
DB_HOST=db
DB_PORT=5432
SECRET_KEY=secretkey (задайте свой ключ)
```

4. Запуск проекта на удаленном сервере:
4.1. Установите соединение с сервером
```bash
ssh <USER>@<HOST>
```
4.2. Запустите контейнеры:
```bash
sudo docker-compose up -d
```
4.3. Выполните настройки внутри контейнера `web`:
```bash
sudo docker-compose exec web python manage.py migrate
sudo docker-compose -p api_yamdb exec web python manage.py createsuperuser
sudo docker-compose exec web python manage.py collectstatic --no-input
```

## Функциональность

### Пользовательские роли

1. Пользователь: может просматривать списки категорий, жанров, а также изучать информацию о произведениях. Также может писать отзывы на произведения и комментарии к отзывам. Может редактировать и/или удалять собственные отзывы и комментарии.
2. Модератор: обладает теми же правами, что и пользователь, но дополнительно имеет права на изменение и/или удаление отзывов и комментариев любых других пользователей.
3. Администратор: в дополнение к правам модератора может добавлять/удалять категории и жанры, добавлять/удалять произведения, регистрировать и удалять новых пользователей, менять роли пользователям.


### Ресурсы

1. Ресурс auth (auth/): аутентификация.
2. Ресурс users (users/): пользователи.
3. Ресурс categories (categories/): категории (типы) произведений («Фильмы», «Книги», «Музыка»).
4. Ресурс genres (genres/): жанры произведений. Одно произведение может быть привязано к нескольким жанрам.
5. Ресурс titles (titles/): произведения, к которым пишут отзывы (определённый фильм, книга или песенка).
6. Ресурс reviews (titles/[id]/reviews/): отзывы на произведения. Отзыв привязан к определённому произведению.
7. Ресурс comments (titles/[id]/reviews/[id]/comments/): комментарии к отзывам. Комментарий привязан к определённому отзыву.


### Регистрация и авторизация

1. Пользователь отправляет POST-запрос с параметрами "email" и "username" на эндпоинт /api/v1/auth/signup/.
2. Сервис YaMDB отправляет письмо с кодом подтверждения (confirmation_code) на указанный адрес email.
3. Пользователь отправляет POST-запрос с параметрами username и confirmation_code на эндпоинт /api/v1/auth/token/, в ответе на запрос ему приходит token (JWT-токен).


### Полная документация к API

`<Your host>/ReDoc/`