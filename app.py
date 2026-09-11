from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Force WhiteNoise to serve static files on Vercel



#let create student class

class Student:
    def __init__(self, student_id, name, age,mark, grade, course):
        self.student_id = student_id
        self.name = name 
        self.age = age
        self.mark = mark
        self.grade = grade
        self.course = course

#i create this student list to store student in the system
student_list = []

def calculate_grade(mark):
    mark = float(mark)
    if mark>=80:
        return "A"
    elif mark >= 70:
        return "B"
    elif mark >= 60:
        return "C"
    else:
        return "F"
    
#i use app route to let python inside Flask
@app.route("/")
def home():# this home is home page
    return render_template("index.html", student_list= student_list)

@app.route("/add",methods = ["POST"])
def add_student():
    sid = request.form.get("student_id")
    name = request.form.get("name")
    age = request.form.get("age")
    mark = request.form.get("mark")
    
    course = request.form.get("course")

    
    if mark is None or mark == "":
        return "Please enter a valid mark from 0-100"
    
    #i create a new student object and add it to student list above
    grade = calculate_grade(mark)
    new_student = Student(sid, name, age,mark,grade, course)
    student_list.append(new_student)

    #here i use redirect to update what user want to see on the screen
    return redirect(url_for("home"))

#search for student by their id or name
@app.route("/search", methods=["GET"])
def search_student():
    query = request.args.get("query", "").strip().lower() #i use request.args.get to grab the data type to search box
    # i use for loop to check the person one by one inside the list
    matching_student = []
    for s in student_list:
        if query in s.name.lower() or query == s.grade.lower():
            matching_student.append(s)
    return render_template("index.html", student_list = matching_student, search_query = query)
@app.route("/delete/<student_id>")
def delete_student(student_id):
    global student_list
    student_list= [s for s in student_list if s.student_id != student_id]
    return redirect(url_for("home"))
#now i want to edit student page
@app.route("/edit/<student_id>")
def edit_student_page(student_id):
    selected_student = None
    for s in student_list:
        if s.student_id == student_id:
            selected_student = s
            break
    return render_template("edit.html", student = selected_student)
# i want to update student mark , so first i need student id to go through that student then update his or her mark
@app.route("/update/<student_id>", methods = ["POST"])
def update_student_mark(student_id):
    new_name = request.form.get("name")
    new_mark = request.form.get("mark")
    new_age = request.form.get("age")
    new_course = request.form.get("course")
    new_grade = calculate_grade(new_mark)
    for s in student_list:
        if s.student_id == student_id:
            s.name = new_name
            s.mark = new_mark
            s.age = new_age
            s.course = new_course
            s.grade = new_grade
            break
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)











