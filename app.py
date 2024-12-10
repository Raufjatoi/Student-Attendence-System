from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Mock database (use a real database in production)
classes = []
students = []
attendance_records = []

# Route for homepage
@app.route('/')
def index():
    return render_template('classes.html', classes=classes)

# Route to add a new class
@app.route('/classes/add', methods=['GET', 'POST'])
def add_class():
    if request.method == 'POST':
        class_name = request.form['class_name']
        class_description = request.form['class_description']
        new_class = {
            'id': len(classes) + 1,
            'name': class_name,
            'description': class_description
        }
        classes.append(new_class)
        return redirect(url_for('index'))
    return render_template('add_class.html')

# Route to add students to a class
@app.route('/students/add/<int:class_id>', methods=['GET', 'POST'])
def add_student(class_id):
    if request.method == 'POST':
        student_name = request.form['student_name']
        student_id = request.form['student_id']
        new_student = {
            'id': student_id,
            'name': student_name,
            'class_id': class_id
        }
        students.append(new_student)
        return redirect(url_for('index'))
    # Find the class by ID
    class_name = next((cls['name'] for cls in classes if cls['id'] == class_id), '')
    return render_template('add_student.html', class_id=class_id, class_name=class_name)

# Route to mark attendance for a class
@app.route('/attendance/mark/<int:class_id>', methods=['GET', 'POST'])
def mark_attendance(class_id):
    if request.method == 'POST':
        for student in students:
            if student['class_id'] == class_id:
                status = request.form.get(f'attendance_status_{student["id"]}')
                attendance_record = {
                    'student_id': student['id'],
                    'student_name': student['name'],
                    'status': status,
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
                attendance_records.append(attendance_record)
        return redirect(url_for('view_attendance', class_id=class_id))

    # Get the students in the class
    class_students = [student for student in students if student['class_id'] == class_id]
    class_name = next((cls['name'] for cls in classes if cls['id'] == class_id), '')
    return render_template('mark_attendance.html', students=class_students, class_id=class_id, class_name=class_name)

# Route to view attendance for a class
@app.route('/attendance/view/<int:class_id>')
def view_attendance(class_id):
    # Get attendance records for the class
    class_name = next((cls['name'] for cls in classes if cls['id'] == class_id), '')
    records = [record for record in attendance_records if record['student_id'] in [student['id'] for student in students if student['class_id'] == class_id]]
    return render_template('view_attendance.html', attendance_records=records, class_name=class_name)

if __name__ == '__main__':
    app.run(debug=True)
