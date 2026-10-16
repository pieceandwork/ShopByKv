# ShopByKv

🛒 Онлайн-магазин комплектующих для ПК на Django. (pet-project)

## Стек
- Python 3.13
- Django 6.1
- SQLite
- Redis (кэш)

## Установка

1. Клонируй репозиторий:
   ```bash
   git clone https://github.com/pieceandwork/shopbykv.git
   cd shopbykv
   ```

2. Создай виртуальное окружение:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # Windows
   source .venv/bin/activate  # Linux / macOS
   ```

3. Установи зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Примени миграции:
   ```bash
   python manage.py migrate
   ```

5. Создай суперпользователя:
   ```bash
   python manage.py createsuperuser
   ```

6. Запусти сервер:
   ```bash
   python manage.py runserver
   ```

7. Открой http://127.0.0.1:8000/

## Автор
Ярослав (pieceandwork) — https://github.com/pieceandwork

---

# English

## ShopByKv

🛒 Online PC components store built with Django. (pet-project)

## Tech Stack
- Python 3.13
- Django 6.1
- SQLite
- Redis (cache)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/pieceandwork/shopbykv.git
   cd shopbykv
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # Windows
   source .venv/bin/activate  # Linux / macOS
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the server:
   ```bash
   python manage.py runserver
   ```

7. Open http://127.0.0.1:8000/

## Author
Yaroslav (pieceandwork) — https://github.com/pieceandwork