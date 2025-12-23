from flask import Flask, render_template, request, redirect, session
from finance_manager import UserManager, PersonalFinanceManager

app = Flask(__name__)
app.secret_key = "supersecretkey"

user_manager = UserManager()
@app.route('/')
def index():
    if "username" not in session:
        return redirect("/login")
    
    manager = PersonalFinanceManager(session["username"])
    transactions = manager.view_transactions(return_list=True)
    budgets = manager.view_budgets()
    manager.close_connection()
    
    return render_template("index.html", transactions=transactions, budgets=budgets)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        success = user_manager.register_user(username, password)
        if success:
            return redirect("/login")
        else:
            return "Username already exists!"
    return render_template("register.html")
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if user_manager.authenticate_user(username, password):
            session['username'] = username
            return redirect("/")
        else:
            return "Invalid credentials!"
    return render_template("login.html")
@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect("/login")
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    if "username" not in session:
        return redirect("/login")

    manager = PersonalFinanceManager(session['username'])

    warning = manager.add_transaction(
        request.form['type'],
        request.form['category'],
        float(request.form['amount']),
        request.form['description']
    )

    transactions = manager.view_transactions()
    budgets = manager.view_budgets()
    manager.close_connection()

    return render_template(
        "index.html",
        transactions=transactions,
        budgets=budgets,
        warning=warning
    )
@app.route('/update_transaction', methods=['POST'])
def update_transaction():
    if "username" not in session:
        return redirect("/login")
    transaction_id = int(request.form['id'])
    amount = float(request.form['amount'])
    description = request.form['description']
    manager = PersonalFinanceManager(session['username'])
    manager.update_transaction(transaction_id, amount, description)
    manager.close_connection()
    return redirect("/")
@app.route('/delete_transaction', methods=['POST'])
def delete_transaction():
    if "username" not in session:
        return redirect("/login")
    transaction_id = int(request.form['id'])
    manager = PersonalFinanceManager(session['username'])
    manager.delete_transaction(transaction_id)
    manager.close_connection()
    return redirect("/")
@app.route('/set_budget', methods=['POST'])
def set_budget():
    if "username" not in session:
        return redirect("/login")
    category = request.form['category']
    budget = float(request.form['budget'])
    manager = PersonalFinanceManager(session['username'])
    manager.set_budget(category, budget)
    manager.close_connection()
    return redirect("/")
@app.route('/report', methods=['GET'])
def report():
    if "username" not in session:
        return redirect("/login")
    period = request.args.get("period", "monthly")
    manager = PersonalFinanceManager(session['username'])
    report_data = manager.generate_report(period, return_data=True)
    manager.close_connection()
    return render_template("report.html", period=period, report=report_data)

if __name__ == "__main__":
    app.run(debug=True)
