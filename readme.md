# TeamFinder

TeamFinder - Django-приложение для поиска командных проектов и участников. В текущей версии реализован вариант 3 задания: необходимые навыки проектов и фильтрация проектов по навыкам.

## Что реализовано

- Кастомная модель пользователя с авторизацией по email, профилем, телефоном, GitHub-ссылкой и аватаром.
- Автогенерация аватара для нового пользователя, если изображение не загружено вручную.
- Создание, редактирование, просмотр проектов, участие в проектах и закрытие проекта владельцем.
- Блок "Необходимые навыки" на странице проекта.
- AJAX-добавление навыков владельцем проекта с подсказками и созданием нового навыка из интерфейса.
- AJAX-удаление навыков владельцем проекта.
- Фильтр списка проектов по навыкам через URL вида `?skill=<Название навыка>`.
- Пагинация списков проектов и участников.
- Демо-данные через management command `seed_demo`.
- Тесты основных пользовательских и проектных сценариев.
- Production-заготовка: `Dockerfile`, `docker-compose.production.yml`, `nginx.conf`, WhiteNoise, gunicorn.

## Локальный запуск

### 1. Перейти в папку проекта

```powershell
cd "C:\Users\artem\OneDrive\Рабочий стол\final_project\team-finder-ad"
```

### 2. Создать и активировать виртуальное окружение

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Если окружение уже создано, достаточно только активировать его.

### 3. Установить зависимости

```powershell
pip install -r requirements.txt
```

### 4. Создать `.env`

Скопируйте пример настроек:

```powershell
copy .env_example .env
```

Для локального запуска с Docker/PostgreSQL можно оставить значения из `.env_example`:

```env
DJANGO_SECRET_KEY=change_for_safety
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=
POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=team_finder
POSTGRES_HOST=localhost
POSTGRES_PORT=5436
USE_SQLITE=False
SQLITE_NAME=db.sqlite3
```


### 5. Запустить PostgreSQL в Docker

Docker Desktop должен быть запущен.

```powershell
docker compose up -d
```

Проверить контейнер:

```powershell
docker compose ps
```

Остановить контейнер при необходимости:

```powershell
docker compose down
```

### 6. Выполнить миграции

```powershell
python manage.py migrate
```

### 7. Создать демо-данные, если нужны

```powershell
python manage.py seed_demo
```

После этого будет доступен пользователь:

```text
email: maria@yandex.ru
password: password
```

### 8. Запустить Django

```powershell
python manage.py runserver
```

Открыть проект:

```text
http://127.0.0.1:8000/projects/list/
```


## Production

Для публичного деплоя в проекте подготовлены:

- `Dockerfile` - сборка backend на Python 3.11 slim, установка зависимостей и запуск через gunicorn.
- `docker-compose.production.yml` - сервисы `postgres`, `backend`, `nginx`, запуск `migrate`, `collectstatic`, затем `gunicorn`.
- `nginx.conf` - раздача `/static/` и `/media/`, проксирование остальных запросов в Django.
- Настройки из env: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, параметры PostgreSQL.
- GitHub Actions CI в `.github/workflows/tests.yml`.

Минимальный production-запуск:

```powershell
docker compose -f docker-compose.production.yml up -d --build
```

## Контакты

Github: https://github.com/atskih
Mail: artemvaluyskih1@gmail.com
