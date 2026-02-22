from flask import Flask, render_template, request, redirect, session, url_for, flash
from db import get_conn
from crypto_api import get_price
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# ---------------- User Auth ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        conn = get_conn()
        cr = conn.cursor()
        try:
            cr.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            flash("Registration successful! Please login.")
            return redirect("/login")
        except:
            flash("Email already exists.")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_conn()
        cr = conn.cursor()
        cr.execute("SELECT * FROM users WHERE email = ?", (email, ))
        user = cr.fetchone()
        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["email"] = user[1]
            return redirect("/dashboard")
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- Dashboard ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

# ---------------- Portfolio ----------------
@app.route("/portfolio", methods=["GET", "POST"])
def portfolio():
    if "user_id" not in session:
        return redirect("/login")
    conn = get_conn()
    cr = conn.cursor()
    if request.method == "POST":
        coin = request.form["coin"].lower()
        quantity = float(request.form["quantity"])
        buy_price = float(request.form["buy_price"])
        cr.execute("INSERT INTO portfolio(user_id, coin, quantity, buy_price) VALUES (?, ?, ?, ?)", (session["user_id"], coin, quantity, buy_price))
        conn.commit()

    cr.execute("SELECT coin, quantity, buy_price FROM portfolio WHERE user_id = ?", (session["user_id"],))
    rows = cr.fetchall()
    portfolio_data = []
    for coin, quantity, buy_price in rows:
        current_price = get_price(coin)
        if current_price:
            portfolio_data.append({
                "coin":coin, 
                "quantity":quantity,
                "buy_price":buy_price,
                "current_price":current_price["price"],
                "change_24h":current_price["change"]
            })
    conn.close()
    return render_template("portfolio.html", portfolio=portfolio_data)

# ---------------- Dashboard ----------------
@app.route("/alert",  methods=["GET", "POST"])
def alert():
    if "user_id" not in session:
        return redirect("/login")
    conn = get_conn()
    cr = conn.cursor()
    if request.method == "POST":
        coin = request.form["coin"].lower()
        target_price = float(request.form["target_price"])
        cr.execute("INSERT INTO alerts(user_id, coin, target_price) VALUES (?, ?, ?)", (session["user_id"], coin, target_price))
        conn.commit()
    cr.execute("SELECT coin, target_price FROM alerts WHERE user_id = ?", (session["user_id"],))
    rows = cr.fetchall()
    alerts_data = []
    for coin, target_price in rows:
        current_price = get_price(coin)
        if current_price:
            alerts_data.append({
                "coin":coin, 
                "target_price":target_price,
                "current_price":current_price["price"],
                "change_24h":current_price["change"]
            })
    conn.close()
    return render_template("alert_form.html", alerts_data=alerts_data)

if __name__ == "__main__":
    app.run(debug=True)
