# ShopByKv

Онлайн-магазин комплектующих для ПК на Django. (pet-project)

## Стек
- Python 3.13
- Django 6.1
- SQLite
- Redis (кэш)

## Установка

1. Клонируй репозиторий:
git clone https://github.com/pieceandwork/shopbykv.git
cd shopbykv
2. Создай виртуальное окружение:
python -m venv .venv
.venv\Scripts\activate # Windows
source .venv/bin/activate # Linux / macOS
3. Установи зависимости:
pip install -r requirements.txt
4. Примени миграции:
python manage.py migrate
5. Создай суперпользователя:
python manage.py createsuperuser
6. Запусти сервер:
python manage.py runserver
7. Открой http://127.0.0.1:8000/

## Автор
Yaroslav (pieceandwork) — https://github.com/pieceandwork