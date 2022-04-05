from flask import Flask, render_template, request, redirect, session, flash
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, date, time

# configure app
app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Custom filters
app.jinja_env.filters["date"] = date
app.jinja_env.filters["time"] = time

# Configure to use SQLite database
db = SQL("sqlite:///mygarden.db")

@app.route("/")
@login_required
def index():

    user = db.execute("SELECT * FROM users WHERE id = :user_id", user_id = session["user_id"])
    top_plants = db.execute("SELECT * FROM plants WHERE email = :email AND removed = 0 ORDER BY timestamp DESC LIMIT 6", email=user[0]["email"])
    top_tasks = db.execute("SELECT * FROM tasks WHERE email = :email AND removed = 0 ORDER BY timestamp DESC LIMIT 6", email=user[0]["email"])
    plant_names = []

    for row in top_tasks:

        name = db.execute("SELECT plant_id, name FROM plants WHERE plant_id = :plant_id", plant_id=row["plant_id"])

        # if task IS associated with a plant
        # and is first instance of plant
        if len(name) == 1 and name[0] not in plant_names:
            plant_names.append(name[0])

    return render_template("index.html", plants=top_plants, tasks=top_tasks, names=plant_names)

@app.route("/plants", methods=["GET", "POST"])
@login_required
def plants():

    # if plant chosen to edit
    if request.method == "POST":

        plant_id = request.form.get("plant_id")

        # if not plant chosen
        if not plant_id:
            flash("Must choose plant to edit", "danger")
            return redirect("/plants")

        # go to edit page and load with existing information
        info = db.execute("SELECT * FROM plants WHERE plant_id = :plant_id", plant_id=plant_id)
        return render_template("plants_edit.html", info=info[0])

    else:
        # display all plants that are not removed in current user's inventory
        inventory = db.execute("SELECT * FROM plants JOIN users ON plants.email = users.email WHERE id = :user_id AND removed = 0 ORDER BY timestamp DESC", user_id=session["user_id"])
        return render_template("plants.html", plants=inventory)

@app.route("/plants_add", methods=["GET", "POST"])
@login_required
def plants_add():

    # if new plant added
    if request.method =="POST":
        name = request.form.get("name")
        quantity = request.form.get("quantity")
        notes = request.form.get("notes")

        # add plant to database under user's email
        email = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session["user_id"])
        db.execute("INSERT INTO plants(email, name, quantity, notes) VALUES(:email, :name, :quantity, :notes)",
        email=email[0]["email"], name=name, quantity=quantity, notes=notes)

        flash("Added!", "primary")
        return redirect("/plants")
    else:
        return render_template("plants_add.html")

@app.route("/plants_edit", methods=["GET", "POST"])
@login_required
def plants_edit():

    if request.method == "POST":
        plant_id = request.form.get("plant_id")
        name = request.form.get("name")
        quantity = request.form.get("quantity")
        notes = request.form.get("notes")

        db.execute("UPDATE plants SET name = :name, quantity = :quantity, notes = :notes, timestamp = CURRENT_TIMESTAMP WHERE plant_id = :plant_id",
        name=name, quantity=quantity, notes=notes, plant_id=plant_id)

        flash("Edits saved!", "primary")
        return redirect("/plants")
    else:
        return render_template("plants_edit.html")

@app.route("/plants_delete", methods=["GET", "POST"])
@login_required
def plants_delete():

    if request.method == "POST":
        plant_id = request.form.get("plant_id")
        # update status of removed plant AND all tasks with that plant
        db.execute("UPDATE plants SET removed = 1 WHERE plant_id = :plant_id", plant_id=plant_id)
        db.execute("UPDATE tasks SET removed = 1 WHERE plant_id = :plant_id", plant_id=plant_id)

        flash("Deleted!", "primary")
        return redirect("/plants")

    else:
        inventory = db.execute("SELECT * FROM plants JOIN users ON plants.email = users.email WHERE id = :user_id AND removed = 0 ORDER BY timestamp DESC", user_id=session["user_id"])
        return render_template("plants_delete.html", plants=inventory)

@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():

    if request.method == "POST":
        task_id = request.form.get("task_id")

        if not task_id:
            flash("Must choose task to edit", "danger")
            return redirect("/tasks")

        info = db.execute("SELECT * FROM tasks WHERE task_id = :task_id", task_id=task_id)
        plant_list = db.execute("SELECT * FROM plants JOIN users ON plants.email = users.email WHERE id = :user_id AND removed = 0 ORDER BY timestamp DESC", user_id=session["user_id"])

        return render_template("tasks_edit.html", info=info[0], plants=plant_list)

    else:
        inventory = db.execute("SELECT * FROM tasks JOIN users ON tasks.email = users.email WHERE id = :user_id AND removed = 0 ORDER BY timestamp DESC", user_id=session["user_id"])
        plant_names = []

        # get plant name of tagged plant for each task
        for row in inventory:
            name = db.execute("SELECT plant_id, name FROM plants WHERE plant_id = :plant_id", plant_id=row["plant_id"])

            # if task IS associated with a plant
            # and is first instance of plant
            if len(name) == 1 and name[0] not in plant_names:
                plant_names.append(name[0])

        return render_template("tasks.html", tasks=inventory, names=plant_names)

@app.route("/tasks_add", methods=["GET", "POST"])
@login_required
def tasks_add():
    if request.method == "POST":
        task = request.form.get("task")
        plant_id = request.form.get("plant_id")
        date = request.form.get("date")
        time = request.form.get("time")
        repeats = request.form.get("repeats")
        increment = request.form.get("increment")

        user = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session["user_id"])
        db.execute("INSERT INTO tasks(email, task, plant_id, date, time, repeats, increment) VALUES(:email, :task, :plant_id, :date, :time, :repeats, :increment)",
        email=user[0]["email"], task=task, plant_id=plant_id, date=date, time=time, repeats=repeats, increment=increment)

        flash("Added!", "primary")
        return redirect("/tasks")

    else:
        plant_list = db.execute("SELECT * FROM plants JOIN users ON plants.email = users.email WHERE id = :user_id AND removed = 0 ORDER BY timestamp DESC", user_id=session["user_id"])
        return render_template("tasks_add.html", plants=plant_list)

@app.route("/tasks_edit", methods=["GET", "POST"])
@login_required
def tasks_edit():

    if request.method == "POST":

        task_id = request.form.get("task_id")
        task = request.form.get("task")
        plant_id = request.form.get("plant_id")
        date = request.form.get("date")
        time = request.form.get("time")
        repeats = request.form.get("repeats")
        increment = request.form.get("increment")

        db.execute("UPDATE tasks SET task = :task, plant_id = :plant_id, date = :date, time = :time, repeats = :repeats, increment = :increment, timestamp = CURRENT_TIMESTAMP WHERE task_id = :task_id",
        task=task, plant_id=plant_id, date=date, time=time, repeats=repeats, increment=increment, task_id=task_id)

        flash("Edits saved!", "primary")
        return redirect("/tasks")

    else:
        return render_template("tasks_edit.html")

@app.route("/tasks_delete", methods=["GET", "POST"])
@login_required
def tasks_delete():

    if request.method == "POST":

        task_id = request.form.get("task_id")
        db.execute("UPDATE tasks SET removed = 1 WHERE task_id = :task_id", task_id=task_id)

        flash("Deleted!", "primary")
        return redirect("/tasks")

    else:

        inventory = db.execute("SELECT * FROM tasks JOIN users ON tasks.email = users.email WHERE id = :user_id AND removed = 0 ORDER BY timestamp DESC", user_id=session["user_id"])
        plant_names = []

        # get plant name of tagged plant for each task
        for row in inventory:
            name = db.execute("SELECT plant_id, name FROM plants WHERE plant_id = :plant_id", plant_id=row["plant_id"])

            # if task IS associated with a plant
            # and is first instance of plant
            if len(name) == 1 and name[0] not in plant_names:
                plant_names.append(name[0])

        return render_template("tasks_delete.html", tasks=inventory, names=plant_names)


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # if log in button pressed
    if request.method == "POST":

        # get email and password
        email = request.form.get("email")
        password = request.form.get("password")

        # find user in database with matching email (unique email)
        user = db.execute("SELECT * FROM users WHERE email = :email", email=email)

        # if no matching emails or if password is incorrect for email
        if len(user) != 1 or not check_password_hash(user[0]["password"], password):
            # reload login page with error message
            flash("Invalid email or password", "danger")
            return render_template("login.html")

        # remember user that's logged in
        session["user_id"] = user[0]["id"]

        # redirect to home page
        flash(f"Welcome back, {user[0]['first']}!", "primary")
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # get registration info
        first = request.form.get("first")
        last = request.form.get("last")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        # if confirmation doesn't match password
        if password != confirm:
            # reload page with error message
            flash("Passwords do no match", "danger")
            return render_template("register.html")

        # check if email has already been used
        users = db.execute("SELECT * FROM users WHERE email = :email", email=email)

        # if email in database, reload with error message
        if len(users) != 0:
            flash("Account already exists", "danger")
            return render_template("register.html")

        # add user info to users table
        db.execute("INSERT INTO users(email, first, last, password) VALUES(:email, :first, :last, :password)",
        email=email, first=first, last=last, password=generate_password_hash(password))

        # get user's unique id number
        user = db.execute("SELECT id FROM users WHERE email = :email", email=email)
        # session id is that number
        session["user_id"] = user[0]["id"]

        flash(f"Welcome to MyGarden, {first}!", "primary")
        return redirect("/")

    else:

        return render_template("register.html")


@app.route("/logout")
def logout():

    # Forget user_id
    session.clear()
    # Redirect to login page
    return redirect("/login")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("error.html", name=e.name, code=e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)