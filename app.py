import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime
import sqlite3

class FinanceApp:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def get_category_name_by_id(self, category_id):
        self.cursor.execute("SELECT name FROM categories WHERE id = ?", (category_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_user_name_by_id(self, user_id):
        self.cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def check_credentials(self, username, password):
        self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = self.cursor.fetchone()
        return user is not None

    def user_exists(self, username):
        """ Проверяет, существует ли пользователь с данным username """
        self.cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        return self.cursor.fetchone() is not None

    def register_user(self, username, password):
        """ Регистрирует нового пользователя, если тот еще не существует """
        if self.user_exists(username):
            messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует")
        else:
            try:
                self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                self.conn.commit()
                messagebox.showinfo("Успех", "Пользователь успешно зарегистрирован")
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка при регистрации пользователя: {e}")
                self.conn.rollback()

    # Методы удаления
    def delete_user(self, user_id):
        try:
            self.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            self.conn.commit()
            messagebox.showinfo("Успех", "Пользователь успешно удален")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении пользователя: {e}")
            self.conn.rollback()

    def delete_transaction(self, transaction_id):
        try:
            self.cursor.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
            self.conn.commit()
            messagebox.showinfo("Успех", "Транзакция успешно удалена")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении транзакции: {e}")
            self.conn.rollback()

    def delete_account(self, account_id):
        try:
            self.cursor.execute("DELETE FROM accounts WHERE id=?", (account_id,))
            self.conn.commit()
            messagebox.showinfo("Успех", "Счет успешно удален")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении счета: {e}")
            self.conn.rollback()

    def delete_category(self, category_id):
        try:
            self.cursor.execute("DELETE FROM categories WHERE id=?", (category_id,))
            self.conn.commit()
            messagebox.showinfo("Успех", "Категория успешно удалена")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении категории: {e}")
            self.conn.rollback()

    def delete_budget(self, budget_id):
        try:
            self.cursor.execute("DELETE FROM budget WHERE id=?", (budget_id,))
            self.conn.commit()
            messagebox.showinfo("Успех", "Бюджет успешно удален")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении бюджета: {e}")
            self.conn.rollback()

    def __del__(self):
        self.conn.close()

    def get_transactions(self):
        self.cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
        return self.cursor.fetchall()

    def validate_and_format_date(self, date_str):
        try:
            # Пробуем преобразовать дату в соответствующий формат
            return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            # Возвращаем None или выбрасываем ошибку, если формат некорректен
            return None

    def add_transaction(self, amount, category_name, description, date_str, type_name=None, tags=None):
        # Проверка и форматирование даты
        date_formatted = date_str # self.validate_and_format_date(date_str)
        print(date_formatted)
        if not date_formatted:
            raise ValueError("Неверный формат даты, используйте DD/MM/YYYY")

        self.cursor.execute("SELECT id FROM categories WHERE name=?", (category_name,))
        category_id = self.cursor.fetchone()[0]
        type_id = None
        if type_name:
            self.cursor.execute("SELECT id FROM transaction_types WHERE name=?", (type_name,))
            type_id_result = self.cursor.fetchone()
            type_id = type_id_result[0] if type_id_result else None

        self.cursor.execute(
            "INSERT INTO transactions (amount, category_id, description, date) VALUES (?, ?, ?, ?)",
            (amount, category_id, description, date_formatted)
        )
        transaction_id = self.cursor.lastrowid
        if type_id:
            self.add_transaction_type_mapping(transaction_id, type_id)
        if tags:
            for tag in tags.split(','):
                self.add_transaction_tag(transaction_id, tag)
        self.conn.commit()
        
    def get_categories(self):
        self.cursor.execute("SELECT * FROM categories")
        return self.cursor.fetchall()

    def add_category(self, name):
        self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        self.conn.commit()

    def get_budget(self):
        self.cursor.execute("SELECT * FROM budget")
        return self.cursor.fetchall()

    def add_budget(self, category_name, amount):
        # Get category ID from name
        self.cursor.execute("SELECT id FROM categories WHERE name=?", (category_name,))
        category_id = self.cursor.fetchone()[0]

        self.cursor.execute("INSERT INTO budget (category_id, amount) VALUES (?, ?)", (category_id, float(amount)))
        self.conn.commit()

    def get_users(self):
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()

    def add_user(self, username, password):
        self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        self.conn.commit()

    def get_accounts(self):
        self.cursor.execute("SELECT * FROM accounts")
        return self.cursor.fetchall()

    def add_account(self, username, name, balance):
        try:
            # Получаем user_id по имени пользователя
            self.cursor.execute("SELECT id FROM users WHERE username=?", (username,))
            user_id_result = self.cursor.fetchone()
            if user_id_result:
                user_id = user_id_result[0]
                # Добавляем счет с user_id
                self.cursor.execute("INSERT INTO accounts (user_id, name, balance) VALUES (?, ?, ?)", (user_id, name, float(balance)))
                self.conn.commit()
                messagebox.showinfo("Успех", "Счет успешно добавлен")
            else:
                messagebox.showerror("Ошибка", "Пользователь не найден")
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении счета: {e}")
            self.conn.rollback()

    def get_transaction_types(self):
        self.cursor.execute("SELECT * FROM transaction_types")
        return self.cursor.fetchall()

    def add_transaction_type(self, name):
        self.cursor.execute("INSERT INTO transaction_types (name) VALUES (?)", (name,))
        self.conn.commit()

    def get_transaction_type_mapping(self):
        self.cursor.execute("SELECT * FROM transaction_type_mapping")
        return self.cursor.fetchall()

    def add_transaction_type_mapping(self, transaction_id, type_id):
        self.cursor.execute("INSERT INTO transaction_type_mapping (transaction_id, type_id) VALUES (?, ?)",
                            (transaction_id, type_id))
        self.conn.commit()

    def get_transaction_tags(self):
        self.cursor.execute("SELECT * FROM transaction_tags")
        return self.cursor.fetchall()

    def add_transaction_tag(self, transaction_id, tag):
        self.cursor.execute("INSERT INTO transaction_tags (transaction_id, tag) VALUES (?, ?)", (transaction_id, tag))
        self.conn.commit()


class LoginWindow:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.master.title("Вход")
        
        self.master.geometry('400x300')

        self.username_label = tk.Label(self.master, text="Имя пользователя:")
        self.username_label.pack()

        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack()

        self.password_label = tk.Label(self.master, text="Пароль:")
        self.password_label.pack()

        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(self.master, text="Войти", command=self.login)
        self.login_button.pack()

        self.register_button = tk.Button(self.master, text="Регистрация пользователя", command=self.register_user)
        self.register_button.pack(padx=10, pady=10)

    def register_user(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Регистрация пользователя")
        
        username_label = tk.Label(dialog, text="Имя пользователя:")
        username_label.pack(padx=5, pady=5)
        
        username_entry = tk.Entry(dialog)
        username_entry.pack(padx=5, pady=5)
        
        password_label = tk.Label(dialog, text="Пароль:")
        password_label.pack(padx=5, pady=5)
        
        password_entry = tk.Entry(dialog, show="*")
        password_entry.pack(padx=5, pady=5)
        
        def submit_registration():
            username = username_entry.get()
            password = password_entry.get()
            if username and password:  # Проверка на непустые значения
                self.app.register_user(username, password)
                dialog.destroy()
            else:
                messagebox.showwarning("Предупреждение", "Имя пользователя и пароль не могут быть пустыми")
        
        register_button = tk.Button(dialog, text="Зарегистрировать", command=submit_registration)
        register_button.pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.app.check_credentials(username, password):
            self.master.destroy()  # Закрываем окно входа
            root = tk.Tk()  # Create a new Tkinter root window
            gui = FinanceAppGUI(root, self.app)  # Instantiate FinanceAppGUI directly
            root.mainloop()  # Start the main event loop
        else:
            messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")


class FinanceAppGUI:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.master.title("Финансовое приложение")
        
        self.transaction_frame = tk.Frame(self.master)
        self.transaction_frame.pack(padx=10, pady=10)

        self.category_frame = tk.Frame(self.master)
        self.category_frame.pack(padx=10, pady=10)

        self.budget_frame = tk.Frame(self.master)
        self.budget_frame.pack(padx=10, pady=10, side="right")

        self.user_frame = tk.Frame(self.master)
        self.user_frame.pack(padx=10, pady=10, side="right")

        self.account_frame = tk.Frame(self.master)
        self.account_frame.pack(padx=10, pady=10)
        
        self.transaction_label = tk.Label(self.transaction_frame, text="Транзакции:")
        self.transaction_label.pack()
            
        self.transaction_treeview = ttk.Treeview(self.transaction_frame, columns=('Сумма', 'Категория', 'Описание', 'Дата'), show="headings")
        self.transaction_treeview.heading('Сумма', text='Сумма')
        self.transaction_treeview.heading('Категория', text='Категория')
        self.transaction_treeview.heading('Описание', text='Описание')
        self.transaction_treeview.heading('Дата', text='Дата')
        self.transaction_treeview.pack()

        self.category_treeview = ttk.Treeview(self.category_frame, columns=('Категория',), show="headings")
        self.category_treeview.heading('Категория', text='Категория')
        self.category_treeview.pack()

        self.budget_treeview = ttk.Treeview(self.budget_frame, columns=('Категория', 'Сумма'), show="headings")
        self.budget_treeview.heading('Категория', text='Категория')
        self.budget_treeview.heading('Сумма', text='Сумма')
        self.budget_treeview.pack()

        self.user_treeview = ttk.Treeview(self.user_frame, columns=('Имя', 'Пароль'), show="headings")
        self.user_treeview.heading('Имя', text='Имя')
        self.user_treeview.heading('Пароль', text='Пароль')
        self.user_treeview.pack()

        self.account_treeview = ttk.Treeview(self.account_frame, columns=('Пользователь', 'Название счета', 'Баланс'), show="headings")
        self.account_treeview.heading('Пользователь', text='Пользователь')
        self.account_treeview.heading('Название счета', text='Название счета')
        self.account_treeview.heading('Баланс', text='Баланс')
        self.account_treeview.pack()

        self.refresh_transactions()
        
        self.add_transaction_button = tk.Button(self.transaction_frame, text="Добавить транзакцию", command=self.add_transaction)
        self.add_transaction_button.pack(pady=5)
        
        self.category_label = tk.Label(self.category_frame, text="Категории:")
        self.category_label.pack()
    
        self.refresh_categories()
        
        self.add_category_button = tk.Button(self.category_frame, text="Добавить категорию", command=self.add_category)
        self.add_category_button.pack(pady=5)

        self.delete_transaction_button = tk.Button(self.transaction_frame, text="Удалить выбранную транзакцию", command=self.delete_transaction)
        self.delete_transaction_button.pack(pady=5)
        
        self.delete_category_button = tk.Button(self.category_frame, text="Удалить выбранную категорию", command=self.delete_category)
        self.delete_category_button.pack(pady=5)

        # добавляем кнопку и функцию для отображения бюджета
        self.budget_label = tk.Label(self.budget_frame, text="Бюджет:")
        self.budget_label.pack()

        self.refresh_budget()

        self.add_budget_button = tk.Button(self.budget_frame, text="Добавить бюджет", command=self.add_budget)
        self.add_budget_button.pack(pady=5)

        # добавляем кнопку и функцию для отображения пользователей
        self.user_label = tk.Label(self.user_frame, text="Пользователи:")
        self.user_label.pack()

        self.refresh_users()

        self.add_user_button = tk.Button(self.user_frame, text="Добавить пользователя", command=self.add_user)
        self.add_user_button.pack(pady=5)

        # добавляем кнопку и функцию для отображения счетов
        self.account_label = tk.Label(self.account_frame, text="Счета:")
        self.account_label.pack()

        self.refresh_accounts()

        self.add_account_button = tk.Button(self.account_frame, text="Добавить счет", command=self.add_account)
        self.add_account_button.pack(pady=5)

        self.delete_user_button = tk.Button(self.user_frame, text="Удалить пользователя", command=self.delete_user)
        self.delete_user_button.pack(pady=5)

        self.delete_account_button = tk.Button(self.account_frame, text="Удалить счет", command=self.delete_account)
        self.delete_account_button.pack(pady=5)

        self.delete_budget_button = tk.Button(self.budget_frame, text="Удалить бюджет", command=self.delete_budget)
        self.delete_budget_button.pack(pady=5)

    def add_budget(self):
        # создаем диалоговое окно для добавления бюджета
        dialog = tk.Toplevel(self.master)
        dialog.title("Добавление бюджета")

        # Добавление кнопки и функции для выбора категории из списка при добавлении бюджета
        category_label = tk.Label(dialog, text="Категория:")
        category_label.pack(padx=5, pady=5)
        category_var = tk.StringVar(dialog)
        categories = self.app.get_categories()
        category_options = [category[1] for category in categories]
        category_dropdown = tk.OptionMenu(dialog, category_var, *category_options)
        category_dropdown.pack(padx=5, pady=5)

        amount_label = tk.Label(dialog, text="Сумма:")
        amount_label.pack(padx=5, pady=5)

        amount_entry = tk.Entry(dialog)
        amount_entry.pack(padx=5, pady=5)

        def add_budget_to_db():
            category = category_var.get()
            amount = amount_entry.get()
            self.app.add_budget(category, amount)
            messagebox.showinfo("Успех", "Бюджет успешно добавлен")
            dialog.destroy()
            self.refresh_budget()

        add_button = tk.Button(dialog, text="Добавить", command=add_budget_to_db)
        add_button.pack(pady=5)

    def add_user(self):
        # создаем диалоговое окно для добавления пользователя
        dialog = tk.Toplevel(self.master)
        dialog.title("Добавление пользователя")

        username_label = tk.Label(dialog, text="Имя пользователя:")
        username_label.pack(padx=5, pady=5)

        username_entry = tk.Entry(dialog)
        username_entry.pack(padx=5, pady=5)

        password_label = tk.Label(dialog, text="Пароль:")
        password_label.pack(padx=5, pady=5)

        password_entry = tk.Entry(dialog)
        password_entry.pack(padx=5, pady=5)

        def add_user_to_db():
            username = username_entry.get()
            password = password_entry.get()
            self.app.add_user(username, password)
            messagebox.showinfo("Успех", "Пользователь успешно добавлен")
            dialog.destroy()
            self.refresh_users()

        add_button = tk.Button(dialog, text="Добавить", command=add_user_to_db)
        add_button.pack(pady=5)

    def add_account(self):
        # создаем диалоговое окно для добавления счета
        dialog = tk.Toplevel(self.master)
        dialog.title("Добавление счета")

        # Добавление кнопки и функции для выбора пользователя из списка при добавлении счета
        user_label = tk.Label(dialog, text="Пользователь:")
        user_label.pack(padx=5, pady=5)
        user_var = tk.StringVar(dialog)
        users = self.app.get_users()
        user_options = [user[1] for user in users]
        user_dropdown = tk.OptionMenu(dialog, user_var, *user_options)
        user_dropdown.pack(padx=5, pady=5)

        user_entry = tk.Entry(dialog)
        user_entry.pack(padx=5, pady=5)

        name_label = tk.Label(dialog, text="Название счета:")
        name_label.pack(padx=5, pady=5)

        name_entry = tk.Entry(dialog)
        name_entry.pack(padx=5, pady=5)

        balance_label = tk.Label(dialog, text="Баланс:")
        balance_label.pack(padx=5, pady=5)

        balance_entry = tk.Entry(dialog)
        balance_entry.pack(padx=5, pady=5)

        def add_account_to_db():
            user = user_var.get()
            name = name_entry.get()
            balance = balance_entry.get()
            self.app.add_account(user, name, balance)
            messagebox.showinfo("Успех", "Счет успешно добавлен")
            dialog.destroy()
            self.refresh_accounts()

        add_button = tk.Button(dialog, text="Добавить", command=add_account_to_db)
        add_button.pack(pady=5)
            
    def delete_transaction(self):
        selected_item = self.transaction_treeview.selection()
        if selected_item:
            transaction_id = selected_item[0]  
            transaction_id_numeric = int(transaction_id[1:])
            # Получаем список всех транзакций
            transactions = self.app.get_transactions()
            # Проверяем, существует ли транзакция с заданным идентификатором
            if any(transaction[0] == transaction_id_numeric for transaction in transactions):
                # Удаляем транзакцию
                self.app.delete_transaction(transaction_id_numeric)
                # Удаляем выбранный элемент из таблицы транзакций на форме
                self.transaction_treeview.delete(transaction_id)
                # Обновляем список транзакций
                self.refresh_transactions()
                # Обновляем другие таблицы
                self.refresh_categories()
                self.refresh_users()
                self.refresh_accounts()
                self.refresh_budget()
                messagebox.showinfo("Успех", "Транзакция успешно удалена")
            else:
                messagebox.showerror("Ошибка", "Выбранная транзакция не существует!")
        else:
            messagebox.showwarning("Предупреждение", "Выберите транзакцию для удаления!")

    def delete_category(self):
        selected_items = self.category_treeview.selection()
        if selected_items:
            for item_id in selected_items:
                try:
                    # Удалить категорию
                    self.app.delete_category(int(item_id))
                    # Удалить выбранный элемент из таблицы категорий на форме
                    self.category_treeview.delete(item_id)
                    # Обновить другие таблицы
                    self.refresh_transactions()
                    self.refresh_budget()
                    messagebox.showinfo("Успех", "Категория успешно удалена")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Произошла ошибка при удалении категории: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Выберите категорию для удаления!")
            
    def delete_user(self):
        selected_items = self.user_treeview.selection()
        if selected_items:
            for item_id in selected_items:
                try:
                    # Удалить пользователя
                    self.app.delete_user(int(item_id))
                    # Удалить выбранный элемент из таблицы пользователей на форме
                    self.user_treeview.delete(item_id)
                    # Обновить другие таблицы
                    self.refresh_transactions()
                    messagebox.showinfo("Успех", "Пользователь успешно удален")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Произошла ошибка при удалении пользователя: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления!")

    def delete_account(self):
        selected_items = self.account_treeview.selection()
        if selected_items:
            for item_id in selected_items:
                try:
                    # Удалить счет
                    self.app.delete_account(int(item_id))
                    # Удалить выбранный элемент из таблицы счетов на форме
                    self.account_treeview.delete(item_id)
                    # Обновить другие таблицы
                    self.refresh_transactions()
                    messagebox.showinfo("Успех", "Счет успешно удален")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Произошла ошибка при удалении счета: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Выберите счет для удаления!")

    def delete_budget(self):
        selected_items = self.budget_treeview.selection()
        if selected_items:
            for item_id in selected_items:
                try:
                    # Удалить бюджет
                    self.app.delete_budget(int(item_id))
                    # Удалить выбранный элемент из таблицы бюджетов на форме
                    self.budget_treeview.delete(item_id)
                    # Обновить другие таблицы
                    self.refresh_transactions()
                    messagebox.showinfo("Успех", "Бюджет успешно удален")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Произошла ошибка при удалении бюджета: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Выберите бюджет для удаления!")

    # Методы обновления данных
    def refresh_transactions(self):
        self.transaction_treeview.delete(*self.transaction_treeview.get_children())
        transactions = self.app.get_transactions()
        categories = self.app.get_categories()
        category_ids = set(category[0] for category in categories)  # Создаем множество идентификаторов категорий
        for transaction in transactions:
            category_id = transaction[2]
            # Проверяем, что категория существует в списке категорий
            if category_id in category_ids:
                category_name = self.app.get_category_name_by_id(category_id)
                date = datetime.strptime(transaction[4], "%Y-%m-%d")
                date_display = date.strftime("%Y-%m-%d")
                self.transaction_treeview.insert('', 'end', values=(transaction[1], category_name, transaction[3], date_display))

    def refresh_categories(self):
        self.category_treeview.delete(*self.category_treeview.get_children())
        categories = self.app.get_categories()
        category_ids = set(category[0] for category in categories)
        for category in categories:
            if category[0] in category_ids:
                self.category_treeview.insert('', 'end', iid=category[0], values=(category[1],))


    def refresh_users(self):
        self.user_treeview.delete(*self.user_treeview.get_children())
        users = self.app.get_users()
        user_ids = set(user[0] for user in users)
        for user in users:
            if user[0] in user_ids:
                self.user_treeview.insert('', 'end', iid=user[0], values=(user[1], user[2]))

    def refresh_accounts(self):
        self.account_treeview.delete(*self.account_treeview.get_children())
        accounts = self.app.get_accounts()
        account_ids = set(account[0] for account in accounts)
        for account in accounts:
            if account[0] in account_ids:
                user_name = self.app.get_user_name_by_id(account[1])
                self.account_treeview.insert('', 'end', iid=account[0], values=(user_name, account[2], account[3]))
    
    def refresh_budget(self):
        self.budget_treeview.delete(*self.budget_treeview.get_children())
        budgets = self.app.get_budget()
        budget_ids = set(budget[0] for budget in budgets)
        for budget in budgets:
            if budget[0] in budget_ids:
                category_name = self.app.get_category_name_by_id(budget[1])
                self.budget_treeview.insert('', 'end', iid=budget[0], values=(category_name, budget[2]))
    '''

    def refresh_categories(self):
        self.category_treeview.delete(*self.category_treeview.get_children())
        categories = self.app.get_categories()
        category_ids = set(category[0] for category in categories)
        for category in categories:
            if category[0] in category_ids:
                # Проверяем связанные транзакции и удаляем их из treeview
                transactions_to_delete = []
                for item in self.transaction_treeview.get_children():
                    if self.transaction_treeview.item(item, "values")[1] == category[1]:
                        transactions_to_delete.append(item)
                for item in transactions_to_delete:
                    self.transaction_treeview.delete(item)
                self.category_treeview.insert('', 'end', iid=category[0], values=(category[1],))
                
    def refresh_users(self):
        self.user_treeview.delete(*self.user_treeview.get_children())
        users = self.app.get_users()
        user_ids = set(user[0] for user in users)
        for user in users:
            if user[0] in user_ids:
                # Проверяем связанные счета и удаляем их из treeview
                accounts_to_delete = []
                for item in self.account_treeview.get_children():
                    if self.account_treeview.item(item, "values")[0] == user[1]:
                        accounts_to_delete.append(item)
                for item in accounts_to_delete:
                    self.account_treeview.delete(item)

                self.user_treeview.insert('', 'end', iid=user[0], values=(user[1], user[2]))

    def refresh_accounts(self):
        self.account_treeview.delete(*self.account_treeview.get_children())
        accounts = self.app.get_accounts()
        account_ids = set(account[0] for account in accounts)
        for account in accounts:
            if account[0] in account_ids:
                # Проверяем связанные транзакции и удаляем их из treeview
                transactions_to_delete = []
                for item in self.transaction_treeview.get_children():
                    if self.transaction_treeview.item(item, "values")[0] == account[2]:
                        transactions_to_delete.append(item)
                for item in transactions_to_delete:
                    self.transaction_treeview.delete(item)

                user_name = self.app.get_user_name_by_id(account[1])
                self.account_treeview.insert('', 'end', iid=account[0], values=(user_name, account[2], account[3]))

    def refresh_budget(self):
        self.budget_treeview.delete(*self.budget_treeview.get_children())
        budgets = self.app.get_budget()
        budget_ids = set(budget[0] for budget in budgets)
        for budget in budgets:
            if budget[0] in budget_ids:
                # Проверяем связанные транзакции и удаляем их из treeview
                transactions_to_delete = []
                for item in self.transaction_treeview.get_children():
                    if self.transaction_treeview.item(item, "values")[1] == self.app.get_category_name_by_id(budget[1]):
                        transactions_to_delete.append(item)
                for item in transactions_to_delete:
                    self.transaction_treeview.delete(item)

                category_name = self.app.get_category_name_by_id(budget[1])
                self.budget_treeview.insert('', 'end', iid=budget[0], values=(category_name, budget[2]))
    '''
    
    def add_transaction(self):
        # Создаем диалоговое окно для ввода данных о новой транзакции
        dialog = tk.Toplevel(self.master)
        dialog.title("Добавление транзакции")
        
        amount_label = tk.Label(dialog, text="Сумма:")
        amount_label.grid(row=0, column=0, padx=5, pady=5)
        amount_entry = tk.Entry(dialog)
        amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        category_label = tk.Label(dialog, text="Категория:")
        category_label.grid(row=1, column=0, padx=5, pady=5)
        category_var = tk.StringVar(dialog)
        categories = self.app.get_categories()
        category_options = [category[1] for category in categories]
        category_dropdown = tk.OptionMenu(dialog, category_var, *category_options)
        category_dropdown.grid(row=1, column=1, padx=5, pady=5)
        
        description_label = tk.Label(dialog, text="Описание:")
        description_label.grid(row=2, column=0, padx=5, pady=5)
        description_entry = tk.Entry(dialog)
        description_entry.grid(row=2, column=1, padx=5, pady=5)
        
        date_label = tk.Label(dialog, text="Дата:")
        date_label.grid(row=3, column=0, padx=5, pady=5)
        date_var = tk.StringVar()
        date_entry = tk.Entry(dialog, textvariable=date_var)
        date_entry.grid(row=3, column=1, padx=5, pady=5)

        type_label = tk.Label(dialog, text="Тип:")
        type_label.grid(row=4, column=0, padx=5, pady=5)
        type_var = tk.StringVar(dialog)
        types = self.app.get_transaction_types()
        type_options = [type[1] for type in types]
        type_dropdown = tk.OptionMenu(dialog, type_var, *type_options)
        type_dropdown.grid(row=4, column=1, padx=5, pady=5)
        
        tags_label = tk.Label(dialog, text="Теги:")
        tags_label.grid(row=5, column=0, padx=5, pady=5)
        tags_entry = tk.Entry(dialog)
        tags_entry.grid(row=5, column=1, padx=5, pady=5)
                
        # Добавляем возможность выбора даты из календаря
        def choose_date():
            cal = Calendar(dialog, selectmode='day', year=2024, month=4, day=13)
            cal.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

            def set_date():
                selected_date = cal.selection_get()
                formatted_date = selected_date.strftime("%d/%m/%Y")  # Ensure the output is in the right format
                print(formatted_date)
                date_var.set(formatted_date)
                cal.destroy()  # Destroy the calendar widget after date is chosen
                ok_button.destroy()  # Destroy the OK button after it's used

            ok_button = tk.Button(dialog, text="OK", command=set_date)
            ok_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        date_picker_button = tk.Button(dialog, text="Выбрать", command=choose_date)
        date_picker_button.grid(row=3, column=2, padx=5, pady=5)
        
        def add_transaction_to_db():
            try:
                amount = float(amount_entry.get())
                category = category_var.get()
                description = description_entry.get()
                date_str = date_var.get()
                
                # Валидация и форматирование даты
                date = self.app.validate_and_format_date(date_str)
                if not date:
                    messagebox.showerror("Ошибка", "Некорректный формат даты. Используйте формат DD/MM/YYYY.")
                    return

                type_name = type_var.get() if type_var.get() != 'Выберите тип' else None
                
                self.app.add_transaction(amount, category, description, date, type_name, tags_entry.get())
                messagebox.showinfo("Успех", "Транзакция успешно добавлена")
                dialog.destroy()
                self.refresh_transactions()
            except ValueError as e:
                messagebox.showerror("Ошибка ввода", str(e))
        
        add_button = tk.Button(dialog, text="Добавить", command=add_transaction_to_db)
        add_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
    
    def add_category(self):
        # Создаем диалоговое окно для ввода названия новой категории
        dialog = tk.Toplevel(self.master)
        dialog.title("Добавление категории")
        
        category_label = tk.Label(dialog, text="Название категории:")
        category_label.pack(padx=5, pady=5)
        
        category_entry = tk.Entry(dialog)
        category_entry.pack(padx=5, pady=5)
        
        def add_category_to_db():
            category = category_entry.get()
            self.app.add_category(category)
            messagebox.showinfo("Успех", "Категория успешно добавлена")
            dialog.destroy()
            self.refresh_categories()
        
        add_button = tk.Button(dialog, text="Добавить", command=add_category_to_db)
        add_button.pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp('finance.db')
    login_window = LoginWindow(root, app)
    root.mainloop()
