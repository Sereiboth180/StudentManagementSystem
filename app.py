import csv
from io import StringIO
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

app = Flask(__name__)
# Secret key used to encrypt user login session
app.secret_key = 'super-secret-key-change-this'

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Student Class Model
class Student(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    mark = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(5), nullable=False)
    course = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

def calculate_grade(mark):
    mark = float(mark)
    if mark >= 80 and mark <= 100:
        return "A"
    elif mark >= 70:
        return "B"
    elif mark >= 60:
        return "C"
    else:
        return "F"

@app.route('/login', methods=['POST'])
def login():
    role = request.form.get('role', '').lower().strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if role == 'admin':
        if username.lower() == 'admin' and password == '1234':
            session['user_role'] = 'admin'
            session['user_id'] = 'admin'
            return redirect(url_for('home'))
        else:
            flash("Invalid Admin credentials.", "danger")
            return redirect(url_for('home'))

    elif role == 'student':
        if username.lower() == 'admin':
            flash("You selected 'Student' role. Please change the role dropdown to 'Admin' to log in.", "danger")
            return redirect(url_for('home'))
            
        if password:
            flash("Students do not need a password. Clear the password field and log in using only your Student ID.", "warning")
            return redirect(url_for('home'))

        student = Student.query.get(username)
        if student:
            session['user_role'] = 'student'
            session['user_id'] = student.id
            return redirect(url_for('home'))
        else:
            flash("Student ID not found.", "danger")
            return redirect(url_for('home'))

    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# Home Route
@app.route("/")
def home():
    role = session.get('user_role', None)
    user_id = session.get('user_id', None)
    
    if role == 'admin':
        query_parameter = request.args.get("query", "").strip()
        db_query = Student.query
        
        if query_parameter:
            search_pattern = f"%{query_parameter}%"
            db_query = db_query.filter(
                (Student.name.ilike(search_pattern)) |
                (Student.grade.ilike(query_parameter)) |
                (Student.course.ilike(search_pattern)) |
                (Student.id.ilike(search_pattern))
            )
            
        page = request.args.get('page', 1, type=int)
        pagination = db_query.paginate(page=page, per_page=10, error_out=False)
        students = pagination.items

        # Dashboard Statistics Calculation
        total_students = Student.query.count()
        
        # Calculate Average Mark
        avg_mark_query = db.session.query(func.avg(Student.mark)).scalar()
        avg_mark = round(avg_mark_query, 1) if avg_mark_query is not None else 0.0

        # Calculate Highest Grade
        highest_student = Student.query.order_by(Student.mark.desc()).first()
        highest_grade = highest_student.grade if highest_student else "N/A"

        # Calculate Distinct Courses Count
        total_courses = db.session.query(func.count(func.distinct(Student.course))).scalar() or 0

        return render_template(
            "index.html", 
            students=students, 
            role=role, 
            pagination=pagination,
            total_students=total_students,
            avg_mark=avg_mark,
            highest_grade=highest_grade,
            total_courses=total_courses
        )

    elif role == 'student':
        student = Student.query.get(user_id)
        return render_template("index.html", student=student, role=role)
        
    return render_template("index.html", role=None)

# Add Student Route
@app.route("/add", methods=["POST"])
def add_student():
    if session.get('user_role') != "admin":
        return "Only admin can add student!", 403
    sid = request.form.get("id", "").strip()
    name = request.form.get("name", "").strip()
    age = request.form.get("age")
    mark = request.form.get("mark")
    course = request.form.get("course")

    if not mark or not sid or not name:
        return "Please fill out all required fields", 400

    if Student.query.get(sid):
        return f"Student with {sid} already exists", 400
    elif Student.query.filter_by(name=name).first():
        return f"Student name {name} already exists", 400

    grade = calculate_grade(mark)
    new_student = Student(id=sid, name=name, age=int(age), mark=float(mark), grade=grade, course=course)

    db.session.add(new_student)
    db.session.commit()

    return redirect(url_for("home"))

# Export Students to CSV
@app.route("/export_csv")
def export_csv():
    if session.get('user_role') != "admin":
        return "Only admin can export data!", 403

    students = Student.query.all()
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(['ID', 'Name', 'Age', 'Mark', 'Grade', 'Course'])

    for s in students:
        writer.writerow([s.id, s.name, s.age, s.mark, s.grade, s.course])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=students.csv"}
    )

# Import Students from CSV
@app.route("/import_csv", methods=["POST"])
def import_csv():
    if session.get('user_role') != "admin":
        return "Only admin can import data!", 403

    file = request.files.get("file")
    if not file or not file.filename.endswith(".csv"):
        return "Please upload a valid CSV file", 400

    stream = StringIO(file.stream.read().decode("UTF-8"), newline=None)
    csv_reader = csv.DictReader(stream)

    for row in csv_reader:
        sid = row.get("ID", "").strip()
        name = row.get("Name", "").strip()
        age = row.get("Age")
        mark = row.get("Mark")
        course = row.get("Course", "").strip()

        if sid and name and mark and age:
            if not Student.query.get(sid):
                grade = calculate_grade(mark)
                new_student = Student(
                    id=sid,
                    name=name,
                    age=int(age),
                    mark=float(mark),
                    grade=grade,
                    course=course
                )
                db.session.add(new_student)

    db.session.commit()
    return redirect(url_for("home"))

# Delete Student Route
@app.route("/delete/<student_id>")
def delete_student(student_id):
    if session.get('user_role') != "admin":
        return "Only admin can access", 403
    student = Student.query.get_or_404(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()

    return redirect(url_for("home"))

# Edit Student Page Route
@app.route("/edit/<student_id>")
def edit_student_page(student_id):
    if session.get('user_role') != 'admin':
        return "Only admin can access", 403

    student = Student.query.get_or_404(student_id)
    return render_template("edit.html", student=student)

@app.route("/update/<student_id>", methods=["POST"])
def update_student(student_id):
    if session.get('user_role') != "admin":
        return "Only admin can access", 403
    student = Student.query.get_or_404(student_id)
    student.name = request.form.get("name", "").strip()
    student.age = int(request.form.get("age"))
    student.course = request.form.get("course", "").strip()

    new_mark = float(request.form.get("mark"))
    student.mark = new_mark
    student.grade = calculate_grade(new_mark)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
