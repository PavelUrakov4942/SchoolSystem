import os
from dotenv import load_dotenv, find_dotenv
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

app = Flask(__name__)
load_dotenv(find_dotenv())
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager(app)
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))
    login = db.Column(db.String(25), unique=True)
    passwordHash = db.Column(db.String(300))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Group(db.Model):
    __tablename__ = 'Group'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(8), unique=True)


class Student(db.Model, UserMixin):
    __tablename__ = 'Student'
    id_user = db.Column(db.Integer, db.ForeignKey('User.id'))
    id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(120))
    dateBirth = db.Column(db.Date)
    id_group = db.Column(db.Integer, db.ForeignKey('Group.id'))


class Teacher(db.Model, UserMixin):
    __tablename__ = 'Teacher'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('User.id'))
    fullName = db.Column(db.String(120))
    dateBirth = db.Column(db.Date)
    qualification = db.Column(db.String(50))


class Administrator(db.Model, UserMixin):
    __tablename__ = "Administrator"
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('User.id'))
    fullName = db.Column(db.String(120))


class TeacherGroup(db.Model):
    __tablename__ = 'TeacherGroup'
    id = db.Column(db.Integer, primary_key=True)
    id_group = db.Column(db.Integer, db.ForeignKey('Group.id'))
    id_teacher = db.Column(db.Integer, db.ForeignKey('Teacher.id'))


class Discipline(db.Model):
    __tablename__ = 'Discipline'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)


class TeacherDiscipline(db.Model):
    __tablename__ = 'TeacherDiscipline'
    id = db.Column(db.Integer, primary_key=True)
    id_teacher = db.Column(db.Integer, db.ForeignKey('Teacher.id'))
    id_discipline = db.Column(db.Integer, db.ForeignKey('Discipline.id'))


class LaboratoryWork(db.Model):
    __tablename__ = 'LaboratoryWork'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    name = db.Column(db.String(50), unique=True)
    id_discipline = db.Column(db.Integer, db.ForeignKey('Discipline.id'))


class WorkGroup(db.Model):
    __tablename__ = 'WorkGroup'
    id = db.Column(db.Integer, primary_key=True)
    deadline = db.Column(db.Date)
    id_LaboratoryWork = db.Column(db.Integer, db.ForeignKey('LaboratoryWork.id'))
    id_discipline = db.Column(db.Integer, db.ForeignKey('Discipline.id'))
    id_group = db.Column(db.Integer, db.ForeignKey('Group.id'))


class ResultLabWork(db.Model):
    __tablename__ = 'ResultLabWork'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20))
    grade = db.Column(db.Integer)
    id_LaboratoryWork = db.Column(db.Integer, db.ForeignKey('LaboratoryWork.id'))
    id_discipline = db.Column(db.Integer, db.ForeignKey('Discipline.id'))
    id_student = db.Column(db.Integer, db.ForeignKey('Student.id'))


class ControlWork(db.Model):
    __tablename__ = 'ControlWork'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    name = db.Column(db.String(50), unique=True)
    deadline = db.Column(db.Date)
    id_discipline = db.Column(db.Integer, db.ForeignKey('Discipline.id'))


class ResultControlWork(db.Model):
    __tablename__ = 'ResultControlWork'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20))
    grade = db.Column(db.Integer)
    id_controlWork = db.Column(db.Integer, db.ForeignKey('ControlWork.id'))
    id_discipline = db.Column(db.Integer, db.ForeignKey('Discipline.id'))
    id_student = db.Column(db.Integer, db.ForeignKey('Student.id'))


# Главная страница входа
@app.route("/", methods=("POST", "GET"))
@app.route("/login", methods=("POST", "GET"))
def login():
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
        user = User.query.filter_by(login=login).first()
        if user and check_password_hash(user.passwordHash, password):
            login_user(user)
            user_log = User.query.get(current_user.id)
            if user_log.role == "студент":
                return redirect("/profile_student")
            elif user_log.role == "преподаватель":
                return redirect("/profile_teacher")
            else:
                return redirect("/profile_admin")
        else:
            flash("Неверный логин или пароль")
    return render_template("login.html")


# Обработчик выхода
@app.route("/logout", methods=("GET", "POST"))
@login_required
def logout():
    logout_user()
    return redirect("/login")


# Страница регистрации студента
@app.route("/reg_student", methods=("POST", "GET"))
@login_required
def reg_student():
    if request.method == "POST":
        try:
            hash = generate_password_hash(request.form["password"])
            user = User(
                passwordHash=hash,
                login=request.form["login"],
                role="студент"
            )
            db.session.add(user)
            db.session.commit()
            print(1)
            newUser = User.query.order_by(User.id.desc()).first()
            id_user = newUser.id
            groupName = request.form["groupName"]
            idGroup = Group.query.filter_by(number=groupName).first()
            id_group = idGroup.id
            student = Student(
                fullName=request.form["fullName"],
                dateBirth=request.form["dateBirth"],
                id_group=id_group,
                id_user=id_user
            )
            print(2)
            db.session.add(student)
            db.session.commit()
            flash("Студент успешно добавлен", category="success")
        except:
            db.session.rollback()
            flash(
                "Возникла ошибка при добавлении записи в базу данных. Проверьте корректность введённых данных. Возможно, студент с таким логином уже зарегистрирован",
                category="error")
    stud_list = db.session.query(Student, Group, User) \
        .join(User, Student.id_user == User.id) \
        .join(Group, Student.id_group == Group.id).all()
    group_list = Group.query.all()
    return render_template("reg_student.html", stud_list=stud_list, group_list=group_list)


# Страница регистрации преподавателя
@app.route("/reg_teacher", methods=("POST", "GET"))
@login_required
def reg_teacher():
    if request.method == "POST":
        try:
            hash = generate_password_hash(request.form["password"])
            user = User(
                passwordHash=hash,
                login=request.form["login"],
                role="преподаватель"
            )
            db.session.add(user)
            db.session.commit()
            newUser = User.query.order_by(User.id.desc()).first()
            id_user = newUser.id
            teacher = Teacher(
                fullName=request.form["fullName"],
                dateBirth=request.form["dateBirth"],
                qualification=request.form["qualification"],
                id_user=id_user
            )
            db.session.add(teacher)
            db.session.commit()
            flash("Преподаватель успешно добавлен", category="success")
        except:
            db.session.rollback()
            flash(
                "Возникла ошибка при добавлении записи в базу данных. Проверьте корректность введённых данных. Возможно, преподаватель с таким логином уже зарегистрирован",
                category="error")
    teacher_list = db.session.query(Teacher, User) \
        .join(User, Teacher.id_user == User.id).all()
    return render_template("reg_teacher.html", teacher_list=teacher_list)


# Добавление учебного класса
@app.route("/add_group", methods=("POST", "GET"))
@login_required
def add_group():
    if request.method == "POST":
        try:
            group = Group(
                number=request.form["number"]
            )
            db.session.add(group)
            db.session.commit()
            flash("Класс успешно добавлен", category="success")
        except:
            db.session.rollback()
            flash(
                "Возникла ошибка при добавлении записи в базу данных. Проверьте корректность введённых данных. Возможно, такой класс уже создан",
                category="error")
    group_list = Group.query.all()
    return render_template("add_group.html", group_list=group_list)


# Добавление дисциплины
@app.route("/add_discipline", methods=("POST", "GET"))
@login_required
def add_discipline():
    if request.method == "POST":
        try:
            discipline = Discipline(
                name=request.form["name"]
            )
            db.session.add(discipline)
            db.session.commit()
            flash("Дисциплина успешно добавлена", category="success")
        except:
            db.session.rollback()
            flash(
                "Возникла ошибка при добавлении записи в базу данных. Проверьте корректность введённых данных. Возможно, дисциплина с таким названием уже существует",
                category="error")
    discipl_list = Discipline.query.all()
    return render_template("add_discipline.html", discipl_list=discipl_list)


# Преподаватель и дисциплина
@app.route("/teacher_discipline", methods=("POST", "GET"))
@login_required
def teacher_discipline():
    if request.method == "POST":
        try:
            teacherName = request.form["teacherName"]
            disciplineName = request.form["disciplineName"]
            teacher = Teacher.query.filter_by(fullName=teacherName).first()
            discipline = Discipline.query.filter_by(name=disciplineName).first()
            teacher_discipline = TeacherDiscipline(
                id_teacher=teacher.id,
                id_discipline=discipline.id
            )
            db.session.add(teacher_discipline)
            db.session.commit()
            flash("Запись успешно добавлена", category="success")
        except:
            db.session.rollback()
            flash("Возникла ошибка при добавлении записи в базу данных. Проверьте корректность введённых данных",
                  category="error")
    list = db.session.query(Teacher, TeacherDiscipline, Discipline) \
        .join(Teacher, TeacherDiscipline.id_teacher == Teacher.id) \
        .join(Discipline, TeacherDiscipline.id_discipline == Discipline.id) \
        .all()
    teach_list = Teacher.query.all()
    d_list = Discipline.query.all()
    return render_template("teacher_discipline.html", list=list, teach_list=teach_list, d_list=d_list)


# Преподаватель и группа
@app.route("/teacher_group", methods=("POST", "GET"))
@login_required
def teacher_group():
    if request.method == "POST":
        try:
            teacherName = request.form["teacherName"]
            groupName = request.form["groupName"]
            teacher = Teacher.query.filter_by(fullName=teacherName).first()
            group = Group.query.filter_by(number=groupName).first()
            teacher_group = TeacherGroup(
                id_teacher=teacher.id,
                id_group=group.id
            )
            db.session.add(teacher_group)
            db.session.commit()
            flash("Запись успешно добавлена", category="success")
        except:
            db.session.rollback()
            flash("Возникла ошибка при добавлении записи в базу данных. Проверьте корректность введённых данных",
                  category="error")
    list = db.session.query(Teacher, TeacherGroup, Group) \
        .join(Teacher, TeacherGroup.id_teacher == Teacher.id) \
        .join(Group, TeacherGroup.id_group == Group.id) \
        .all()
    teach_list = Teacher.query.all()
    group_list = Group.query.all()
    return render_template("teacher_group.html", list=list, teach_list=teach_list, group_list=group_list)


# Страница профиля студента
@app.route("/profile_student", methods=("POST", "GET"))
@login_required
def profile_student():
    stud = db.session.query(Student, Group) \
        .join(Group, Student.id_group == Group.id).all()
    result_lw_list = db.session.query(ResultLabWork, Student, Discipline, LaboratoryWork, WorkGroup) \
        .join(Student, ResultLabWork.id_student == Student.id) \
        .join(LaboratoryWork, ResultLabWork.id_LaboratoryWork == LaboratoryWork.id) \
        .join(WorkGroup, LaboratoryWork.id == WorkGroup.id_LaboratoryWork) \
        .join(Discipline, ResultLabWork.id_discipline == Discipline.id).all()
    result_cw_list = db.session.query(ResultControlWork, Student, Discipline, ControlWork) \
        .join(Student, ResultControlWork.id_student == Student.id) \
        .join(ControlWork, ResultControlWork.id_controlWork == ControlWork.id) \
        .join(Discipline, ResultControlWork.id_discipline == Discipline.id).all()
    return render_template("profile_student.html", stud=stud, result_lw_list=result_lw_list,
                           result_cw_list=result_cw_list)


# Страница профиля преподавателя
@app.route("/profile_teacher", methods=("POST", "GET"))
@login_required
def profile_teacher():
    inf = Teacher.query.filter_by(id_user=current_user.id).first()
    groups = db.session.query(Group, TeacherGroup) \
        .join(TeacherGroup, Group.id == TeacherGroup.id_group).all()
    discipline = db.session.query(Teacher, TeacherDiscipline, Discipline) \
        .join(Teacher, TeacherDiscipline.id_teacher == Teacher.id) \
        .join(Discipline, TeacherDiscipline.id_discipline == Discipline.id) \
        .all()
    return render_template("profile_teacher.html", inf=inf, groups=groups, discipline=discipline)


# Страница группы
@app.route("/group/<string:number>/<int:id_group>", methods=("POST", "GET"))
@login_required
def group(number, id_group):
    if request.method == "POST":
        try:
            work = request.form["name_LaboratoryWork"]
            seachwork = LaboratoryWork.query.filter_by(name=work).first()
            group_work = WorkGroup(
                deadline=request.form["deadline"],
                id_LaboratoryWork=seachwork.id,
                id_discipline=seachwork.id_discipline,
                id_group=id_group
            )
            db.session.add(group_work)
            db.session.commit()
            flash("Запись успешно добавлена", category="success")
        except:
            db.session.rollback()
            flash("Возникла ошибка при добавлении записи в базу данных. Проверьте корректность введённых данных",
                  category="error")

    lr_list = db.session.query(LaboratoryWork, WorkGroup, Discipline, TeacherDiscipline, Teacher) \
        .join(LaboratoryWork, WorkGroup.id_LaboratoryWork == LaboratoryWork.id) \
        .join(Discipline, WorkGroup.id_discipline == Discipline.id) \
        .join(TeacherDiscipline, Discipline.id == TeacherDiscipline.id_discipline) \
        .join(Teacher, TeacherDiscipline.id_teacher == Teacher.id).all()
    cr_list = db.session.query(ControlWork, Discipline, TeacherDiscipline, Teacher) \
        .join(Discipline, ControlWork.id_discipline == Discipline.id) \
        .join(TeacherDiscipline, Discipline.id == TeacherDiscipline.id_discipline) \
        .join(Teacher, TeacherDiscipline.id_teacher == Teacher.id).all()
    lw_list = db.session.query(LaboratoryWork, Discipline, TeacherDiscipline, Teacher) \
        .join(Discipline, LaboratoryWork.id_discipline == Discipline.id) \
        .join(TeacherDiscipline, Discipline.id == TeacherDiscipline.id_discipline) \
        .join(Teacher, TeacherDiscipline.id_teacher == Teacher.id).all()
    return render_template("group.html", number=number, id_group=id_group, lr_list=lr_list, cr_list=cr_list,
                           lw_list=lw_list)


# Добавление ЛР
@app.route("/add_lw", methods=("POST", "GET"))
@login_required
def add_lw():
    if request.method == "POST":
        try:
            discipline = request.form["disciplineName"]
            seachdiscipline = Discipline.query.filter_by(name=discipline).first()
            laboratory_work = LaboratoryWork(
                number=request.form["number"],
                name=request.form["name"],
                id_discipline=seachdiscipline.id
            )
            db.session.add(laboratory_work)
            db.session.commit()
            flash("Запись успешно добавлена", category="success")
        except:
            db.session.rollback()
            flash("Возникла ошибка при добавлении записи в базу данных. Проверьте корректность введённых данных",
                  category="error")
    lw_list = db.session.query(LaboratoryWork, Discipline, TeacherDiscipline, Teacher) \
        .join(Discipline, LaboratoryWork.id_discipline == Discipline.id) \
        .join(TeacherDiscipline, Discipline.id == TeacherDiscipline.id_discipline) \
        .join(Teacher, TeacherDiscipline.id_teacher == Teacher.id).all()
    d_list = db.session.query(Discipline, TeacherDiscipline, Teacher) \
        .join(TeacherDiscipline, Discipline.id == TeacherDiscipline.id_discipline) \
        .join(Teacher, TeacherDiscipline.id_teacher == Teacher.id).all()
    return render_template("add_lw.html", lw_list=lw_list, d_list=d_list)


# Добавление КР
@app.route("/add_cw", methods=("POST", "GET"))
@login_required
def add_cw():
    if request.method == "POST":
        try:
            discipline = request.form["disciplineName"]
            seachdiscipline = Discipline.query.filter_by(name=discipline).first()
            control_work = ControlWork(
                number=request.form["number"],
                name=request.form["name"],
                deadline=request.form["deadline"],
                id_discipline=seachdiscipline.id
            )
            db.session.add(control_work)
            db.session.commit()
            flash("Запись успешно добавлена", category="success")
        except:
            db.session.rollback()
            flash("Возникла ошибка при добавлении записи в базу данных. Проверьте корректность введённых данных",
                  category="error")
    cw_list = db.session.query(ControlWork, Discipline, TeacherDiscipline, Teacher) \
        .join(Discipline, ControlWork.id_discipline == Discipline.id) \
        .join(TeacherDiscipline, Discipline.id == TeacherDiscipline.id_discipline) \
        .join(Teacher, TeacherDiscipline.id_teacher == Teacher.id).all()
    d_list = db.session.query(Discipline, TeacherDiscipline, Teacher) \
        .join(TeacherDiscipline, Discipline.id == TeacherDiscipline.id_discipline) \
        .join(Teacher, TeacherDiscipline.id_teacher == Teacher.id).all()
    return render_template("add_cw.html", cw_list=cw_list, d_list=d_list)


# Добавление оценки за КР
@app.route("/result_cw/<int:id_group>/<int:id_controlWork>/<int:id_discipline>", methods=("POST", "GET"))
@login_required
def result_cw(id_group, id_controlWork, id_discipline):
    id_group = id_group
    id = id_controlWork
    stud_in_group = db.session.query(Student, Group) \
        .join(Group, Student.id_group == Group.id).all()
    if request.method == "POST":
        try:
            studentName = request.form["studentName"]
            for i in range(len(stud_in_group)):
                if stud_in_group[i].Student.fullName == studentName and stud_in_group[i].Student.id_group == id_group:
                    id_stud = stud_in_group[i].Student.id
                    break
            resultCW = ResultControlWork(
                status=request.form["status"],
                grade=request.form["grade"],
                id_discipline=id_discipline,
                id_controlWork=id,
                id_student=id_stud
            )
            db.session.add(resultCW)
            db.session.commit()
            flash("Запись успешно добавлена", category="success")
        except:
            db.session.rollback()
            flash("Возникла ошибка при добавлении записи в базу данных. Проверьте корректность введённых данных",
                  category="error")
    result_cw_list = db.session.query(ControlWork, Discipline, Student, ResultControlWork, TeacherDiscipline, Teacher) \
        .join(ControlWork, ResultControlWork.id_controlWork == ControlWork.id) \
        .join(Discipline, ResultControlWork.id_discipline == Discipline.id) \
        .join(TeacherDiscipline, Discipline.id == TeacherDiscipline.id_discipline) \
        .join(Teacher, TeacherDiscipline.id_teacher == Teacher.id) \
        .join(Student, ResultControlWork.id_student == Student.id).all()
    return render_template("result_cw.html", result_cw_list=result_cw_list, stud_in_group=stud_in_group,
                           id_group=id_group, id_controlWork=id_controlWork)


# Добавление оценки за ЛР
@app.route("/result_lw/<int:id_group>/<int:id_LaboratoryWork>/<int:id_discipline>", methods=("POST", "GET"))
@login_required
def result_lw(id_group, id_LaboratoryWork, id_discipline):
    id_group = id_group
    id = id_LaboratoryWork
    stud_in_group = db.session.query(Student, Group) \
        .join(Group, Student.id_group == Group.id).all()
    if request.method == "POST":
        try:
            studentName = request.form["studentName"]
            for i in range(len(stud_in_group)):
                if stud_in_group[i].Student.fullName == studentName and stud_in_group[i].Student.id_group == id_group:
                    id_stud = stud_in_group[i].Student.id
                    break
            resultLW = ResultLabWork(
                status=request.form["status"],
                grade=request.form["grade"],
                id_discipline=id_discipline,
                id_LaboratoryWork=id,
                id_student=id_stud
            )
            db.session.add(resultLW)
            db.session.commit()
            flash("Запись успешно добавлена", category="success")
        except:
            db.session.rollback()
            flash("Возникла ошибка при добавлении записи в базу данных. Проверьте корректность введённых данных",
                  category="error")
    result_lw_list = db.session.query(LaboratoryWork, Discipline, Student, ResultLabWork, TeacherDiscipline, Teacher) \
        .join(LaboratoryWork, ResultLabWork.id_LaboratoryWork == LaboratoryWork.id) \
        .join(Discipline, ResultLabWork.id_discipline == Discipline.id) \
        .join(TeacherDiscipline, Discipline.id == TeacherDiscipline.id_discipline) \
        .join(Teacher, TeacherDiscipline.id_teacher == Teacher.id) \
        .join(Student, ResultLabWork.id_student == Student.id).all()
    return render_template("result_lw.html", result_lw_list=result_lw_list, stud_in_group=stud_in_group,
                           id_group=id_group, id_LaboratoryWork=id_LaboratoryWork)


# Страница профиля админа
@app.route("/profile_admin", methods=("POST", "GET"))
@login_required
def profile_admin():
    inf = Administrator.query.get(current_user.id)
    return render_template("profile_admin.html", inf=inf)


if __name__ == "__main__":
    app.run()

# from app import db, Administrator, User
# from werkzeug.security import generate_password_hash, check_password_hash
# hash = generate_password_hash("password")
# user1 = User(role="администратор", login="admin", passwordHash=hash)
# db.session.add(user1)
# db.session.commit()
# admin1 = Administrator(fullName="AdminName", id_user=1)
# db.session.add(admin1)
# db.session.commit()
