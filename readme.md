# TeamFinder

Реализован backend Django для варианта 3 задания: необходимые навыки проектов и фильтрация проектов по навыкам.

## Проверка реализации

1. Убедитесь, что в `.env` указано `TASK_VERSION=3`.
2. Запустите PostgreSQL:
   ```bash
   docker compose up -d
   ```
3. Выполните миграции:
   ```bash
   python manage.py migrate
   ```
4. При необходимости создайте тестовые данные:
   ```bash
   python manage.py seed_demo
   ```
   Будет создан тестовый пользователь `maria@yandex.ru` с паролем `password`.
5. Запустите сервер:
   ```bash
   python manage.py runserver
   ```

## Что реализовано

* Кастомная модель пользователя с входом по email и автогенерацией аватара.
* Модель проектов с автором, участниками, статусом, ссылкой на GitHub.
* Регистрация, вход, выход, профиль, редактирование профиля и смена пароля.
* Создание, редактирование, просмотр проектов, участие и завершение проекта.
* Вариант 3: необходимые навыки проектов, AJAX-добавление/удаление навыков и фильтр проектов по навыкам.
* Автоматические тесты основных пользовательских и проектных сценариев.

## Подготовка к публичному деплою

Для публичного деплоя в проекте подготовлено:

* Есть `Dockerfile`: backend собирается на `python:3.11-slim`, ставит зависимости и запускает Django через `gunicorn`.
* Есть `docker-compose.production.yml`: поднимает `postgres`, `backend` и `nginx`; backend запускает `migrate`, `collectstatic`, затем `gunicorn`.
* Есть `nginx.conf`: nginx слушает `80:80`, отдаёт `/static/` и `/media/`, остальные запросы проксирует в Django.
* В `settings.py` настройки вынесены в env: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, параметры PostgreSQL.
* Есть GitHub Actions CI в `.github/workflows/tests.yml`: тесты на Python 3.10/3.11/3.12, `ruff`, проверка миграций, затем сборка Docker-образа. Push в Docker Hub выполняется при наличии секретов `DOCKERHUB_USERNAME` и `DOCKERHUB_TOKEN`.

Минимальные production-переменные:

```env
DJANGO_SECRET_KEY=change_for_real_secret
DJANGO_DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
TASK_VERSION=3
POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=change_for_real_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Запуск production-сборки:

```bash
docker compose -f docker-compose.production.yml up -d --build
```

# Первоначальная настройка проекта TeamFinder

## 1. Виртуальное окружение

Перед началом работы необходимо создать и активировать виртуальное окружение Python.  


1. **Создайте виртуальное окружение (в папке проекта):**
   ```bash
   python3 -m venv venv
   ```

   После этого появится папка `venv`, где будут храниться зависимости проекта.

2. **Активируйте окружение:**

    - **Windows (PowerShell):**
      ```bash
      venv\Scripts\Activate.ps1
      ```
    - **Windows (cmd):**
      ```bash
      venv\Scripts\activate
      ```
    - **Linux/Mac:**
      ```bash
      source venv/bin/activate
      ```

3. **Установите зависимости из `requirements.txt`:**
   ```bash
   pip install -r requirements.txt
   ```

   После установки в окружении будут доступны все нужные библиотеки Django-проекта.

## 2. Создание `.env`

Файл `.env` содержит конфиденциальные настройки проекта — ключ Django, параметры БД и другие переменные.  

Особое внимание обратите на строчку `TASK_VERSION=`. 
Добавьте число, которое соответствует вашему варианту задания. 
Этот параметр определяет, какие шаблоны использовать для сайта (из папок `templates_var1`/`templates_var2`/`templates_var3`).
Лишние две папки не из вашего варианта можно удалить.

В репозитории есть пример `.env_example`, который нужно скопировать и заполнить:

```bash
cp .env_example .env
```

После этого откройте `.env` и укажите свои значения.  

| Переменная            | Назначение                                                                                                                                                 |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DJANGO_SECRET_KEY** | Секретный ключ Django, используемый для подписи cookie и токенов. Можно сгенерировать при помощи `get_random_secret_key` из `django.core.management.utils` |
| **DJANGO_DEBUG**      | Режим отладки. Установите `True` во время разработки.                                                                                                      |
| **POSTGRES_DB**       | Имя базы данных PostgreSQL, которую будет использовать Django.                                                                                             |
| **POSTGRES_USER**     | Имя пользователя PostgreSQL.                                                                                                                               |
| **POSTGRES_PASSWORD** | Пароль пользователя PostgreSQL.                                                                                                                            |
| **POSTGRES_HOST**     | Адрес сервера БД. В случае локальной разработки localhost.                                                                                                 |
| **POSTGRES_PORT**     | Порт подключения к БД (по умолчанию `5432`).                                                                                                               |
| **TASK_VERSION**      | Номер варианта вашего задания. Используется для определения набора HTML-шаблонов.                                                                          |

---

## 3. Запуск PostgreSQL

Для работы приложения **TeamFinder** используется база данных **PostgreSQL**.
По условию задания база данных должна запускаться в контейнере Docker.

В проекте уже есть пример файла `docker-compose.yml`. 
Используйте готовый или измените под свои нужды, а дальше запускайте:

```bash
docker compose up -d
```

`-d` значит `detach`, то есть контейнер продолжит работать в фоне. Чтобы его остановить, надо будет ввести

```bash
docker compose down
```

Если возникает ошибка "permission denied while trying to connect to the Docker daemon socket", то может потребоваться добавить `sudo` перед командой.

---

После этого база данных будет доступна по адресу `localhost:5432`.  
Нужно будет использовать эти же параметры в файле `.env`.

> Если на компьютере уже развёрнут сервер БД на порте 5432, и вы не хотите создавать БД для этого проекта на этом сервере, целесообразнее будет изменить порт на нестандартный.
> Нестандартный порт нужно будет поставить слева в паре портов в docker-compose (`"5433":"5432"`) и в .env.

## 4. Запуск Django

После заполнения `.env` и настройки базы данных можно запустить сервер разработки:

```bash
python manage.py runserver
```

Теперь проект доступен по адресу [http://localhost:8000](http://localhost:8000).
