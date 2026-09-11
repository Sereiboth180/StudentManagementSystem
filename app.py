from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Student Class Model
class Student:
    def __init__(self, id, name, age, mark, grade, course):
        self.id = id
        self.name = name
        self.age = age
        self.mark = mark
        self.grade = grade
        self.course = course

# In-memory student storage
student_list = []

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

# Home Route
@app.route("/")
def home():
    return render_template("index.html", students=student_list)

# Add Student Route
@app.route("/add", methods=["POST"])
def add_student():
    sid = request.form.get("id", "").strip()
    name = request.form.get("name", "").strip()
    age = request.form.get("age")
    mark = request.form.get("mark")
    course = request.form.get("course")

    if not mark or not sid or not name:
        return "Please fill out all required fields", 400

    # Duplicate Validation
    for s in student_list:
        if s.id.lower() == sid.lower():
            return f"Error: Student ID '{sid}' already exists", 400
        if s.name.lower() == name.lower():
            return f"Error: Student name '{name}' already exists", 400

    grade = calculate_grade(mark)
    new_student = Student(sid, name, age, mark, grade, course)
    student_list.append(new_student)

    return redirect(url_for("home"))

# Search Student Route
@app.route("/search", methods=["GET"])
def search_student():
    query = request.args.get("query", "").strip().lower()
    matching_student = []

    for s in student_list:
        if (
            query in s.name.lower()
            or query == s.grade.lower()
            or query in s.course.lower()
        ):
            matching_student.append(s)

    return render_template("index.html", students=matching_student, search_query=query)

# Delete Student Route
@app.route("/delete/<student_id>")
def delete_student(student_id):
    global student_list
    student_list = [s for s in student_list if s.id != student_id]
    return redirect(url_for("home"))

# Edit Student Page Route
@app.route("/edit/<student_id>")
def edit_student_page(student_id):
    selected_student = None
    for s in student_list:
        if s.id == student_id:
            selected_student = s
            break
    return render_template("edit.html", student=selected_student)

# Update Student Route
@app.route("/update/<student_id>", methods=["POST"])
def update_student_mark(student_id):
    new_name = request.form.get("name", "").strip()
    new_mark = request.form.get("mark")
    new_age = request.form.get("age")
    new_course = request.form.get("course")

    if not new_mark:
        return "Please enter a valid mark from 0-100", 400

    new_grade = calculate_grade(new_mark)

    for s in student_list:
        if s.id == student_id:
            s.name = new_name
            s.mark = new_mark
            s.age = new_age
            s.course = new_course
            s.grade = new_grade
            break

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
