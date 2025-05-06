from flask import Flask, render_template, request, redirect, session,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Add your own secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'  # Optional but good practice
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    todos = db.relationship('Todo', backref='user', lazy=True)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        user = User.query.filter_by(username=username).first()

        if not user:
            flash("User not found. Please register.", "danger")
            return redirect("/")
        
        if not check_password_hash(user.password, password):
            flash("Incorrect password. Try again.", "danger")
            return redirect("/")

        # Success
        session['user_id'] = user.user_id
        return redirect("/dashboard")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already registered. Please login or use a different email.")
            return redirect("/register")
            

        # Check if username already exists
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash("Username already taken. Please choose a different one.")
            return redirect("/register") 

        # All good, hash password and create user
        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect("/")
    return render_template("register.html") 

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect("/")
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        todo = Todo(title=title, description=description, user=user)
        db.session.add(todo)
        db.session.commit()

    allTodo = Todo.query.filter_by(user=user).all()
    return render_template("dashboard.html", allTodo=allTodo, user=user)

@app.route("/update/<int:id>", methods=['GET', 'POST']) 
def Update(id):
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        todo = Todo.query.filter_by(id=id).first()  # Changed `sno` to `id`
        todo.title = title
        todo.description = description
        db.session.add(todo)
        db.session.commit()
        return redirect('/dashboard')

    todo = Todo.query.filter_by(id=id).first()  # Changed `sno` to `id`
    return render_template("update.html", todo=todo)
    
@app.route("/delete/<int:id>") 
def Delete(id):
    todo = Todo.query.filter_by(id=id).first()  # Changed `sno` to `id`
    db.session.delete(todo)
    db.session.commit()
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged-out Successfully!")
    return redirect("/")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
