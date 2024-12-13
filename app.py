from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    students = db.relationship('Student', backref='class_', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)  # Add roll_no
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)

# Routes
@app.route('/')
def index():
    classes = Class.query.order_by(Class.name).all()
    return render_template('classes.html', classes=classes)

@app.route('/classes/add', methods=['GET', 'POST'])
def add_class():
    if request.method == 'POST':
        class_name = request.form['class_name']
        class_description = request.form.get('class_description')
        if not class_name.strip():
            flash('Class name cannot be empty!', 'danger')
            return redirect(url_for('add_class'))
        new_class = Class(name=class_name, description=class_description)
        db.session.add(new_class)
        db.session.commit()
        flash('Class added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_class.html')

@app.route('/students/add/<int:class_id>', methods=['GET', 'POST'])
def add_student(class_id):
    class_ = Class.query.get_or_404(class_id)
    if request.method == 'POST':
        student_name = request.form['student_name']
        roll_no = request.form['roll_no']
        if not student_name.strip():
            flash('Student name cannot be empty!', 'danger')
            return redirect(url_for('add_student', class_id=class_id))
        if not roll_no.strip():
            flash('Roll No cannot be empty!', 'danger')
            return redirect(url_for('add_student', class_id=class_id))
        new_student = Student(name=student_name, roll_no=roll_no, class_id=class_id)
        db.session.add(new_student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_student.html', class_=class_)

@app.route('/attendance/mark/<int:class_id>', methods=['GET', 'POST'])
def mark_attendance(class_id):
    class_ = Class.query.get_or_404(class_id)
    students = class_.students
    if request.method == 'POST':
        date = datetime.strptime(request.form.get('attendance_date'), '%Y-%m-%d')
        for student in students:
            status = request.form.get(f'attendance_status_{student.id}', 'Absent')
            new_record = Attendance(student_id=student.id, status=status, date=date)
            db.session.add(new_record)
        db.session.commit()
        flash('Attendance marked successfully!', 'success')
        return redirect(url_for('view_attendance', class_id=class_id))
    
    # Pass datetime to the template
    return render_template('mark_attendance.html', class_=class_, students=students, datetime=datetime)
@app.route('/attendance/view/<int:class_id>')
def view_attendance(class_id):
    class_ = Class.query.get_or_404(class_id)
    # Get all attendance records for the class ordered by date
    attendance_records = db.session.query(Attendance, Student).join(Student).filter(Student.class_id == class_id).order_by(Attendance.date.desc()).all()
    return render_template('view_attendance.html', class_=class_, attendance_records=attendance_records)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables before running the app
    app.run(debug=True)
