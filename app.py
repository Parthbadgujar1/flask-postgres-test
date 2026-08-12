import os

from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

# Railway provides DATABASE_URL
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is not set")

# Handle older Railway PostgreSQL URLs if necessary
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# -------------------------
# Database Model
# -------------------------

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    course = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Student {self.name}>"


# -------------------------
# Routes
# -------------------------

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        course = request.form.get("course")

        if not name or not email or not course:
            flash("Please fill all fields.", "danger")
            return redirect("/")

        student = Student(
            name=name,
            email=email,
            course=course
        )

        db.session.add(student)
        db.session.commit()

        flash("Student added successfully!", "success")

        return redirect("/")

    students = Student.query.order_by(Student.id.desc()).all()

    return render_template(
        "index.html",
        students=students
    )


# -------------------------
# Create Database Tables
# -------------------------

with app.app_context():
    db.create_all()


# -------------------------
# Run Application
# -------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )