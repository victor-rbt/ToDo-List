from app import app, db, login
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from app.models.tables import Tasks, Users
from app.models.forms import LoginForm, RegisterForm, AddTaskForm

import json
import bcrypt

@login.user_loader
def load_user(id):
    return Users.query.filter_by(id=id).first()

@app.route("/", methods=["GET", "POST"])
def login():
    title = 'Autenticação'

    form = LoginForm()
    if form.validate_on_submit():
        user_result = Users.query.filter_by(username=form.username.data).first()
        if user_result and bcrypt.checkpw(form.passwd.data.encode('utf-8'), user_result.passwd):
            login_user(user_result)
            return redirect(url_for('index'))
        else:
            flash("Credenciais inválidas!", "err")
            return redirect(url_for('login'))

    return render_template('login.html', title=title, form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()

    flash("Você saiu.", "err")
    return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    title = 'Cadastro'

    form = RegisterForm()
    if form.validate_on_submit():
        user_result = Users.query.filter_by(username=form.username.data).all()
        if user_result:
            flash("Usuário já existe na base de dados!" , "err")
            return redirect(url_for('register'))
        else:
            passwd_hashed = bcrypt.hashpw(form.passwd.data.encode('utf-8'), bcrypt.gensalt())
            ins_user = Users(form.name.data, form.surname.data, form.username.data, passwd_hashed)
            db.session.add(ins_user)
            db.session.commit()
            flash("Usuário criados!", "inf")
            return redirect(url_for('login'))

    return render_template('register.html', title=title, form=form)

@app.route("/index/<string:status>")
@app.route("/index")
@login_required
def index(status=None):
    title = 'Pagina Inicial'

    if status == 'concluidos':
        sql = Tasks.query.filter_by(users_id=current_user.id, status_id=1).all()
    elif status == 'deletados':
        sql = Tasks.query.filter_by(users_id=current_user.id, status_id=2).all()
    else:
        sql = Tasks.query.filter_by(users_id=current_user.id, status_id=0).all()

    return render_template('index.html', title=title, sql=sql)

@app.route("/add_task", methods=["GET", "POST"])
@login_required
def add_task():
    title = 'Criar Tarefa'

    form = AddTaskForm()
    if form.validate_on_submit():
        add_task_sql = Tasks(current_user.id, form.title.data, form.description.data, 0)
        db.session.add(add_task_sql)
        db.session.commit()
        flash("Tarefa adicionada!", "inf")
        return redirect(url_for('index'))

    return render_template('add_task.html', title=title, form=form)

@app.route("/details/<int:val_task>")
@login_required
def details(val_task):
    title = 'Detalhes Tarefa'

    validate_user = Tasks.query.filter_by(id=val_task).first()
    if validate_user.users_id == current_user.id:
        task_result = Tasks.query.filter_by(id=val_task).first()
    else:
        flash("Você não tem permissão para visualizar essa tarefa!", "err")
        return redirect(url_for(index))

    return render_template('details.html', title=title, task_result=task_result)

@app.route("/update_task/<int:id_task>")
def update_task(id_task):

    validate_user = Tasks.query.filter_by(id=id_task).first()
    if validate_user.users_id == current_user.id:
        sql = Tasks.query.filter_by(id=id_task).first()
        sql.status_id = 1
        db.session.commit()
    else: 
        flash("Você não tem permissão para alterar essa tarefa!", "err")
        return redirect(url_for('index'))

    flash("Tarefa atualizada!", "inf")
    return redirect(url_for('index'))

@app.route("/delete_task/<int:id_task>")
def delete_task(id_task):

    validate_user = Tasks.query.filter_by(id=id_task).first()
    if validate_user.users_id == current_user.id:
        sql = Tasks.query.filter_by(id=id_task).first()
        sql.status_id = 2
        db.session.commit()
    else: 
        flash("Você não tem permissão para alterar essa tarefa!", "err")
        return redirect(url_for('index'))

    flash("Tarefa deletada!", "inf")
    return redirect(url_for('index'))