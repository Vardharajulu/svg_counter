import sqlite3, pytz
from flask import Flask, request, session, redirect
from datetime import datetime, timedelta
import html

app = Flask(__name__)
app.secret_key = "any-random-secret"  # Needed for session handling
DB_FILE = "chat.db"
app.permanent_session_lifetime = timedelta(minutes=10)
login_history = []


@app.before_request
def make_session_permanent():
    session.permanent = True

# Initialize DB
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                name TEXT,
                message TEXT
            )
        """)
init_db()

@app.route("/count", methods=["GET"])
def counter():
    global login_history
    return login_history

@app.route("/cls", methods=["GET", "POST"])
def clear_chat():
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd == 'ramvar':
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute("DELETE FROM messages")
            return "<h3>Chat history cleared.</h3><a href='/chat'>Back to chat</a>"
        else:
            return "<h3>Incorrect password.</h3><a href='/cls'>Try again</a>"

    return '''
        <h2>Enter Admin Password to Clear Chat</h2>
        <form method="post">
            Password: <input type="password" name="password" />
            <button type="submit">Clear</button>
        </form>
        <p><a href='/chat'>Cancel</a></p>
    '''

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == datetime.now().strftime("%d%m%Y"):
            session["authenticated"] = True
            global login_history
            chennai_tz = pytz.timezone('Asia/Kolkata')
            login_history.append({'time':datetime.now(chennai_tz).strftime('%d%m%Y %H:%M:%S'),
                                  'login': 'success'
                                  })
            return redirect("/chat")
        else:
            # global login_history
            chennai_tz = pytz.timezone('Asia/Kolkata')
            login_history.append({'time':datetime.now(chennai_tz).strftime('%d%m%Y %H:%M:%S'),
                                  'login': 'failed'
                                  })
            return "<h3>Incorrect password.</h3><a href='/'>Try again</a>"

    return '''
        <h2>Login to Chat</h2>
        <form method="post">
            Password: <input type="password" name="password" />
            <button type="submit">Login</button>
        </form>
    '''

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if not session.get("authenticated"):
        return redirect("/")

    if request.method == "POST":
        name = request.form.get("name", "Anonymous").strip()
        message = request.form.get("message", "").strip()
        if message[0] == "$":
            name = 'Vardha'
            message = message[1:]
        if message:
            with sqlite3.connect(DB_FILE) as conn:
                chennai_tz = pytz.timezone('Asia/Kolkata')
                conn.execute(
                    "INSERT INTO messages (timestamp, name, message) VALUES (?, ?, ?)",
                    (datetime.now(chennai_tz).strftime('%d-%m-%Y %H:%M:%S'), name, message)
                )
        return redirect("/chat")

    # Load messages
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute("SELECT timestamp, name, message FROM messages ORDER BY id").fetchall()
        history = "\n".join(
            f"{timestamp} - {html.escape(name)}: {html.escape(message)}" for timestamp, name, message in rows
        )
    name = str(datetime.now().strftime("%d%m%Y"))
    return f'''
        <h2>Chat Room</h2>
        <form method="post">
            Message: <input name="message" required />
            <button type="submit">Move to History</button>
        </form>
        <h3>History:</h3>
        <pre>{history or "No chat history yet."}</pre>
        <p><a href="/logout">Logout</a> </t> <a href="/cls">Clear History</a></p>
    '''

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
