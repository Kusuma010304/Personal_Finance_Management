import sqlite3
import datetime
import hashlib
class UserManager:
    def __init__(self):
        self.conn = sqlite3.connect("finance.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_user_table()

    def create_user_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def register_user(self, username, password):
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate_user(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, hashed_password)
        )
        return self.cursor.fetchone() is not None
class PersonalFinanceManager:
    def __init__(self, username):
        self.conn = sqlite3.connect("finance.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.username = username
        self.create_transactions_table()
        self.create_budget_table()

    def create_transactions_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY(username) REFERENCES users(username)
            )
        ''')
        self.conn.commit()

    def create_budget_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                username TEXT NOT NULL,
                category TEXT NOT NULL,
                budget REAL NOT NULL,
                PRIMARY KEY (username, category),
                FOREIGN KEY(username) REFERENCES users(username)
            )
        ''')
        self.conn.commit()
    def add_transaction(self, t_type, category, amount, description):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            INSERT INTO transactions (username, type, category, amount, description, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.username, t_type, category, amount, description,date))
        self.conn.commit()
        if t_type =="Expense":

            return self.check_budget(category)
        return None
    def update_transaction(self, transaction_id, amount, description):
        self.cursor.execute("""
            UPDATE transactions SET amount = ?, description = ?
            WHERE id = ? AND username = ?
        """, (amount, description, transaction_id, self.username))
        self.conn.commit()
    def delete_transaction(self, transaction_id):
        self.cursor.execute("""
            DELETE FROM transactions WHERE id = ? AND username = ?
        """, (transaction_id, self.username))
        self.conn.commit()
    def set_budget(self, category, budget):
        self.cursor.execute("""
            INSERT INTO budgets (username, category, budget)
            VALUES (?, ?, ?)
            ON CONFLICT(username, category) DO UPDATE SET budget = ?
        """, (self.username, category, budget, budget))
        self.conn.commit()
    def view_budgets(self):
        self.cursor.execute("SELECT category, budget FROM budgets WHERE username = ?", (self.username,))
        return self.cursor.fetchall()
    def check_budget(self, category):
        self.cursor.execute("SELECT budget FROM budgets WHERE username = ? AND category = ?", (self.username, category))
        budget_row = self.cursor.fetchone()
        if not budget_row:
            return None
        budget = budget_row[0]
        self.cursor.execute("""
            SELECT SUM(amount) FROM transactions 
                WHERE username = ? AND category = ? AND type = ?
            """, (self.username, category, "Expense"))
        total_expense = self.cursor.fetchone()[0] or 0
        if total_expense > budget:
            return{
                "category":category,
                "budget":budget,
                "spent":total_expense
            }
        return None
    def view_transactions(self, return_list=False):
        self.cursor.execute("SELECT * FROM transactions WHERE username = ?", (self.username,))
        rows = self.cursor.fetchall()
        if return_list:
            return [list(row) for row in rows]
        return rows
    def generate_report(self, period='monthly', return_data=False):
        if period == 'monthly':
            date_filter = datetime.datetime.now().strftime("%Y-%m")
        elif period == 'yearly':
            date_filter = datetime.datetime.now().strftime("%Y")
        else:
            return []

        self.cursor.execute("""
            SELECT category, SUM(amount) FROM transactions
            WHERE username = ? AND date LIKE ? AND type = ?
            GROUP BY category
        """, (self.username, f"{date_filter}%", "Expense"))
        rows = self.cursor.fetchall()

        if return_data:
            return rows
        return rows
    def close_connection(self):
        self.conn.close()
