import sqlite3
from datetime import datetime

def create_database():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    # Создание таблицы категорий
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT
    )''')

    # Создание таблицы пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )''')

    # Создание таблицы счетов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        name TEXT,
        balance REAL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )''')

    # Создание таблицы типов транзакций (расходы/доходы)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transaction_types (
        id INTEGER PRIMARY KEY,
        name TEXT
    )''')

    # Создание таблицы транзакций
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        amount REAL,
        category_id INTEGER,
        description TEXT,
        date TEXT,
        account_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories(id),
        FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
    )''')

    # Создание таблицы для связи транзакций с типами
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transaction_type_mapping (
        transaction_id INTEGER,
        type_id INTEGER,
        FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
        FOREIGN KEY (type_id) REFERENCES transaction_types(id) ON DELETE CASCADE
    )''')

    # Создание таблицы для тегов транзакций
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transaction_tags (
        transaction_id INTEGER,
        tag TEXT,
        FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
    )''')

    # Создание таблицы бюджета
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budget (
        id INTEGER PRIMARY KEY,
        category_id INTEGER,
        amount REAL,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )''')

    conn.commit()
    conn.close()

def populate_initial_data():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    # Добавление начальных данных, если необходимо
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        categories_data = [
            ('Продукты',), ('Транспорт',), ('Жилье',),
            ('Коммунальные услуги',), ('Развлечения',), ('Зарплата',),
            ('Фриланс',), ('Инвестиции',)
        ]
        cursor.executemany("INSERT INTO categories (name) VALUES (?)", categories_data)

    cursor.execute("SELECT COUNT(*) FROM transaction_types")
    if cursor.fetchone()[0] == 0:
        transaction_types_data = [('Расход',), ('Доход',)]
        cursor.executemany("INSERT INTO transaction_types (name) VALUES (?)", transaction_types_data)

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users_data = [('user1', 'password1'), ('user2', 'password2')]
        cursor.executemany("INSERT INTO users (username, password) VALUES (?, ?)", users_data)

    cursor.execute("SELECT COUNT(*) FROM accounts")
    if cursor.fetchone()[0] == 0:
        accounts_data = [(1, 'Счет пользователя 1', 1500.00), (2, 'Счет пользователя 2', 2500.00)]
        cursor.executemany("INSERT INTO accounts (user_id, name, balance) VALUES (?, ?, ?)", accounts_data)

    # Добавление транзакций
    cursor.execute("SELECT COUNT(*) FROM transactions")
    if cursor.fetchone()[0] == 0:
        transactions_data = [
            (200.00, 1, "Покупка в магазине", datetime.now().strftime("%Y-%m-%d"), 1),
            (1500.00, 6, "Зарплата за месяц", datetime.now().strftime("%Y-%m-%d"), 1)
        ]
        cursor.executemany("INSERT INTO transactions (amount, category_id, description, date, account_id) VALUES (?, ?, ?, ?, ?)", transactions_data)

    # Добавление бюджетов
    cursor.execute("SELECT COUNT(*) FROM budget")
    if cursor.fetchone()[0] == 0:
        budget_data = [
            (1, 500.00),
            (2, 300.00)
        ]
        cursor.executemany("INSERT INTO budget (category_id, amount) VALUES (?, ?)", budget_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    populate_initial_data()
